import math
from numpy import ma
import matplotlib.pyplot as plt
import matplotlib.dates as dt
from matplotlib.dates import DateFormatter
import numpy as np
import os
import matplotlib
import datetime
from datetime import timedelta
from PyQt4 import QtCore, QtGui


from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Graphics:
    def __init__(self, manager, user, medicaid_id=None):
        self.manager = manager
        self.user = user
        self.automatic = False
        if medicaid_id is not None:
            self.medicaid_id = medicaid_id
        else:
            self.automatic = True

    def graphic_automatic(self):
        list_kids = self.manager.list_kids(self.user)
        for kid in list_kids:
            self.medicaid_id = str(kid.split('-->')[0])
            self.my_kid_name = str(kid.split('-->')[1])
            list_beh = self.manager.list_behavior_or_program('behaviors', self.medicaid_id)
            list_program = self.manager.list_behavior_or_program('programs', self.medicaid_id)

            for beh in list_beh:
                self.show_graphic('behaviors', "Maladaptive Behaviors Graph", str(beh))
            for program in list_program:
                self.show_graphic('programs', "Programs Graph", str(program))
        # print '--------------END AUTOMATIC GRAPHICS'

    def show_graphic(self, table_name, title, name_in_combo_box, kid_name=''):
        if self.automatic:
            print 'estoy en automatic '
            kid_name = self.my_kid_name
        else:
            # print 'no autoamtic'
            kid_name = kid_name
        matplotlib.rcParams["figure.figsize"] = [12, 9]

        b, dict_dates_values = self.manager.list_dates(table_name, self.medicaid_id, name_in_combo_box)
        name_y = self.manager.measure(table_name, self.medicaid_id, name_in_combo_box)
        if b:
            plt.ioff()

            list_dates = dict_dates_values.keys()

            list_tuple_value_comment = dict_dates_values.values()

            list_dates = dt.datestr2num(list_dates)

            list_comments = []
            list_values = []
            for k, item in enumerate(list_dates):
                list_comments.append(list_tuple_value_comment[k][1])
                list_values.append(list_tuple_value_comment[k][0])

            list_mastered = self.verify_sto(table_name, name_in_combo_box, dict_dates_values)

            date_lto_mastered = self.verify_lto(table_name, name_in_combo_box, dict_dates_values, list_mastered)

            list_dates = list(list_dates)
            if date_lto_mastered:
                # print '----------------------entro----------------------'
                date_aux = list_dates[date_lto_mastered[0]]
                if len(list_dates) > date_lto_mastered[0] + 1:
                    difference = list_dates[date_lto_mastered[0] + 1] - list_dates[date_lto_mastered[0]]
                    if difference is not 0:
                        date_aux = list_dates[date_lto_mastered[0]] + difference - 1
                    list_dates.insert(date_lto_mastered[0] + 1, date_aux)
                    list_comments.insert(date_lto_mastered[0] + 1, '')
                    list_values.insert(date_lto_mastered[0] + 1, -3)
                else:
                    list_dates.append(date_aux + 1)
                    list_comments.append('')
                    list_values.append(-3)

            count_mastered_list = []
            count_inserted = 0
            for index, item in enumerate(list_mastered):
                date_aux = list_dates[item[0] + count_inserted]

                if len(list_dates) > item[0] + count_inserted + 1:

                    difference = list_dates[item[0] + count_inserted + 1] - list_dates[item[0] + count_inserted]

                    if difference is not 0:
                        date_aux = list_dates[item[0] + count_inserted] + difference - 1

                    list_dates.insert(item[0] + 1 + count_inserted, date_aux)
                    # print '---sto mastered'
                    # print dt.num2date(date_aux)
                    list_comments.insert(item[0] + 1 + count_inserted, '')
                    list_values.insert(item[0] + 1 + count_inserted, -2)
                    count_mastered_list.append(item[1])
                    count_inserted += 1

                else:
                    list_dates.append(date_aux + 1)
                    # print dt.num2date(date_aux + 1)
                    list_comments.append('')
                    list_values.append(-2)
                    count_mastered_list.append(item[1])

            baseline = self.manager.list_baseline(table_name, self.medicaid_id, name_in_combo_box)

            y_values = ma.masked_where((np.array(list_values) == -1) | (np.array(list_values) == -2) |
                                       (np.array(list_values) == -3), list_values)

            low = min(list_dates)
            if low > dt.datestr2num(baseline[3]):
                low = dt.datestr2num(baseline[3])
            high = max(list_dates)

            plt.xlim(low - 14, high + 14)
            low = min(y_values)
            if low > baseline[0]:
                low = baseline[0]
            high = max(y_values)
            if high < baseline[0]:
                high = baseline[0]

            # plt.ylim([math.ceil(low - 0.5 * (high - low)), math.ceil(high + 0.5 * (high - low))])
            plt.ylim(0, math.ceil(high + 0.5 * (high - low)))
            plt.plot_date(list_dates, y_values, marker='*', linestyle='-', color='k')

            # Haciendo anotaciones con los comments
            y_comments = ma.masked_where((np.array(list_comments) == ''), list_comments)

            for i, item in enumerate(y_comments):
                if type(item) is not np.ma.core.MaskedConstant:
                    if item == 'Only one day collected':
                        plt.axvline(list_dates[i], color='k', ls="-", lw=1.5)
                        plt.text(list_dates[i], high, item, fontsize=12)
                    # if table_name == 'behaviors':
                    #     xytext = (list_dates[i], high)
                    # else:
                    #     xytext = (list_dates[i], low)
                    # xytext = (list_dates[i], high)
                    #     color='g'
                    # plt.annotate(item, xy=(list_dates[i], plt.ylim()[0]), xycoords='data',
                    #              xytext=xytext, ha='center',
                    #              fontsize=12, color='k', arrowprops=dict(arrowstyle="->")).draggable()
                    else:
                        plt.axvline(list_dates[i], color='k', ls=":", lw=1.2)
                        plt.text(list_dates[i], high, item, fontsize=12, rotation=90.)
            xytext = (plt.ylim()[1] + high) / float(2)

            count_mastered = 0
            for i, item in enumerate(list_values):
                if item is (-2):
                    plt.axvline(list_dates[i], color='k', ls="--", lw=1.2)
                    text = u'STO #{}'.format(count_mastered_list[count_mastered])
                    plt.text(list_dates[i], xytext, text, fontsize=12, rotation=90.)
                    count_mastered += 1
                elif item is (-3):
                    plt.axvline(list_dates[i], color='k', ls="--", lw=1.2)
                    plt.text(list_dates[i], xytext, 'LTO', fontsize=12)

            # PLOTEANDO LOS BASELINES
            if baseline:
                count = baseline[0]
                if baseline[1] is 'Months':
                    count = baseline[0] / 4

                y0 = np.array([count, -1])
                baseline_aux = np.array([dt.datestr2num(baseline[2]), dt.datestr2num(baseline[3])])
                # #print baseline_aux
                # #print [baseline_aux == dt.datestr2num(baseline[3])]
                y = ma.masked_where((baseline_aux == dt.datestr2num(baseline[3])), y0)
                # #print y
                plt.xticks(rotation=30)

                plt.plot_date(baseline_aux, y, marker='*', linestyle='-', color='k', label=name_in_combo_box)
                plt.axvline(dt.datestr2num(baseline[3]), color='k', ls='-', lw=1.2)
                plt.text(dt.datestr2num(baseline[3]), xytext, 'BL', fontsize=12)

            formatter = DateFormatter('%m/%d/%y')

            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_formatter(formatter)

            plt.xticks(rotation=30)
            plt.legend().draggable()
            # plt.legend(prop={'size': 9}).draggable()
            plt.suptitle(kid_name, fontsize=15)
            # title = u"{} Graph".format(str(table_name).capitalize())
            plt.title(title)
            plt.xlabel("WEEKS")
            # print '-------------------------'
            # print name_y[1]
            # print '----------------'
            plt.ylabel(str(name_y[1]).upper())

            # plt.get_current_fig_manager().window.state('zoomed')
            # mng = plt.get_current_fig_manager()
            # mng.window.showMaximized()

            # fig_size = plt.rcParams["figure.figsize"]
            # print "Current size:", fig_size
            # fig_size[0] = 12
            # fig_size[1] = 9
            # matplotlib.rcParams["figure.figsize"] = [12, 9]

            if self.automatic:
                name = name_in_combo_box.replace("/", ' ')
                name = name.replace(":", ' ')

                my_date = datetime.datetime.now()
                my_date = my_date.replace(day=1) - timedelta(days=1)
                my_date = my_date.strftime("%B") + ' ' + str(my_date.year)
                address = os.path.join(os.getcwd(), os.path.join('GRAPHICS', my_date))
                if not os.path.isdir(address):
                    os.mkdir(address)
                plt.savefig(os.path.join(address,
                                         table_name + ' ' + kid_name + ' ' + name + '.png'))
                plt.close()
                # import os
                # plt.imsave(os.path.join(os.getcwd(), kid_name + ' ' + title + '.png'))
            else:
                plt.show()

        else:
            pass
            # QMessageBox.warning(self, "Warning", "Not exist kids data yet", QMessageBox.Ok)

    def verify_sto(self, table_name, name_in_combo_box, dict_dates_values):
        list_dates = dict_dates_values.keys()
        list_values = dict_dates_values.values()
        b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)

        # name_aux = u'sto_{}'.format(table_name)
        # for item in string_sto:
        #     id_item = item[2]
        #     item = item[1]
        #     s = str(item).split('(M')[0]
        #     self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'], [0, ''], self.medicaid_id,
        #                                          name_in_combo_box, name_in_combo_box=id_item)
        #
        # b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)
        # print 'string sto de nuevo'
        # print string_sto

        # list_result --> [(sto number mastered, date mastered)]
        list_result = []
        import datetime
        current_date = datetime.datetime(1, 1, 1).date()

        current_time_to_look = 0
        current_index_sto = -1
        current_sto_string = ''

        new_string_sto = []
        if b:
            for j, item in enumerate(string_sto):
                if not item[0]:
                    new_string_sto = [(val[3], val[2]) for val in string_sto if not val[0]]
                    break
                else:
                    i = list_dates.index(item[1])
                    list_result.append((i, j + 1, item[1]))
                    current_date = string_sto[j][1]

            minus = len(string_sto) - len(new_string_sto)
            difference = minus if not minus == len(string_sto) else 0

            for j, item in enumerate(new_string_sto):

                if j > 0 and not list_result:
                    break
                if current_index_sto < j - 1:
                    break

                all_ok, _, data = self.manager.sto_data(table_name, self.medicaid_id, name_in_combo_box, str(item[0]))

                if all_ok:
                    count = 0

                    time_to_look = data[2] if not data[3] == 'months' else data[2] * 4
                    if current_time_to_look is not 0 and current_time_to_look is time_to_look \
                            and current_index_sto + 1 is j and not current_sto_string == str(item[0]):
                        print 'entre al unir dos sto'
                        if table_name == 'programs':
                            if max_data is not -1 and ((data[1] is not -1 and data[0] <= max_data <= data[1]) or (
                                            data[1] is -1 and data[0] <= max_data)):
                                current_index_sto = j
                                new_tuple = (list_result[-1][0], list_result[-1][1] + 1, list_result[-1][2])
                                list_result[-1] = new_tuple
                                name_aux = u'sto_{}'.format(table_name)

                                self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
                                                                     [1, list_result[-1][2]], self.medicaid_id,
                                                                     name_in_combo_box, name_in_combo_box=item[1])

                                print 'update ' + item[0] + ' ' + str(list_result[-1][2])

                                continue
                        elif table_name == 'behaviors' and max_data is not -1 and data[0] <= max_data <= data[1]:
                            current_index_sto = j
                            new_tuple = (list_result[-1][0], list_result[-1][1] + 1, list_result[-1][2])
                            list_result[-1] = new_tuple
                            name_aux = u'sto_{}'.format(table_name)

                            self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
                                                                 [1, list_result[-1][2]], self.medicaid_id,
                                                                 name_in_combo_box, name_in_combo_box=item[1])
                            print 'update ' + item[0] + ' ' + str(list_result[-1][2])

                            continue

                    current_time_to_look = time_to_look
                    current_sto_string = str(item[0])
                    max_data = -1
                    one_day_collected = False
                    for i, date in enumerate(list_dates):

                        if date <= str(current_date):
                            continue

                        if one_day_collected:
                            continue

                        if list_values[i][0] is -1 and str(list_values[i][1]).startswith('Only one day collected'):
                            # print 'only one day'
                            one_day_collected = True
                            continue
                        # print list_values[i][1]
                        if list_values[i][0] is -1 and str(list_values[i][1]).startswith('Normal Collection'):
                            one_day_collected = False
                            continue

                        if table_name == 'programs':
                            if list_values[i][0] is not -1:
                                if data[1] is not -1 and data[0] <= list_values[i][0] <= data[1]:
                                    if list_values[i][0] < max_data:
                                        max_data = list_values[i][0]
                                    count += 1
                                elif data[1] is -1 and data[0] <= list_values[i][0]:
                                    if list_values[i][0] < max_data:
                                        max_data = list_values[i][0]
                                    count += 1
                                else:
                                    count = 0

                                # print 'count ->' + str(count)
                        elif table_name == 'behaviors':
                            if list_values[i][0] is not -1 and data[0] <= list_values[i][0] <= data[1]:
                                if list_values[i][0] > max_data:
                                    max_data = list_values[i][0]
                                count += 1

                            elif list_values[i][0] is not -1:
                                count = 0

                        if count is time_to_look:
                            name_aux = u'sto_{}'.format(table_name)
                            self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
                                                                 [1, date], self.medicaid_id,
                                                                 name_in_combo_box, name_in_combo_box=item[1])
                            list_result.append((i, j + 1 + difference, date))
                            current_index_sto = j
                            current_date = date
                            break

        return list_result

    def verify_lto(self, table_name, name_in_combo_box, dict_dates_values, last_sto_mastered):
        list_dates = dict_dates_values.keys()
        list_values = dict_dates_values.values()
        tuple_result = ()

        b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)

        if len(last_sto_mastered) < 1 or last_sto_mastered[-1][1] < len(string_sto):
            return tuple_result
        # tuple_result --> [(lto number mastered, date mastered)]
        index_date = False
        last_sto_mastered = last_sto_mastered[-1]
        # lto_count, lto_time_count, lto_time, mastered
        all_ok, _, data = self.manager.lto_data(table_name, self.medicaid_id, name_in_combo_box)
        if all_ok:
            count = 0
            time_to_look = data[1]
            if data[2] == 'Months':
                time_to_look = (data[1] * 4)
            elif data[2] == 'Days':
                time_to_look = round(data[1] / float(30))

            for i, date in enumerate(list_dates):

                if not str(date) == str(last_sto_mastered[2]) and not index_date:
                    continue
                elif str(date) == str(last_sto_mastered[2]):
                    index_date = True
                    continue
                if index_date:
                    if table_name == 'programs':
                        if list_values[i][0] is not -1 and list_values[i][0] >= data[0]:
                            # print 'count += 1'

                            count += 1
                        else:
                            # ESTO TENGO Q QUITARLO
                            count = 0
                            # continue
                    elif table_name == 'behaviors':
                        if list_values[i][0] is not -1 and list_values[i][0] <= data[0]:
                            # print 'count += 1'

                            count += 1
                        else:
                            # ESTO TENGO Q QUITARLO
                            count = 0
                            # continue

                    if count is time_to_look:
                        # table_name, columns_name, columns_value, medicaid_id, name_in_line_edit,
                        #     name_in_combo_box
                        name_aux = u'lto_{}'.format(table_name)
                        self.manager.update_components_table(name_aux, ['mastered'], [1], self.medicaid_id,
                                                             name_in_combo_box)
                        tuple_result = (i, date)

                        break

        return tuple_result
