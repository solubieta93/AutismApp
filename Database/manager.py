import sqlite3
from os.path import exists as file_exists, abspath, dirname
from os.path import join as path_join
from sys import stderr, stdout
from operators import *
import collections

base_path = abspath(dirname(__file__))


class Manager:
    def __init__(self, db_name='database.db'):
        self.db_file_path = path_join(base_path, db_name)
        self.db_name = db_name

    def create_db(self, table_name, column_types, references=[], unique=False):
        # create or truncate the db file
        if not file_exists(self.db_file_path):
            try:
                db = open(self.db_file_path, 'w')
                db.close()
            except:
                stderr.write('ERROR: Failed to create "%s" file\n' % self.db_file_path)
                return False
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()
            try:
                table_column_types = ', '.join(('{0:s} {1:s}'.format(col_name, Manager.__get_type(column_types[col_name]))
                               for col_name in column_types.keys()))

                table_references = ', '.join(('{0:s}_id INTEGER REFERENCES {0:s}(id)'.format(table) for table in references))
                # ON DELETE CASCADE
                tail = ', '.join((table_references, table_column_types)) if references else table_column_types

                create_table_users_query = u'CREATE TABLE IF NOT EXISTS {0:s} (id INTEGER PRIMARY KEY, {1:s})'.format(
                    table_name, tail)

                # Create table images
                c.execute(create_table_users_query)

                if unique:
                    c.execute(
                        u'CREATE UNIQUE INDEX images_index ON images({0:s})'.format(', '.join(column_types.keys())))

            except:
                stderr.write('ERROR: Failed to create DB \'{}\'\n'.format(self.db_name))
                return False
            else:
                stdout.write('DB \'{}\' successfully created!\n'.format(self.db_name))
                return True

    # data_references = {'table':table_name, 'column':column, 'value':value}
    def insert(self, table_name, data, data_references=None):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

            if data_references:

                column_value = repr(data_references['column_value']) if type(data_references['column_value']) \
                                                                       in (str, unicode) else str(data_references['column_value'])
                query = u'SELECT id FROM {} WHERE ({}) LIMIT 1'.format(
                    data_references['table'],
                    u'{}={}'.format(data_references['column_name'], column_value))

                print 'query1-->' + query
                rows = c.execute(query)

                try:
                    row_id = rows.next()[0]
                except Exception as e:
                    stderr.write(e.message)
                    return False, e.message

        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

            query = u'INSERT INTO {} ({}{}) VALUES ({}{})'.format(
                table_name,
                u'{}_id, '.format(data_references['table']) if data_references else u'',
                u', '.join(data.keys()),
                u'{}, '.format(row_id) if data_references else u'',
                u', '.join(Manager.__get_value(data[col], Manager.__get_type(self.__TABLES[table_name][col])) for col in data.keys()))
            print 'query2-->' + query
            try:
                #row
                c.execute(query)

                # commit changes
                conn.commit()

            except Exception as e:
                stderr.write(e.message)
                return False, e.message
            else:
                stdout.write('DB \'{}\' successfully created!\n'.format(self.db_name))
                return True, 'successfully created!'

    def insert_b(self, reference_table, table_name, data, row_id):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

            query = u'INSERT INTO {} ({}{}) VALUES ({}{})'.format(
                table_name,
                u'{}_id, '.format(reference_table),
                u', '.join(data.keys()),
                u'{}, '.format(row_id),
                u', '.join(Manager.__get_value(data[col], Manager.__get_type(self.__TABLES[table_name][col])) for col in data.keys()))

            try:
                #row
                c.execute(query)

                # commit changes
                conn.commit()

            except Exception as e:
                stderr.write(e.message)
                return False, e.message
            else:
                stdout.write('DB \'{}\' successfully created!\n'.format(self.db_name))
                return True, 'Successfully created!'

    def _run_query(self, query):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()
            try:
                return c.execute(query)
            except Exception as e:
                stderr.write(e.message)
                print 'except'
                return None

    def _get_row(self, row, columns, column_names):
        # return row[columns['id']], dict((col, row[columns[col]]) for col in column_names)
        return dict((col, row[columns[col]]) for col in column_names)

    def login_user(self, user, password):
        query = 'SELECT username, password FROM user WHERE ({})'.format((COL('username') == user).to_sql())
        users = self._run_query(query)
        # users = tuple(users)
        users_cols = dict((name[0], index) for index, name in enumerate(users.description))
        users = tuple(users)
        if not len(users) == 1:
            return False, 'user not valid'

        row = users[0]
        user_data = self._get_row(row, users_cols, self.__TABLES['user'].keys())
        if not user_data['password'] == password:
            return False, 'Wrong password'
        return True, 'logged successfully'

    def register_user(self, user, password):
        query = 'SELECT username, password FROM user WHERE ({})'.format((COL('username') == user).to_sql())
        users = self._run_query(query)
        # users = tuple(users)
        users_cols = dict((name[0], index) for index, name in enumerate(users.description))
        users = tuple(users)
        if len(users) == 1:
            return False, 'user existed'

        result = self.insert('user', data={'username': user, 'password': password})
        return result[0], 'registed successfully' if result[0] else result[1]

    # region Delete
    # TODO: aqui hay q hacer eliminacion de todo el q tenga referencia, arreglar ON DELETE CASCADE
    def delete_table(self, table_name, medicaid_id, name_in_combo_box=''):
        print medicaid_id
        kid_id = self.id_kid(medicaid_id)

        print 'k' + str(kid_id)
        list_id = []

        if table_name is 'kids':
            need_column = 'id'
            query = u'DELETE FROM {} WHERE {}'.format(
                table_name,
                (COL(need_column) == kid_id).to_sql()
            )

            self._run_query(query)

            return self.delete_rest_table(kid_id)

        elif name_in_combo_box is not '':

            need_column = 'kids_id'

            query1 = u'SELECT id FROM {} WHERE ({} AND {})'.format(
                table_name,
                (COL(need_column) == kid_id).to_sql(),
                (COL('name') == name_in_combo_box).to_sql()
            )
            row_id_table = self._run_query(query1)

            for item in tuple(row_id_table):
                list_id.append(item[0])

            if list_id:
                column_need = u'{}_id'.format(table_name)
                list_tables = [u'baseline_{}'.format(table_name), u'lto_{}'.format(table_name),
                               u'sto_{}'.format(table_name), u'data_{}'.format(table_name)]
                for i in list_id:
                    for table in list_tables:
                        query = u'DELETE FROM {} WHERE {}'.format(
                            table,
                            (COL(column_need) == i).to_sql()
                        )
                        self._run_query(query)

            query = u'DELETE FROM {} WHERE ({} AND {})'.format(
                table_name,
                (COL(need_column) == kid_id).to_sql(),
                (COL('name') == name_in_combo_box).to_sql()
            )

            return self._run_query(query)

    def delete_rest_table(self, kid_id):
        tables = ['behaviors', 'programs']

        list_id = []
        for table_name in tables:
            need_column = 'kids_id'

            query1 = u'SELECT id FROM {} WHERE {}'.format(
                table_name,
                (COL('kids_id') == kid_id).to_sql()
            )
            print query1
            row_id_table = self._run_query(query1)
            print row_id_table

            if row_id_table is not None:
                for item in tuple(row_id_table):
                    list_id.append(item[0])

                if list_id:
                    column_need = u'{}_id'.format(table_name)
                    list_tables = [u'baseline_{}'.format(table_name), u'lto_{}'.format(table_name),
                                   u'sto_{}'.format(table_name), u'data_{}'.format(table_name)]
                    for i in list_id:
                        for table in list_tables:
                            query = u'DELETE FROM {} WHERE {}'.format(
                                table,
                                (COL(column_need) == i).to_sql()
                            )
                            self._run_query(query)

                query = u'DELETE FROM {} WHERE {}'.format(
                    table_name,
                    (COL(need_column) == kid_id).to_sql()
                )
                return self._run_query(query)

    def delete_table_part(self, table_name, medicaid_id, name_in_combo_box, name_part):

        if table_name.endswith('behaviors'):
            need_name = 'behaviors'
            need_id = u'{}_id'.format(need_name)
        elif table_name.endswith('programs'):
            need_name = 'programs'
            need_id = u'{}_id'.format(need_name)

        b, _, table_id = self.id_table(need_name, medicaid_id, name_in_combo_box)

        if b:
            print 'table_id--> ' + str(table_id)
            query = u'DELETE FROM {} WHERE ({} AND {})'.format(
                table_name,
                (COL('date') == str(name_part)).to_sql(),
                (COL(need_id) == table_id).to_sql()
            )

            print 'query --> ' + query

            return self._run_query(query)

    # endregion

    # region Add Methods
    def add_kid(self, username, kid_name, last_name, kid_age, medicaid_id, analyst):
        result = self.insert('kids', {'kid_name': kid_name, 'last_name': last_name, 'kid_age': kid_age, 'medicaidID': medicaid_id,
                                      'analyst': analyst}, data_references={'table': 'user',
                                                                            'column_name': 'username',
                                                                            'column_value': username})
        if result[0]:
            return result[0], 'Successful insertion'
        else:
            return result

    def add_baseline(self, reference_table, medicaid_id, name, bl_count_time, bl_time, bl_begin_date,
                     bl_end_date, exist_bl_end_date):
        b, s, row_id = self.id_table(reference_table, medicaid_id, name)

        if row_id is None:
            return b, s

        table_name = u'baseline_{}'.format(reference_table)
        int_bool = int(exist_bl_end_date)
        result = self.insert_b(reference_table, table_name, {'bl_count_time': bl_count_time, 'bl_time': bl_time,
                                                             'bl_begin_date': bl_begin_date,
                                                             'bl_end_date': bl_end_date, 'exist_bl_end_date': int_bool},
                               row_id)
        if result[0]:
            return result[0], 'Successful insertion'
        else:
            return result

    def add_lto(self, reference_table, medicaid_id, name, lto_count, lto_time_count, lto_time):
        b, s, row_id = self.id_table(reference_table, medicaid_id, name)

        if row_id is None:
            return b, s

        table_name = u'lto_{}'.format(reference_table)
        result = self.insert_b(reference_table, table_name, {'lto_count': lto_count, 'lto_time_count': lto_time_count,
                                                             'lto_time': lto_time, 'mastered': 0}, row_id)
        if result[0]:
            return result[0], 'Successful insertion'
        else:
            return result

    def add(self, table_name, kid_medicaid_id, name, measure):
        result = self.insert(table_name, {'name': name, 'measure': measure}, data_references={'table': 'kids',
                                                                                               'column_name':
                                                                                                   'medicaidID',
                                                                                               'column_value':
                                                                                                   kid_medicaid_id})

        return result[0], 'Successful insertion'

    def add_maladaptive_behavior(self, kid_medicaid_id, name, measure):
        result = self.insert('behaviors', {'name': name, 'measure': measure}, data_references={'table': 'kids',
                                                                                               'column_name':
                                                                                                   'medicaidID',
                                                                                               'column_value':
                                                                                                   kid_medicaid_id})
        return result[0], 'Successful insertion'

    def add_program(self, kid_medicaid_id, name, measure):
        result = self.insert('programs', {'name': name, 'measure': measure}, data_references={'table': 'kids',
                                                                                              'column_name':
                                                                                                  'medicaidID',
                                                                                              'column_value':
                                                                                                  kid_medicaid_id})
        return result[0], 'Successful insertion'

    def add_sto(self, table_reference, medicaid_id, name_in_line_edit, sto_count_min, sto_count_max, sto_time_count,
                sto_time, string_rep_params=''):
        b, s, row_id = self.id_table(table_reference, medicaid_id, name_in_line_edit)

        print 'estoy en add sto con table-> ' + table_reference

        if row_id is None:
            return b, s

        list_sto_string = self.sto_data_string(table_reference, medicaid_id, name_in_line_edit)[2]
        count_sto_number = len(list_sto_string)
        count_sto_string = 'STO ' + str(count_sto_number + 1) + '--'

        if string_rep_params is not '':
            string_rep = string_rep_params
        else:
            if table_reference == 'programs' and sto_count_max is -1:
                string_rep = count_sto_string + ' No less than ' + str(sto_count_min) + \
                                 ' incidents per week for ' + str(sto_time_count) + \
                                 ' consecutive ' + str(sto_time)
            elif table_reference == 'behaviors' and sto_count_min is -1:
                string_rep = count_sto_string + ' No more than ' + str(sto_count_max) + ' incidents per week for ' \
                             + str(sto_time_count) + ' consecutive ' + str(sto_time)
            else:
                string_rep = count_sto_string + ' Between ' + str(sto_count_min) + ' and ' + str(sto_count_max) + ' incidents per week for ' \
                             + str(sto_time_count) + ' consecutive ' + str(sto_time)

        table_name = u'sto_{}'.format(table_reference)
        result = self.insert_b(table_reference, table_name,
                               {'sto_count_min': sto_count_min, 'sto_count_max': sto_count_max,
                                'sto_time_count': sto_time_count, 'sto_time': sto_time, 'string_rep': string_rep,
                                'mastered': 0},
                               row_id)

        if result[0]:
            return result[0], 'Successful insertion'
        else:
            return result

    def add_data_kid(self, table_reference, medicaid_id, name_in_line_edit, date, value, comments=''):
            b, s, row_id = self.id_table(table_reference, medicaid_id, name_in_line_edit)

            if row_id is None:
                return b, s

            table_name = u'data_{}'.format(table_reference)

            result = self.insert_b(table_reference, table_name, {'date': date, 'value': value, 'comment': comments},
                                   row_id)

            if result[0]:
                return result[0], 'Successful insertion'
            else:
                return result

    # endregion

    # region Get IDs
    def id_user(self, username):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

        query = u'SELECT id FROM user WHERE ({}) LIMIT 1'.format((COL('username') == username).to_sql())

        rows = c.execute(query)

        try:
            row_id = rows.next()[0]
        except StopIteration:
            row_id = None

        return row_id

    def id_table(self, table_name, medicaid_id, name):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

        query = u'SELECT id FROM kids WHERE ({}) LIMIT 1'.format(
            (COL('medicaidID') == medicaid_id).to_sql())

        rows = c.execute(query)

        try:
            row_id = rows.next()[0]
        except StopIteration:
            row_id = None

        if row_id is None:
            return False, 'Kids_id not found', row_id

        query = u'SELECT id FROM {} WHERE ({} AND {}) LIMIT 1'.format(
            table_name,
            (COL('name') == str(name)).to_sql(),
            (COL('kids_id') == row_id).to_sql())

        print 'id_table'
        print query

        rows2 = c.execute(query)
        try:
            row_id = rows2.next()[0]
        except StopIteration:
            row_id = None

        if row_id is None:
            return False, u'Table_{}_id not found'.format(name), row_id

        return True, '', row_id

    def id_kid(self, medicaid_id):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

        query = u'SELECT id FROM kids WHERE ({}) LIMIT 1'.format((COL('medicaidID') == medicaid_id).to_sql())

        rows = c.execute(query)

        try:
            row_id = rows.next()[0]
        except StopIteration:
            row_id = None
        return row_id
    # endregion

    # region Get List
    def list_usernames(self):
        query = 'SELECT username FROM user'
        users = self._run_query(query)
        return [item[0] for item in tuple(users)]

    def list_kids(self, username):

        row_id = self.id_user(username)

        if row_id is None:
            return False, 'user not found'

        query = u'SELECT kid_name, last_name, medicaidID FROM kids WHERE ({})'.format(
            (COL('user_id') == row_id).to_sql())
        print 'query in list_kids ' + query
        kids_names = self._run_query(query)

        kidsnames = [str(kids[2]) + '-->' + kids[0] + ' ' + kids[1] for kids in tuple(kids_names)]
        # print kidsnames
        return kidsnames

    def list_medicaid_kid(self, username):
        row_id = self.id_user(username)

        if row_id is None:
            return False, 'user not found'

        query = u'SELECT medicaidID FROM kids WHERE ({})'.format((COL('user_id') == row_id).to_sql())

        kids_names = self._run_query(query)
        return [kids[0] for kids in tuple(kids_names)]

    def list_behavior_or_program(self, table_name, medicaid_id):
        row_id = self.id_kid(medicaid_id)

        if row_id is None:
            return []

        query = u'SELECT name FROM {} WHERE ({})'.format(
            table_name,
            (COL('kids_id') == row_id).to_sql())
        # print 'query-->' + query

        behaviors_names = self._run_query(query)

        result = [item[0] for item in tuple(behaviors_names)]

        return result

    def list_maladaptive_behavior(self, medicaid_id):
        row_id = self.id_kid(medicaid_id)

        if row_id is None:
            return []

        query = u'SELECT name FROM behaviors WHERE ({})'.format((COL('kids_id') == row_id).to_sql())

        behaviors_names = self._run_query(query)
        result = [behaviors[0] for behaviors in tuple(behaviors_names)]
        return result

    def list_programs(self, medicaid_id):
        row_id = self.id_kid(medicaid_id)

        if row_id is None:
            return []

        query = u'SELECT name FROM programs WHERE ({})'.format((COL('kids_id') == row_id).to_sql())

        programs_names = self._run_query(query)
        result = [programs[0] for programs in tuple(programs_names)]
        return result

    def list_baseline(self, table_reference, medicaid_id, name_in_combo_box):
        b, s, row_id = self.id_table(table_reference, medicaid_id, name_in_combo_box)

        if row_id is None:
            return b, s

        table = u'baseline_{}'.format(table_reference)
        col = u'{}_id'.format(table_reference)
        query = u'SELECT bl_count_time, bl_time, bl_begin_date, bl_end_date, exist_bl_end_date FROM {} WHERE {}'.format(
            table,
            (COL(col) == row_id).to_sql()
        )

        results = self._run_query(query)
        data = []
        for item in tuple(results):
            data.append(item[0])
            data.append(item[1])
            data.append(item[2])
            data.append(item[3])
            data.append(item[4])

        return data

    def list_dates(self, table_reference, medicaid_id, name_in_combo_box):
        # print 'estoy en list dates'
        b, s, row_id = self.id_table(table_reference, medicaid_id, name_in_combo_box)

        if row_id is None:
            return b, s

        table = u'data_{}'.format(table_reference)
        col = u'{}_id'.format(table_reference)
        query = u'SELECT date, value, comment FROM {} WHERE {}'.format(
            table,
            (COL(col) == row_id).to_sql()
        )
        # print query
        results = self._run_query(query)

        dict_dates_values = collections.OrderedDict()

        exist = False

        # dict[date] = (value, comment)
        for item in tuple(results):
            dict_dates_values[item[0]] = (item[1], item[2])
            exist = True

        import operator
        res = sorted(dict_dates_values.items(), key=operator.itemgetter(0))
        dict_dates_values = collections.OrderedDict()
        for item in res:
            # print 'item'
            # print item
            dict_dates_values[item[0]] = item[1]
        # print res
        # print dict_dates_values
        return exist, dict_dates_values
    # endregion

    # region Get Data
    def kid_data(self, medicaid_id):
        query = u'SELECT kid_name, last_name, kid_age, analyst FROM kids WHERE ({})'.format(
            (COL('medicaidID') == medicaid_id).to_sql())

        kid_datas = self._run_query(query)
        for kids in tuple(kid_datas):
            return True, 'child already exist', [kids[0], kids[1], kids[2], kids[3]]
        return False, 'not exist', []

    def table_all_data(self, table, medicaid_id, name):
        row_id = self.id_kid(medicaid_id)

        if row_id is None:
            return False, 'ID kid not found', []

        query = u'SELECT id, measure FROM {} WHERE ({} AND {})'.format(
            table,
            (COL('kids_id') == row_id).to_sql(),
            (COL('name') == name).to_sql())

        # print 'query-->' + query

        table_data = self._run_query(query)
        if table_data is None:
            return False, 'Behavior not found', []
        data = {}

        for item in tuple(table_data):
            data['measure'] = item[1]
            table_id = item[0]

        from_column_name = u'baseline_{}'.format(table)
        where_column_name = u'{}_id'.format(table)
        query = u'SELECT bl_count_time, bl_time, bl_begin_date, bl_end_date, exist_bl_end_date FROM {} WHERE ({})'.format(
            from_column_name,
            (COL(where_column_name) == table_id).to_sql())

        # print 'query2-->' + query

        table_data = self._run_query(query)
        if table_data is None:
            return False, 'Table`s baseline not found', []

        for item in tuple(table_data):
            data['bl_count_time'] = item[0]
            data['bl_time'] = item[1]
            data['bl_begin_date'] = item[2]
            data['bl_end_date'] = item[3]
            data['exist_bl_end_date'] = item[4]

            # print item[0]
            # print item[1]
            # print item[2]
            # print item[3]
            # print item[4]

        from_column_name = u'lto_{}'.format(table)
        query = u'SELECT lto_count, lto_time_count, lto_time FROM {} WHERE ({})'.format(
            from_column_name,
            (COL(where_column_name) == table_id).to_sql())

        table_data = self._run_query(query)
        if table_data is None:
            return False, 'Table`s LTO not found', []

        for item in tuple(table_data):
            data['lto_count'] = item[0]
            data['lto_time_count'] = item[1]
            data['lto_time'] = item[2]

        from_column_name = u'sto_{}'.format(table)
        query = u'SELECT sto_count_min, sto_count_max, sto_time_count, sto_time FROM {} WHERE ({})'.format(
            from_column_name,
            (COL(where_column_name) == table_id).to_sql())

        table_data = self._run_query(query)

        if table_data is None:
            return False, 'Table`s STO not found', []

        exist = False
        for item in tuple(table_data):
            data['sto_count_min'] = item[0]
            data['sto_count_max'] = item[1]
            data['sto_time_count'] = item[2]
            data['sto_time'] = item[3]
            exist = True

        if not exist:
            return True, 'No exist STO', data

        return True, '', data

    # TODO: VER Q FUNCIONA LA MODIF
    def sto_data_string(self, table_reference, medicaid_id, name_value):
        b, s, id_table = self.id_table(table_reference, medicaid_id, name_value)

        if id_table is None:
            return b, s, []

        need_id = u'{}_id'.format(table_reference)

        query = u'SELECT string_rep, mastered, date_mastered, id FROM {} WHERE ({})'.format(
            u'sto_{}'.format(table_reference),
            (COL(need_id) == id_table).to_sql())

        sto_names = self._run_query(query)

        if sto_names is None:
            return False, 'STO not found', []

        result = []
        for sto in tuple(sto_names):
            # print 'sto ->' + str(sto)
            if sto[1]:
                string_result = str(sto[0]) + '(MASTERED ' + str(sto[2]) + ').'
                add_tuple = (sto[1], str(sto[2]), sto[3], string_result)
                # result.append((sto[3],  string_result))
            else:
                add_tuple = (sto[1], str(sto[2]), sto[3], str(sto[0]))
            result.append(add_tuple)

        if not result:
            return False, 'STO not found', []

        return True, '', result

    def sto_data(self, table_reference, medicaid_id, name_value_table, string_rep_value):
        b, s, id_table = self.id_table(table_reference, medicaid_id, name_value_table)

        if id_table is None:
            return b, s, []

        need_id = u'{}_id'.format(table_reference)

        query = u'SELECT sto_count_min, sto_count_max, sto_time_count, sto_time FROM {} WHERE ({} AND {})'.format(
            u'sto_{}'.format(table_reference),
            (COL(need_id) == id_table).to_sql(),
            (COL('string_rep') == string_rep_value).to_sql())

        # print 'query in sto data-> ' + query
        sto_data = self._run_query(query)

        # print sto_data
        if sto_data is None:
            return False, 'STO not found', []

        data = []
        for sto in tuple(sto_data):
            data.append(sto[0])
            data.append(sto[1])
            data.append(sto[2])
            data.append(sto[3])

        return True, '', data

    def sto_data_without_string(self, table_reference, medicaid_id, name_value_table):
        b, s, id_table = self.id_table(table_reference, medicaid_id, name_value_table)

        if id_table is None:
            return b, s, []

        need_id = u'{}_id'.format(table_reference)

        query = u'SELECT sto_count_min, sto_count_max, sto_time_count, sto_time FROM {} WHERE {}'.format(
            u'sto_{}'.format(table_reference),
            (COL(need_id) == id_table).to_sql())

        # print 'query in sto data-> ' + query
        sto_data = self._run_query(query)

        # print sto_data
        if sto_data is None:
            return False, 'STO not found', []

        data = []

        for sto in tuple(sto_data):
            current_data = []
            current_data.append(sto[0])
            current_data.append(sto[1])
            current_data.append(sto[2])
            current_data.append(sto[3])
            data.append(current_data)

        return True, '', data

    def lto_data(self, table_reference, medicaid_id, name_value_table):
        b, s, id_table = self.id_table(table_reference, medicaid_id, name_value_table)

        if id_table is None:
            return b, s, []

        need_id = u'{}_id'.format(table_reference)

        query = u'SELECT lto_count, lto_time_count, lto_time, mastered FROM {} WHERE {}'.format(
            u'lto_{}'.format(table_reference),
            (COL(need_id) == id_table).to_sql()
        )

        lto_data = self._run_query(query)

        if lto_data is None:
            return False, 'LTO not found', []

        data = []
        exist = False
        for sto in tuple(lto_data):
            data.append(sto[0])
            data.append(sto[1])
            data.append(sto[2])
            data.append(sto[3])
            exist = True

        if not exist:
            return False, 'LTO not found', []

        return True, '', data

    def measure(self, name_table, medicaid_id, name_in_combo_box):
        row_id = self.id_kid(medicaid_id)
        if row_id is None:
            return False, None

        query = u'SELECT measure FROM {} WHERE ({} AND {})'.format(
            name_table,
            (COL('kids_id') == row_id).to_sql(),
            (COL('name') == name_in_combo_box)
        )

        result = self._run_query(query)
        measure = None
        for item in tuple(result):
            measure = item[0]
        if measure is not None:
            return True, measure

        return False, None
    # endregion

    # region Updates
    def update_run_query(self, query):
        with sqlite3.connect(self.db_file_path) as conn:
            c = conn.cursor()

            try:
                # row
                c.execute(query)

                # commit changes
                conn.commit()

            except Exception as e:
                stderr.write(e.message)
                return False, e.message
            else:
                stdout.write('DB \'{}\' successfully updated!\n'.format(self.db_name))
                return True, 'Successfully updated!'

    def update_table(self, table_name, column_name, column_value, medicaid_id, old_value=''):
        row_id = self.id_kid(medicaid_id)
        if table_name == 'behaviors' or table_name == 'programs':
            need_query = (COL('kids_id') == row_id).to_sql()
            query = u'UPDATE {} SET {} = {} WHERE ({} AND {})'.format(
                table_name,
                column_name,
                u'"{}" '.format(column_value),
                (COL(column_name) == old_value).to_sql(),
                need_query)
            # print query
        else:
            need_query = (COL('medicaidID') == medicaid_id).to_sql()

            query = u'UPDATE {} SET {} = {} WHERE {}'.format(
                table_name,
                column_name,
                u'"{}" '.format(column_value),
                need_query)

        return self.update_run_query(query)

    # Esto es para las tablas 'baseline_{}, lto_{} , sto_{}'
    def update_components_table(self, table_name, columns_name, columns_value, medicaid_id, name_in_line_edit,
                                column_aux='string_rep', name_in_combo_box=''):

        # print '--EN UPDATE COMPONENTS'
        # print 'table_name ' + table_name
        # print 'columns_value ==>'
        # print columns_value
        # print 'name_in_line_edit ' + name_in_line_edit
        # print 'column_aux ' + column_aux
        # print 'name_in_combo_box ' + name_in_combo_box

        if table_name.endswith('behaviors'):
            need_name = 'behaviors'
            need_id = u'{}_id'.format(need_name)
        elif table_name.endswith('programs'):
            need_name = 'programs'
            need_id = u'{}_id'.format(need_name)

        _, _, id_table = self.id_table(need_name, medicaid_id, name_in_line_edit)

        if id_table is None:
            return False, 'Table not found'

        list_columns = [col_n + "=" + u'"{}"'.format(columns_value[i]) for i, col_n in enumerate(columns_name)]

        if table_name.startswith('data'):
            query = u'UPDATE {} SET {} WHERE  ({} AND {})'.format(
                table_name,
                u', '.join(l for l in list_columns),
                (COL(need_id) == id_table).to_sql(),
                (COL('date') == name_in_combo_box).to_sql())
            print 'query CON name_in_combo_box--> ' + query

        else:
            if name_in_combo_box is not '':
                query = u'UPDATE {} SET {} WHERE  ({} AND id=={})'.format(
                    table_name,
                    u', '.join(l for l in list_columns),
                    (COL(need_id) == id_table).to_sql(),
                    name_in_combo_box)

                print 'query CON name_in_combo_box--> ' + query

            else:
                query = u'UPDATE {} SET {} WHERE {}'.format(
                    table_name,
                    u', '.join(l for l in list_columns),
                    (COL(need_id) == id_table).to_sql())
                print 'query SIN name_in_combo_box--> ' + query

        return self.update_run_query(query)
    # endregion

    def delete_registros(self, table_name, medicaid_id, name_in_line_edit):
        if table_name.endswith('behaviors'):
            need_name = 'behaviors'
            need_id = u'{}_id'.format(need_name)
        elif table_name.endswith('programs'):
            need_name = 'programs'
            need_id = u'{}_id'.format(need_name)

        _, _, id_table = self.id_table(need_name, medicaid_id, name_in_line_edit)

        if id_table is None:
            return False, 'Table not found'

        query = u'DELETE FROM {} WHERE {}'.format(
            table_name,
            (COL(need_id) == id_table).to_sql()
        )
        return self.update_run_query(query)

    def need(self):
        l = self.list_behavior_or_program('programs', str(9461200935))
        for i in l:
            _, _, id_table = self.id_table('programs', str(9461200935), str(i))

            query = u'SELECT value FROM {} WHERE ({} AND {})'.format(
                'data_programs',
                (COL('programs_id') == id_table).to_sql(),
                (COL('date') == '2018-04-28').to_sql()
            )
            data = self._run_query(query)
            for item in tuple(data):
                if item[0] is -1:
                    col_n = 'comment'
                    list_columns = col_n + "=" + u'"{}"'.format('Vacations')

                    # list_columns = 'comment' + "=" + 'Vacations'

                    query = u'UPDATE {} SET {} WHERE ({} AND {})'.format(
                        'data_programs',
                        list_columns,
                        (COL('programs_id') == id_table).to_sql(),
                        (COL('date') == '2018-04-28').to_sql())
                    self.update_run_query(query)

    # region Bool Methods
    def existing_data(self, table_reference, medicaid_id, name_in_line_edit, date):
        b, s, row_id = self.id_table(table_reference, medicaid_id, name_in_line_edit)

        if row_id is None:
            return b, s

        id_need = u'{}_id'.format(table_reference)
        table = u'data_{}'.format(table_reference)
        query = u'SELECT id FROM {} WHERE ({} AND {})'.format(
            table,
            (COL(id_need) == row_id).to_sql(),
            (COL('date') == date).to_sql()
        )

        result = self._run_query(query)

        # si da true es q esta llena la tupla
        if tuple(result):
            return True
        return False

    def existing_child(self, username, name, last_name, age, medicaid_id, analyst):
        row_id = self.id_user(username)

        if row_id is None:
            return False, 'user not found', []

        query = u'SELECT medicaidID, kid_name, last_name, kid_age, analyst FROM kids WHERE ({})'.format(
            (COL('user_id') == row_id).to_sql())

        kids_names = self._run_query(query)
        for kids in tuple(kids_names):
            if kids[0] == str(medicaid_id) and kids[1] == name and kids[2] == last_name and kids[3] == age and \
                            kids[4] == analyst:
                return True, 'child already exist', [kids[0], kids[1], kids[2], kids[3], kids[4]]
            elif kids[0] == str(medicaid_id):
                return True, 'medicaid ID already exist', []
        return False, 'not exist', []
    # endregion

    # region STATIC METHODS
    @staticmethod
    def _get_query(query, filter=None, limit=None, offset=None):
        if filter is not None:
            query += ' WHERE {}'.format(filter)
        if limit is not None and limit >= 0:
            query += ' LIMIT {}'.format(limit)
        if offset is not None and offset > 0:
            query += ' OFFSET {}'.format(offset)
        return query

    @staticmethod
    def __get_type(type):
        type = type.strip().upper()

        # some sanitation for common types, just in case...
        if type in ('INT', 'BOOL', 'BOOLEAN'):
            type = 'INTEGER'
        elif type in ('FLOAT', 'DOUBLE'):
            type = 'REAL'

        return type if type in ('INTEGER', 'REAL') else 'TEXT'

    @staticmethod
    def __get_value(value, value_type):
        if value is None:
            return 'NULL'

        if value_type == 'INTEGER':
            # special treatment for booleans...
            if type(value) is bool:
                return '1' if value else '0'
            if type(value) in (str, unicode) and value.lower().strip() in ('true', 'false'):
                return '1' if value.lower().strip() == 'true' else '0'

            return str(int(value))

        elif value_type == 'REAL':
            return str(float(value))

        else:  # TEXT
            return u"\"{}\"".format(value)

    # endregion

    #region TABLES
    __QUERY_ALL = 'SELECT images.*, rois.* ' \
                  'FROM images LEFT JOIN rois ' \
                  'ON rois.image_id = images.id '

    __QUERY_IMAGES_ALL = 'SELECT images.* FROM images'
    __QUERY_ROIS_ALL = 'SELECT rois.* FROM rois'

    __USER_COLUMNS = {'username': 'text',
                      'password': 'text'}

    __KIDS_COLUMNS = {'user_id': 'int',
                      'kid_name': 'text',
                      'last_name': 'text',
                      'kid_age': 'int',
                      'analyst': 'text',
                      'medicaidID': 'text'}

    __BEHAVIORS_COLUMNS = {'kids_id': 'int',
                           'name': 'text',
                           'measure': 'text'}

    __BASELINE_BEHAVIORS_COLUMNS = {'behaviors_id': 'int',
                                    'bl_count_time': 'int',
                                    'bl_time': 'text',
                                    'bl_begin_date': 'text',
                                    'bl_end_date': 'text',
                                    'exist_bl_end_date': 'int'}

    __LTO_BEHAVIORS_COLUMNS = {'behaviors_id': 'int',
                               'lto_count': 'int',
                               'lto_time_count': 'int',
                               'lto_time': "text",
                               'mastered': 'INT',
                               'date_mastered': 'text'}

    __STO_BEHAVIORS_COLUMNS = {'behaviors_id': 'int',
                               'sto_count_min': 'INT',
                               'sto_count_max': 'INT',
                               'sto_time_count': 'INT',
                               'sto_time': 'TEXT',
                               'string_rep': 'TEXT',
                               'mastered': 'INT',
                               'date_mastered': 'text',
                               'number_sto': 'INT'}

    __DATA_BEHAVIORS_COLUMNS = {'behaviors_id': 'int',
                                'date': 'text',
                                'value': 'int',
                                'comment': 'text'}

    __PROGRAMS_COLUMNS = {'kids_id': 'int',
                          'name': 'text',
                          'measure': 'text'}

    __BASELINE_PROGRAMS_COLUMNS = {'programs_id': 'int',
                                   'bl_count_time': 'int',
                                   'bl_time': 'text',
                                   'bl_begin_date': 'text',
                                   'bl_end_date': 'text',
                                   'exist_bl_end_date': 'int'}

    __LTO_PROGRAMS_COLUMNS = {'programs_id': 'int',
                              'lto_count': 'int',
                              'lto_time_count': 'int',
                              'lto_time': "text",
                              'mastered': 'INT',
                              'date_mastered': 'text'}

    __STO_PROGRAMS_COLUMNS = {'programs_id': 'int',
                              'sto_count_min': 'INT',
                              'sto_count_max': 'INT',
                              'sto_time_count': 'INT',
                              'sto_time': 'TEXT',
                              'string_rep': 'TEXT',
                              'mastered': 'INT',
                              'date_mastered': 'text',
                              'number_sto': 'INT'}

    __DATA_PROGRAMS_COLUMNS = {'programs_id': 'int',
                               'date': 'text',
                               'value': 'int',
                               'comment': 'text'}

    __TABLES = {'user': __USER_COLUMNS,
                'kids': __KIDS_COLUMNS,
                'behaviors': __BEHAVIORS_COLUMNS,
                'baseline_behaviors': __BASELINE_BEHAVIORS_COLUMNS,
                'lto_behaviors': __LTO_BEHAVIORS_COLUMNS,
                'sto_behaviors': __STO_BEHAVIORS_COLUMNS,
                'data_behaviors': __DATA_BEHAVIORS_COLUMNS,
                'programs': __PROGRAMS_COLUMNS,
                'baseline_programs': __BASELINE_PROGRAMS_COLUMNS,
                'lto_programs': __LTO_PROGRAMS_COLUMNS,
                'sto_programs': __STO_PROGRAMS_COLUMNS,
                'data_programs': __DATA_PROGRAMS_COLUMNS
                }

    #endregion




if __name__ == '__main__':
    m = Manager()

    # b, s, d = m.sto_data_without_string('behaviors', '9539062969', 'Self-Injurious behavior')
    # print d

    # region CREATE
    m.create_db('user', {'username': 'TEXT', 'password': 'TEXT'})
    m.create_db('kids', {'kid_name': 'TEXT', 'last_name': 'TEXT', 'kid_age': 'INT', 'analyst': 'TEXT',
    'medicaidID': 'TEXT'},
                ['user'])

    # BEHAVIORS
    m.create_db('behaviors', {'name':'TEXT', 'measure':'TEXT'}, ['kids'])
    m.create_db('baseline_behaviors', {'bl_count_time': 'INT', 'bl_time': 'TEXT', 'bl_begin_date': 'TEXT',
                                       'bl_end_date': 'TEXT', 'exist_bl_end_date' : 'INT'}, ['behaviors'])
    m.create_db('lto_behaviors', {'lto_count': 'INT', 'lto_time_count': 'INT',
                                  'lto_time': "TEXT", 'mastered': 'INT', 'date_mastered': 'TEXT'},
                ['behaviors'])
    m.create_db('sto_behaviors', {'sto_count_min': 'INT', 'sto_count_max': 'INT',
                                  'sto_time_count': 'INT', 'sto_time': 'TEXT',
                                  'string_rep': 'TEXT', 'mastered': 'INT', 'date_mastered': 'TEXT',
                                  'number_sto': 'INT'},
                ['behaviors'])
    m.create_db('data_behaviors', {'date': 'TEXT', 'value': 'INT', 'comment': 'text'}, ['behaviors'])

    # PROGRAMS
    m.create_db('programs', {'name': 'TEXT', 'measure': 'TEXT'}, ['kids'])
    m.create_db('baseline_programs', {'bl_count_time': 'INT', 'bl_time': 'TEXT', 'bl_begin_date': 'TEXT',
                                      'bl_end_date': 'TEXT', 'exist_bl_end_date' : 'INT'}, ['programs'])
    m.create_db('lto_programs', {'lto_count': 'INT', 'lto_time_count': 'INT',
                                 'lto_time': "TEXT", 'mastered': 'INT', 'date_mastered': 'TEXT'},
                ['programs'])

    m.create_db('sto_programs', {'sto_count_min': 'INT', 'sto_count_max': 'INT',
                                 'sto_time_count': 'INT', 'sto_time': 'TEXT',
                                 'string_rep': 'TEXT', 'mastered': 'INT', 'date_mastered': 'TEXT',
                                 'number_sto': 'INT'},
                ['programs'])

    m.create_db('data_programs', {'date': 'TEXT', 'value': 'INT', 'comment': 'text'}, ['programs'])
    # endregion

    # region CONSULTS
    # m.create_db('data_programs2', {'date': 'TEXT', 'value': 'INT', 'comment': 'text'}, ['user'])
    # m.insert('user', {'username': 'yessy11', 'password': 'ydr1912'})
    # # m.insert('data_programs2', {'date': '1900-01-01', 'value': 5, 'comment': ''},
    # #          data_references={'table': 'user', 'column_name': 'username', 'column_value': 'yessy11'})

    # query = u'SELECT password FROM user WHERE {}'.format(
    #     (COL('username') == 'yessica').to_sql()
    # )
    # rows = m._run_query(query)
    # print tuple(rows)

    # query = u'SELECT id FROM user WHERE {}'.format(
    #     (COL('username') == 'yessica').to_sql()
    # )
    # rows = m._run_query(query)
    # user_id = rows.next()[0]
    # print user_id
    #
    # query = u'SELECT kid_name, medicaidID FROM kids WHERE {}'.format(
    #     (COL('user_id') == user_id).to_sql()
    # )
    # list_kids = m._run_query(query)
    # print tuple(list_kids)
    #
    # for tuple_kid in list_kids:
    #     medicaidID = tuple_kid[1]
    #     query = u'SELECT id FROM kids WHERE ({} AND {})'.format(
    #         (COL('user_id') == user_id).to_sql(),
    #         (COL('medicaidID') == str(medicaidID)).to_sql()
    #     )
    #     rows = m._run_query(query)
    #     kid_id = rows.next()[0]
    #     print kid_id
    #
    #     behaviors = m.list_behavior_or_program('behaviors', str(medicaidID))
    #     for i in behaviors:
    #         if i == 'Impulsive':
    #             query = u'SELECT id FROM behaviors WHERE ({} AND {})'.format(
    #                 (COL('kids_id') == kid_id).to_sql(),
    #                 (COL('name') == str(i)).to_sql()
    #             )
    #             print query
    #             rows_1 = m._run_query(query)
    #             kid_id_program = rows_1.next()[0]
    #             print kid_id_program
    #
    #             query = u'DELETE FROM sto_behaviors WHERE {}'.format(
    #                 (COL('behaviors_id') == kid_id_program).to_sql()
    #             )
    #             m.update_run_query(query)
    #             #
    #             query = u'DELETE FROM data_behaviors WHERE {}'.format(
    #                 (COL('behaviors_id') == kid_id_program).to_sql()
    #             )
    #             m.update_run_query(query)
    #
    #     prog = m.list_behavior_or_program('programs', med)
    #     for i in prog:
    #         # result = m.delete_table('programs', '9496673228', name_in_combo_box=str(i))
    #         # print result
    #         query = u'SELECT id FROM programs WHERE ({} AND {})'.format(
    #             (COL('kids_id') == kid_id).to_sql(),
    #             (COL('name') == str(i)).to_sql()
    #         )
    #         print query
    #         rows_1 = m._run_query(query)
    #         kid_id_program = rows_1.next()[0]
    #         print kid_id_program
    #
    #         # query = u'DELETE FROM programs WHERE {}'.format(
    #         #     (COL('programs_id') == kid_id_program).to_sql()
    #         # )
    #
    #         query = u'DELETE FROM data_programs WHERE {}'.format(
    #             (COL('programs_id') == kid_id_program).to_sql()
    #         )
    #         m.update_run_query(query)
    #
    #         query = u'DELETE FROM sto_programs WHERE {}'.format(
    #             (COL('programs_id') == kid_id_program).to_sql()
    #         )
    #         m.update_run_query(query)


        #region Delete sto
        # query = u'SELECT id FROM behaviors WHERE ({} AND {})'.format(
        #     (COL('kids_id') == kid_id).to_sql(),
        #     (COL('name') == str(i)).to_sql()
        # )
        # print query
        # rows_1 = m._run_query(query)
        # kid_id_program = rows_1.next()[0]
        # print kid_id_program
        #
        # query = u'DELETE FROM sto_behaviors WHERE {}'.format(
        #     (COL('behaviors_id') == kid_id_program).to_sql()
        # )
        # m.update_run_query(query)
        #endregion
    #
    # query = u'SELECT id FROM programs WHERE ({} AND {})'.format(
    #     (COL('kids_id') == kid_id).to_sql(),
    #     (COL('name') == '19- Parent Training - Data Collection').to_sql()
    # )
    # rows = m._run_query(query)
    # kid_id_program = rows.next()[0]
    # print kid_id_program

    # query = u'SELECT id FROM programs WHERE ({} AND {})'.format(
    #     (COL('kids_id') == kid_id).to_sql(),
    #     (COL('name') == '20- Parent Training - Generalization of skills').to_sql()
    # )
    # rows = m._run_query(query)
    # kid_id_program = rows.next()[0]
    # print kid_id_program

    # name_y = m.measure('programs', '9461200935', 'Request Break')
    # print 'name y'
    # print name_y



    # query = u'DELETE FROM programs WHERE {}'.format(
    #     (COL('name') == '19- Parent Training - Data Collection of maladaptive behaviors').to_sql()
    # )
    # delete_t = m._run_query(query)
    #
    # query = u'DELETE FROM programs WHERE {}'.format(
    #     (COL('name') == '19- Parent Training - Data Collection of maladaptive behaviors ').to_sql()
    # )
    # delete_t = m._run_query(query)
    #
    # query = u'DELETE FROM programs WHERE {}'.format(
    #     (COL('name') == '20- Parent Training - Generalization of skills').to_sql()
    # )
    # delete_t = m._run_query(query)
    #
    # query = u'SELECT id FROM programs WHERE ({} AND {})'.format(
    #     (COL('kids_id') == kid_id).to_sql(),
    #     # (COL('name') == '21- Parent Training - Generalization of skills').to_sql()
    #     (COL('name') == '19- Parent Training - Data Collection of maladaptive behaviors ').to_sql()
    # )
    # rows = m._run_query(query)
    # print tuple(rows)


    # if rows is not None:
    #     programs_id = rows.next()[0]
    # print programs_id

    # behaviors_id = rows.next()[0]
    # print behaviors_id
    #
    # query = u'SELECT id FROM behaviors WHERE ({} AND {})'.format(
    #     (COL('kids_id') == kid_id).to_sql(),
    #     (COL('name') == 'Tantrum').to_sql()
    # )
    # rows = m._run_query(query)
    # behaviors_id = rows.next()[0]
    # print behaviors_id
    #
    # query = u'SELECT date, value FROM data_behaviors WHERE ({})'.format(
    #     (COL('behaviors_id') == behaviors_id).to_sql()
    # )
    # rows = m._run_query(query)
    # print tuple(rows)
    #
    # b, message = m.update_components_table('data_behaviors', ['value'], [15], '9460188605', 'Tantrum',
    #                                                               column_aux='date',
    #                                                               name_in_combo_box= '2019-03-08')
    #
    # print b, message
    #
    # query = u'SELECT date, value FROM data_behaviors WHERE ({})'.format(
    #     (COL('behaviors_id') == behaviors_id).to_sql()
    # )
    # rows = m._run_query(query)
    # print tuple(rows)


    # query = u'DELETE FROM user where {}'.format(
    #     (COL('id') == row_id).to_sql()
    # )
    # a = m._run_query(query)
    # query = u'SELECT value FROM data_programs2 WHERE {}'.format(
    #     (COL('user_id') == row_id).to_sql()
    # )
    # a = m._run_query(query)
    # print tuple(a)[0]
    # m.insert('user', {'username': 'yessy11', 'password': 'ydr1912'})
    # m.add_kid('sol', 'isaac', 10)
    # m.insert('kids', {'kid_name':'ale', 'kid_age':10},data_references={'table':'user',
    #                                                                    'column_name':'username',
    #                                                                    'column_value':'yessy11'})
    # m.insert('behaviors', {'name': 'cry', 'measure': 'Time'}, data_references={'table': 'kids',
    #                                                                          'column_name': 'medicaidID',
    #                                                                          'column_value': '4040'})
    # print m.list_maladaptive_behavior(4040)
    # print m.list_kids('sol')
    # m.insert('user', {'username': 'oscar', 'password': 'oscar'})
    # print (COL('username') == 'yessy').to_sql()
    # print m.list_kids('sol')
    # print m.exist_user('yesssy')
    # print m.list_usernames()
    # m.add_lto_behaviors(4040, 'cry', 40, 30, 'Days')
    # print m.existing_child(username='sol', name='ale perez', age=26, medicaid_id=None, analyst=None)

    # print m.id_table('behaviors', 4040, 'cry')
    # print m.kid_data(4040)
    # m.update_table('kids', 'last_name', "rdguez", 25)
    # print m.list_kids('sol')
    # m.behavior_data(25, 'cry')
    # print m.update_components_table('baseline_behaviors', ['bl_count_time', 'bl_time'],
    #                           [3, 'Weeks'], 25, 'cry')
    # print m.update_table('kids', 'kid_name', 'solangel', 25)
    # m.existing_data('behaviors', 25, 'run', '2000-01-30', 0)
    # m.list_dates('behaviors', 30, 'callado')
    # m.measure('behaviors', 25, 'run')
    # print m.list_medicaid_kid('sol')
    # m.add_data_kid('behaviors', 25, 'run', '2000-01-08', 1)
    #
    # # print m.list_medicaid_kid('sol')
    # print m.list_behavior_or_program('behaviors', 25)
    # m.delete_table('behaviors', 25, 'run')
    # print m.list_behavior_or_program('behaviors', 25)
    # endregion

    # m.table_all_data('behaviors', str(9460188605), 'Tantrum')
    # l = m.list_medicaid_kid('yessica')
    # for item in l:
    #     b = m.list_behavior_or_program('behaviors', str(item))
    #     p = m.list_behavior_or_program('programs', str(item))
    #     for i in b:
    #         m.delete_registros('sto_behaviors', str(item), str(i))
    #         m.delete_registros('lto_behaviors', str(item), str(i))
    #     for i in p:
    #         m.delete_registros('sto_programs', str(item), str(i))
    #         m.delete_registros('lto_programs', str(item), str(i))

    # query = u'SELECT id FROM user WHERE {}'.format(
    #     (COL('username') == 'yessica').to_sql()
    # )
    # rows = m._run_query(query)
    # row_id = rows.next()[0]
    # print row_id
    #
    # med_l = ['9539062977']
    # for med in med_l:
    #     query = u'SELECT id FROM kids WHERE ({} AND {})'.format(
    #         (COL('user_id') == row_id).to_sql(),
    #         (COL('medicaidID') == med).to_sql()
    #     )
    #     rows = m._run_query(query)
    #     kid_id = rows.next()[0]
    #     print ('kid id', kid_id)
    #
    #     b = m.list_behavior_or_program('behaviors', str(med))
    #     p = m.list_behavior_or_program('programs', str(med))
    #
    #     print 'behaviors'
    #     for i in b:
    #         print str(i)
    #         query = u'SELECT id FROM behaviors WHERE ({} AND {})'.format(
    #             (COL('kids_id') == kid_id).to_sql(),
    #             # (COL('name') == '21- Parent Training - Generalization of skills').to_sql()
    #             (COL('name') == str(i)).to_sql()
    #         )
    #         rows = m._run_query(query)
    #         kid_id_program = rows.next()[0]
    #         print ('id-beh', kid_id_program)
    #
    #         # m.delete_registros('data_programs', med, '9- Social Skills- Takin turns during a play')
    #         query = u'DELETE FROM data_behaviors WHERE {}'.format(
    #             (COL('behaviors_id') == kid_id_program).to_sql()
    #         )
    #         m.update_run_query(query)
    #
    #     print 'programs'
    #     for i in p:
    #         print str(i)
    #         query = u'SELECT id FROM programs WHERE ({} AND {})'.format(
    #             (COL('kids_id') == kid_id).to_sql(),
    #             # (COL('name') == '21- Parent Training - Generalization of skills').to_sql()
    #             (COL('name') == str(i)).to_sql()
    #         )
    #         rows = m._run_query(query)
    #         kid_id_program = rows.next()[0]
    #         print ('id-prog', kid_id_program)
    #
    #         # m.delete_registros('data_programs', med, '9- Social Skills- Takin turns during a play')
    #         query = u'DELETE FROM data_programs WHERE {}'.format(
    #             (COL('programs_id') == kid_id_program).to_sql()
    #         )
    #         m.update_run_query(query)
    # #
    # print m.list_baseline('programs', str(9461200935),str('Parent Training - Deliver reinforcers'))
    #
    # m.list_dates('behaviors', str(9460188605), '1- Request Break')

    # list_medi = m.list_medicaid_kid('yessica')
    # for med in list_medi:
    #     print str(med) + '----------'
    #     list_bh = m.list_behavior_or_program('behaviors', str(med))
    #     for beh in list_bh:
    #         print str(beh) + '------------'
    #         print m.list_baseline('behaviors', str(med), str(beh))
    #     list_pg = m.list_behavior_or_program('programs', str(med))
    #     for pg in list_pg:
    #         print str(pg) + '------------'
    #         print m.list_baseline('programs', str(med), str(pg))

    # b, dict_dates_values = m.list_dates('programs', str(9496673228), "1- Request Break")
    # list_dates = dict_dates_values.keys()
    # list_values = dict_dates_values.values()
    # for i, date in enumerate(list_dates):
    #     print date
    #     print list_values[i]

    # l = m.sto_data_string('programs', str(9460188605), "15- Stay on task")[2]
    # print l
    # print l[1][1]
    # query = u'SELECT mastered FROM sto_programs WHERE id==424'
    #
    # print tuple(m._run_query(query))