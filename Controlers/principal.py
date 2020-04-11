#region Unused
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import QDateTime, QDate

# from tabulate import tabulate
from UI.add_data_kid import Ui_MainWindow as addDataKid_MainWindow
import matplotlib
import math
from numpy import ma
import matplotlib.pyplot as plt
# from Database.manager import Manager
from matplotlib.dates import DateFormatter
import numpy as np
#endregion
from PyQt4 import QtCore, QtGui
from Database.manager import Manager

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from UI.login import Ui_MainWindow as login_MainWindow
from UI.register import Ui_MainWindow as register_MainWindow
from UI.main import Ui_MainWindow as main_MainWindow

from UI.list_kids import Ui_MainWindow as listKids_MainWindow
from UI.show_kid import Ui_MainWindow as showKid_MainWindow

from UI.add_kid import Ui_MainWindow as addKid_MainWindow
from UI.add_STO import Ui_MainWindow as addSTO_MainWindow
from UI.add_data import Ui_MainWindow as addData_MainWindow

from UI.newBehavior import Ui_MainWindow as newBehavior_MainWindow

from UI.edit_STO import Ui_MainWindow as editSTO_MainWindow
from UI.edit_view import Ui_MainWindow as edit_MainWindow

from UI.table_view import Ui_MainWindow as table_MainWindow

from resources.graphics import Graphics

import os
from resources.export_data import create_monthly, create_excel
from resources.importations import read_data

import matplotlib.dates as dt


class EditWindow(QMainWindow, edit_MainWindow):
    def __init__(self, table_name, manager, finish, medicaid_id, name_program, parent=None):
        super(EditWindow, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.finish = finish
        self.medicaid_id = medicaid_id
        self.name_program_or_behavior = name_program

        self.stoProgram_message.setVisible(False)

        self.table_name = table_name

        b, self.old_measure = self.manager.measure(self.table_name, self.medicaid_id, self.name_program_or_behavior)
        # self.old_measure = str(self.measureProgram_comboBox.currentText())
        print self.old_measure

        text = u'{} Name:'.format(str(table_name).rpartition('s')[0].capitalize())
        if table_name is 'behaviors':
            text = u'Maladaptive {}'.format(text)
        self.label_10.setText(text)

        self.show_all()
        self.name_edit.clicked.connect(self.edit_name_met)
        self.baseline_edit.clicked.connect(self.edit_baseline_met)
        self.measure_edit.clicked.connect(self.edit_measure_met)
        self.lto_edit.clicked.connect(self.edit_lto_met)
        self.sto_edit.clicked.connect(self.edit_sto_met)

        self.cancelProgram_pushButton.clicked.connect(self.finish)
        self.addStoProgram_pushButton.clicked.connect(self.add_sto)
        self.baselineProgram_checkBox_2.stateChanged.connect(self.active_date)

        self.sto_comboBox.activated.connect(self.clear_error)

    def active_date(self):
        if self.baselineProgram_checkBox_2.isChecked():
            self.baselineProgram_dateEdit2.setEnabled(True)
        else:
            self.baselineProgram_dateEdit2.setEnabled(False)

    # table_name, column_name, column_value, medicaid_id
    def finish_edit_sto(self):
        self.show()
        self.ui_edit_sto.close()
        self.update_combo_box()

    def finish_add_sto(self):
        self.show()
        self.ui_add_sto.close()
        self.update_combo_box()

    def update_combo_box(self):
        self.sto_comboBox.clear()
        _, _, list_data = self.manager.sto_data_string(self.table_name, self.medicaid_id,
                                                       str(self.name_program_or_behavior))

        # ##print 'list data-->'
        # ##print list_data
        list_data = [string_sto[3] for string_sto in list_data]
        if list_data is not []:
            self.sto_comboBox.addItems(list_data)

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.stoProgram_message.setVisible(bool(self.error))
        self.stoProgram_message.setText(self.error)

    def show_all(self):
        b, s, data = self.manager.table_all_data(self.table_name, self.medicaid_id, str(self.name_program_or_behavior))
        if not b:
            self.error = s
            self.update_widgets()
        else:
            self.programName_lineEdit.setText(self.name_program_or_behavior)
            # #print 'data[measure]-->' + data['measure']

            if data['measure'] == 'Time':
                self.measureProgram_comboBox.setCurrentIndex(0)
            elif data['measure'] == '% of Opportunities' or data['measure'] == '%':
                self.measureProgram_comboBox.setCurrentIndex(1)
            else:
                self.measureProgram_comboBox.setCurrentIndex(2)

            # bl_count_time, bl_time, bl_begin_date, bl_end_date

            self.baselineProgram_spinBox_2.setValue(data['bl_count_time'])
            if data['bl_time'] == 'Weeks':
                self.baselineProgram_comboBox.setCurrentIndex(0)
            else:
                self.baselineProgram_comboBox.setCurrentIndex(1)

            time1 = dt.num2date(dt.datestr2num(data['bl_begin_date']))
            self.baselineProgram_dateEdit1.setDateTime(time1)
            if data['exist_bl_end_date']:
                time2 = dt.num2date(dt.datestr2num(data['bl_end_date']))
                self.baselineProgram_dateEdit2.setDateTime(time2)
                self.baselineProgram_checkBox_2.setChecked(True)
                self.baselineProgram_dateEdit2.setEnabled(True)

            # lto_count, lto_time_count, lto_time
            self.ltoProgram_spinBox1.setValue(data['lto_count'])
            self.ltoProgram_spinBox2.setValue(data['lto_time_count'])
            if data['lto_time'] == 'Days':
                self.ltoProgram_comboBox.setCurrentIndex(0)
            elif data['lto_time'] == 'Week':
                self.ltoProgram_comboBox.setCurrentIndex(1)
            else:
                self.ltoProgram_comboBox.setCurrentIndex(2)

            self.update_combo_box()

    def edit_name_met(self):
        name = str(self.programName_lineEdit.text())
        bool_fine, string_error = self.manager.update_table(self.table_name, 'name', name,
                                                            self.medicaid_id, self.name_program_or_behavior)
        if bool_fine:
            self.name_program_or_behavior = name
        self.error = string_error
        self.update_widgets()

    def edit_measure_met(self):
        measure = self.measureProgram_comboBox.currentText()
        print 'measure'
        print measure
        print 'old'
        print self.old_measure
        bool_fine, string_error = self.manager.update_table(self.table_name, 'measure', measure,
                                                            self.medicaid_id, str(self.old_measure))
        if bool_fine:
            self.old_measure = measure
        self.error = string_error
        self.update_widgets()

    def edit_baseline_met(self):
        # BASELINE
        enable = False
        bl_count_time = self.baselineProgram_spinBox_2.value()

        bl_time = self.baselineProgram_comboBox.currentText()

        bl_begin_date = self.baselineProgram_dateEdit1.date().toPyDate()
        print 'bl begin date --> ' + str(bl_begin_date)
        bl_end_date = self.baselineProgram_dateEdit1.date().addDays(3).toPyDate()

        if self.baselineProgram_dateEdit2.isEnabled():
            bl_end_date = self.baselineProgram_dateEdit2.date().toPyDate()
            enable = True

        list_names = ['bl_count_time', 'bl_time', 'bl_begin_date', 'bl_end_date', 'exist_bl_end_date']
        list_values = [bl_count_time, bl_time, bl_begin_date, bl_end_date, int(enable)]

        print 'bl end date --> ' + str(bl_end_date)
        print 'enable->' + str(enable)
        # #print 'new list values'
        # #print list_values
        table_name_string = u'baseline_{}'.format(self.table_name)
        bool_fine, string_error = self.manager.update_components_table(table_name_string, list_names,
                                                                       list_values, self.medicaid_id,
                                                                       self.name_program_or_behavior)

        self.error = string_error
        self.update_widgets()

    def edit_lto_met(self):
        # LTO
        lto_count = self.ltoProgram_spinBox1.value()
        lto_time_count = self.ltoProgram_spinBox2.value()
        lto_time = self.ltoProgram_comboBox.currentText()

        list_names = ['lto_count', 'lto_time_count', 'lto_time']

        list_values = [lto_count, lto_time_count, lto_time]

        table_name_string = u'lto_{}'.format(self.table_name)
        bool_fine, string_error = self.manager.update_components_table(table_name_string, list_names, list_values,
                                                                       self.medicaid_id,
                                                                       self.name_program_or_behavior)

        self.error = string_error
        self.update_widgets()

    def edit_sto_met(self):
        if self.sto_comboBox.count() > 0:
            string_rep_value = str(self.sto_comboBox.currentText())
            if string_rep_value.endswith(').'):
                self.error = 'This STO has mastered'
                self.update_widgets()
            else:
                self.ui_edit_sto = EditSTOWindow(self.manager, self.finish_edit_sto, self.medicaid_id, self.table_name,
                                                 string_rep_value, self.name_program_or_behavior)
                self.close()
                self.ui_edit_sto.show()
        else:
            self.error = 'Not exist STO yet'
            self.update_widgets()

    def add_sto(self):
        self.clear_error()
        self.close()
        self.ui_add_sto = AddSTOWindow(self.table_name, self.manager, self.finish_add_sto, self.medicaid_id,
                                       self.name_program_or_behavior)
        self.ui_add_sto.show()


class EditSTOWindow(QMainWindow, editSTO_MainWindow):
    def __init__(self, manager, finish, medicaid_id, parent_table_name, string_rep_value, name_in_line_edit, parent=None):
        super(EditSTOWindow, self).__init__(parent)
        self.setupUi(self)
        if parent_table_name == 'programs':
            self.stoMathBehavior_comboBox.removeItem(0)
            self.stoMathBehavior_comboBox.removeItem(0)
            self.stoMathBehavior_comboBox.addItems(['no less than', 'between'])
            self.stoMathBehavior_comboBox.setCurrentIndex(0)
        self.manager = manager
        self.finish = finish
        self.medicaid_id = medicaid_id
        self.parent_table_name = parent_table_name
        self.string_rep_value = string_rep_value
        self.name_in_line_edit = name_in_line_edit

        self.show_all()
        self.stoBehavior_message_2.setVisible(False)

        self.stoMathBehavior_comboBox.activated.connect(self.selection_change)
        self.quit_pushButton.clicked.connect(self.finish)
        self.pushButton.clicked.connect(self.edit_sto)

    def selection_change(self):
        if self.stoMathBehavior_comboBox.currentText() == 'between':
            self.stoBehavior_spinBox2.setEnabled(True)
        else:
            self.stoBehavior_spinBox2.setEnabled(False)

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.stoBehavior_message_2.setVisible(bool(self.error))
        self.stoBehavior_message_2.setText(self.error)

    def show_all(self):
        # table_reference, medicaid_id, name_value
        b, s, data = self.manager.sto_data(self.parent_table_name, self.medicaid_id, self.name_in_line_edit,
                                           self.string_rep_value)
        # sto_count_min, sto_count_max, sto_time_count, sto_time
        # #print 's->' + str(s)
        if b:
            if data[0] is not -1:
                self.stoMathBehavior_comboBox.setCurrentIndex(1)

                self.stoBehavior_spinBox1.setValue(data[0])
                self.stoBehavior_spinBox2.setEnabled(True)
                self.stoBehavior_spinBox2.setValue(data[1])
            else:
                self.stoBehavior_spinBox1.setValue(data[1])

            self.stoBehavior_spinBox3.setValue(data[2])
            if data[3] == 'weeks':
                self.stoBehaviorTime_comboBox.setCurrentIndex(0)
            else:
                self.stoBehaviorTime_comboBox.setCurrentIndex(1)

    def edit_sto(self):
        # STO

        if self.stoBehavior_spinBox2.isEnabled():
            sto_count_min = self.stoBehavior_spinBox1.value()
            sto_count_max = self.stoBehavior_spinBox2.value()
        else:
            if self.parent_table_name == 'programs':
                sto_count_min = self.stoBehavior_spinBox1.value()
                sto_count_max = -1
            else:
                sto_count_max = self.stoBehavior_spinBox1.value()
                sto_count_min = -1

        sto_time_count = self.stoBehavior_spinBox3.value()
        sto_time = self.stoBehaviorTime_comboBox.currentText()

        if self.stoBehavior_spinBox2.isEnabled():
            string_rep = 'Between ' + str(sto_count_min) + ' y ' + str(sto_count_max) + ' incidents per week for ' \
                         + str(sto_time_count) + ' consecutive ' + str(sto_time)
        elif self.parent_table_name == 'behaviors':
            string_rep = 'No more than ' + str(sto_count_max) + ' incidents per week for ' \
                         + str(sto_time_count) + ' consecutive ' + str(sto_time)
        elif self.parent_table_name == 'programs':
            string_rep = 'No less than ' + str(sto_count_min) + ' incidents per week for ' \
                         + str(sto_time_count) + ' consecutive ' + str(sto_time)

        # table_name, columns_name, columns_value, medicaid_id, name_beh_prog):
        table = u'sto_{}'.format(self.parent_table_name)
        b, s = self.manager.update_components_table(table, ['sto_count_min', 'sto_count_max', 'sto_time_count',
                                                            'sto_time', 'string_rep'], [sto_count_min, sto_count_max,
                                                                                        sto_time_count, sto_time,
                                                                                        string_rep],
                                                    self.medicaid_id, self.name_in_line_edit,
                                                    name_in_combo_box=self.string_rep_value)

        self.error = s
        self.update_widgets()


class AddDataBehaviorProgramWindow(QMainWindow, addData_MainWindow):
    def __init__(self, table_name, manager, medicaid_id, user, name_program, close_add, parent=None):
        super(AddDataBehaviorProgramWindow, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.medicaid_id = medicaid_id
        self.user = user
        self.quit = close_add
        self.name_program_or_behavior = name_program
        self.table_name = table_name

        text = u'{} Name:'.format(str(table_name).rpartition('s')[0].capitalize())
        if table_name is 'behaviors':
            text = u'Maladaptive {}'.format(text)
        self.label.setText(text)
        self.message_label.setVisible(False)
        self.nameProgram_lineEdit.setText(self.name_program_or_behavior)

        self.data_value_spinBox.setEnabled(False)
        self.comments_lineEdit.setEnabled(False)
        self.data_dateEdit.dateChanged.connect(self.clear_error)
        self.data_value_spinBox.valueChanged.connect(self.clear_error)

        self.accept_button.clicked.connect(self.save_data)
        self.quit_button.clicked.connect(self.quit)

        self.value_checkBox.stateChanged.connect(self.enable_value)
        self.comments_checkBox.stateChanged.connect(self.enable_comments)

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.message_label.setVisible(bool(self.error))
        self.message_label.setText(self.error)

    def enable_value(self):
        self.comments_checkBox.setChecked(False)
        self.data_value_spinBox.setEnabled(True)
        self.comments_lineEdit.setEnabled(False)

    def enable_comments(self):
        self.value_checkBox.setChecked(False)
        self.data_value_spinBox.setEnabled(False)
        self.comments_lineEdit.setEnabled(True)

    def save_data(self):
        date = str(self.data_dateEdit.date().toPyDate())
        value = -1
        if not self.manager.existing_data(self.table_name, self.medicaid_id, self.name_program_or_behavior, date):
            if self.data_value_spinBox.isEnabled():
                value = self.data_value_spinBox.value()
                result = self.manager.add_data_kid(self.table_name, self.medicaid_id, self.name_program_or_behavior, date, value)
            elif self.comments_lineEdit.isEnabled():
                comment = str(self.comments_lineEdit.text())
                result = self.manager.add_data_kid(self.table_name, self.medicaid_id, self.name_program_or_behavior, date, value,
                                                   comment)
            self.error = result[1]
            self.update_widgets()
        else:
            self.error = 'This data already exist'
            self.update_widgets()


class AddKidWindow(QMainWindow, addKid_MainWindow):
    def __init__(self, manager, accept, user, parent=None):
        super(AddKidWindow, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.accept = accept
        self.user = user
        self.message_label.setVisible(False)
        self.update_combo_box()
        self.addBehaviors_Button.clicked.connect(self.add_behaviors)
        self.addProgram_Button.clicked.connect(self.add_program)
        self.acceptAddKid_pushButton.clicked.connect(self.my_accept)
        self.finish_pushButton.clicked.connect(self.my_quit)
        self.lineEdit.textChanged.connect(self.clear_error)
        self.kidName_lineEdit.textChanged.connect(self.clear_error)

        self.medicaidID_line_edit.textChanged.connect(self.clear_combo_box)
        self.medicaidID_line_edit.textChanged.connect(self.clear_error)

    def my_quit(self):
        self.lineEdit.setText(' ')
        self.kidName_lineEdit.setText(' ')
        self.clear_error()
        self.kidAge_spinBox.clear()
        self.medicaidID_line_edit.setText(' ')
        self.lineEdit_2.setText(' ')
        self.accept()

    def finish_behavior(self):
        self.show()
        self.ui_newBehavior.close()
        self.update_combo_box()
        self.error = 'Child successfully inserted'

    def finish_program(self):
        self.show()
        self.ui_newProgram.close()
        self.update_combo_box()

    def update_combo_box(self):
        self.comboBox_3.clear()
        self.comboBox.clear()
        name, last_name, age, medicaid_id, analyst = self.values()

        print 'estoy en el update combo en add kid con medicaid -->' + str(medicaid_id)
        list_behaviors = self.manager.list_behavior_or_program('behaviors', medicaid_id)
        list_programs = self.manager.list_behavior_or_program('programs', medicaid_id)

        print list_behaviors
        print list_programs

        self.comboBox_3.addItems(list_behaviors)
        self.comboBox.addItems(list_programs)

    def update_line_edit(self):
        self.lineEdit.setText(' ')
        self.kidName_lineEdit.setText(' ')

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.message_label.setVisible(bool(self.error))
        self.message_label.setText(self.error)

    def clear_error(self):
        self.error = ''
        self.update_widgets()
        self.clear_combo_box()

    def clear_combo_box(self):
        self.comboBox.clear()
        self.comboBox_3.clear()

    def values(self):
        kid_name = str(self.kidName_lineEdit.text())
        last_name = str(self.lineEdit.text())
        age = self.kidAge_spinBox.value()
        medicaid_id = str(self.medicaidID_line_edit.text())
        analyst = str(self.lineEdit_2.text())
        return kid_name, last_name, age, medicaid_id, analyst

    # TODO: poner un msj de rellenar los campos antes de add behavior y demas
    def my_add_kid(self, index):
        name, last_name, age, medicaid_id, analyst = self.values()
        print 'name ' + name
        print 'medicaid ' + medicaid_id
        if name is '' or medicaid_id is '':
            self.error = 'please fill the field Name and Medicaid ID'
            self.update_widgets()
        else:
            # medicaidID, kid_name, kid_age, analyst
            exist_kid, string_exist, list_values = self.manager.existing_child(self.user, name, last_name, age, medicaid_id,
                                                                               analyst)
            if exist_kid and not list_values == [] and index is 1:
                self.error = 'The child already exist'
                self.update_widgets()
                # self.update_lineEdit()
                # self.accept
            elif exist_kid and not list_values == [] and index is not 1:
                return True
            elif exist_kid and list_values == []:
                self.error = 'This Medical ID already exist'
                self.update_widgets()
            elif not exist_kid and not string_exist == 'user not found':
                self.manager.add_kid(self.user, name, last_name, age, medicaid_id, analyst)
                return True
        return False

    def add_behaviors(self):
        name, last_name, age, medicaid_id, analyst = self.values()
        my_bool = self.my_add_kid(2)
        if my_bool:
            self.close()
            self.ui_newBehavior = AddWindow('behaviors', self.manager, self.finish_behavior, medicaid_id)
            self.ui_newBehavior.show()

    def my_accept(self):
        my_bool = self.my_add_kid(1)
        if my_bool:
            self.error = 'Successful insertion'
            self.update_widgets()
            # self.addBehaviors_Button.setEnabled(False)
            # self.addProgram_Button.setEnabled(False)

    def add_program(self):
        name, age, last_name, medicaid_id, analyst = self.values()
        my_bool = self.my_add_kid(3)
        if my_bool:
            self.close()
            self.ui_newProgram = AddWindow('programs', self.manager, self.finish_program, medicaid_id)
            self.ui_newProgram.show()


class AddWindow(QMainWindow, newBehavior_MainWindow):
    def __init__(self, table_name, manager, finish, medicaid_id, parent=None):
        super(AddWindow, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.finish = finish
        self.medicaid_id = medicaid_id
        self.table_name = table_name
        # self.kid_name = kid_name
        self.stoBehavior_message.setVisible(False)
        self.acceptBehavior_pushButton.setEnabled(True)
        self.acceptBehavior_pushButton.clicked.connect(self.accept)

        self.behaviorName_lineEdit.textChanged.connect(self.clear_error)
        self.result = True
        self.cancelBehavior_pushButton.clicked.connect(self.finish)
        self.addStoBehavior_pushButton.clicked.connect(self.add_sto)
        self.baselineBehavior_checkBox.stateChanged.connect(self.active_date)

    def update_combo_box(self):
        self.sto_comboBox.clear()
        name = str(self.behaviorName_lineEdit.text())
        _, _, list_data = self.manager.sto_data_string(self.table_name, self.medicaid_id, str(name))
        print 'estoy en update combo box con table-> ' + self.table_name
        print list_data
        list_data = [s[3] for s in list_data]
        if list_data is not []:
            self.sto_comboBox.addItems(list_data)

    def finish_add_sto(self):
        self.ui_add_sto.close()
        self.update_combo_box()
        self.show()

    def clear_error(self):
        self.error = ''
        self.update_widgets()
        self.result = True
        self.sto_comboBox.clear()

    def active_date(self):
        if self.baselineBehavior_checkBox.isChecked():
            self.baselineBehavior_dateEdit2.setEnabled(True)
        else:
            self.baselineBehavior_dateEdit2.setEnabled(False)

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.stoBehavior_message.setVisible(bool(self.error))
        self.stoBehavior_message.setText(self.error)

    def add_sto(self):
        name_in_line_edit = str(self.behaviorName_lineEdit.text())
        if name_in_line_edit == '':
            if self.table_name == 'behaviors':
                self.error = 'Please fill the name of maladaptive behavior'
            else:
                self.error = 'Please fill the name of program'
            self.update_widgets()
        else:
            exist = True if name_in_line_edit in self.manager.list_behavior_or_program(self.table_name,
                                                                                       self.medicaid_id) else False
            if not exist:
                self.add_behavior_or_program()

            if self.result:
                self.close()
                self.ui_add_sto = AddSTOWindow(self.table_name, self.manager, self.finish_add_sto, self.medicaid_id,
                                               name_in_line_edit)
                self.ui_add_sto.show()

    def accept(self):
        print 'name table ->' + self.table_name
        name = str(self.behaviorName_lineEdit.text())
        print 'name beh or prog -> ' + name
        exist = True if name in self.manager.list_behavior_or_program(self.table_name, self.medicaid_id) else False
        if exist:
            if self.table_name == 'behaviors':
                self.error = 'This Maladaptive Behavior already exist'
            else:
                self.error = 'This Program already exist'
            print 'error->' + self.error
            self.update_widgets()
        if not exist:
            print 'no hubo error, entro al add'
            self.add_behavior_or_program()
            if self.result:
                self.error = 'Successful insertion'
                print self.error
                self.update_widgets()

    def add_behavior_or_program(self):
        print 'name table ->' + self.table_name

        name = str(self.behaviorName_lineEdit.text())

        print 'name-->' + name

        #BASELINE
        enable = False
        bl_count_time = self.baselineBehavior_spinBox.value()
        # #print 'bl_count_time-->' + str(bl_count_time)
        bl_time = self.baselineBehavior_comboBox.currentText()
        # #print 'bl_time-->' + str(bl_time)
        bl_begin_date = self.baselineBehavior_dateEdit1.date().toPyDate()
        bl_end_date = self.baselineBehavior_dateEdit1.date().addDays(3).toPyDate()
        # #print(bl_begin_date)

        if self.baselineBehavior_dateEdit2.isEnabled():
            bl_end_date = self.baselineBehavior_dateEdit2.date().toPyDate()
            enable = True
            # #print(bl_end_date)

        #MEASURE
        measure = str(self.measureBehavior_comboBox.currentText())

        #LTO
        lto_count = self.ltoBehavior_spinBox1.value()
        lto_time_count = self.ltoBehavior_spinBox2.value()
        lto_time = str(self.ltoBehavior_comboBox.currentText())

        exist = True if name in self.manager.list_behavior_or_program(self.table_name, self.medicaid_id) else False

        if exist:
            print 'exist true'

            self.finish()
        else:
            add_behavior_error = self.manager.add(self.table_name, self.medicaid_id, name, measure)
            if add_behavior_error[0]:
                print 'termino add'
                add_baseline_error = self.manager.add_baseline(self.table_name, self.medicaid_id, name,
                                                               bl_count_time,
                                                               bl_time, bl_begin_date,
                                                               bl_end_date, enable)
                if add_baseline_error[0]:
                    print 'termino add_baseline'
                    add_lto_error = self.manager.add_lto(self.table_name, self.medicaid_id, name, lto_count,
                                                         lto_time_count,
                                                         lto_time)
                    if not add_lto_error[0]:
                        self.error = add_baseline_error[1]
                        self.update_widgets()
                        self.result = False
                else:
                    self.error = add_baseline_error[1]
                    self.update_widgets()
                    self.result = False
            else:
                self.error = add_behavior_error[1]
                self.update_widgets()
                self.result = False


class AddSTOWindow(QMainWindow, addSTO_MainWindow):
    def __init__(self, table_reference, manager, finish, medicaid_id, name_in_line_edit, parent=None):
        super(AddSTOWindow, self).__init__(parent)
        self.setupUi(self)
        if table_reference == 'programs':
            self.stoMathBehavior_comboBox.removeItem(0)
            self.stoMathBehavior_comboBox.removeItem(0)
            self.stoMathBehavior_comboBox.addItems(['no less than', 'between'])
            self.stoMathBehavior_comboBox.setCurrentIndex(0)
        self.manager = manager
        self.finish = finish
        self.medicaid_id = medicaid_id
        self.name_in_line_edit = name_in_line_edit
        self.table_ref = table_reference
        # self.kid_name = kid_name
        self.mesage_add_sto.setVisible(False)

        self.stoMathBehavior_comboBox.activated.connect(self.clear_error)
        self.stoBehavior_spinBox1.valueChanged.connect(self.clear_error)
        self.stoBehavior_spinBox2.valueChanged.connect(self.clear_error)
        self.stoBehaviorTime_comboBox.activated.connect(self.clear_error)

        self.stoMathBehavior_comboBox.activated.connect(self.selection_change)
        self.addStoBehavior_pushButton.clicked.connect(self.add_sto)
        self.quit_pushButton.clicked.connect(self.finish)

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def selection_change(self):
        if self.stoMathBehavior_comboBox.currentText() == 'between':
            self.stoBehavior_spinBox2.setEnabled(True)
        else:
            self.stoBehavior_spinBox2.setEnabled(False)

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.mesage_add_sto.setVisible(bool(self.error))
        self.mesage_add_sto.setText(self.error)

    def add_sto(self):
        # STO
        if self.stoBehavior_spinBox2.isEnabled():
            sto_count_min = self.stoBehavior_spinBox1.value()
            sto_count_max = self.stoBehavior_spinBox2.value()

        else:
            if self.table_ref == 'programs':
                sto_count_min = self.stoBehavior_spinBox1.value()
                sto_count_max = -1
            else:
                sto_count_max = self.stoBehavior_spinBox1.value()
                sto_count_min = -1

        sto_time_count = self.stoBehavior_spinBox3.value()
        sto_time = self.stoBehaviorTime_comboBox.currentText()

        # if self.stoBehavior_spinBox2.isEnabled():
        #     string_rep = 'Between ' + str(sto_count_min) + ' and ' + str(sto_count_max) + ' incidents per week for ' \
        #                  + str(sto_time_count) + ' consecutive ' + str(sto_time)
        # elif self.table_ref == 'behaviors':
        #     string_rep = 'No more than ' + str(sto_count_max) + ' incidents per week for ' \
        #                  + str(sto_time_count) + ' consecutive ' + str(sto_time)
        # elif self.table_ref == 'programs':
        #     string_rep = 'No less than ' + str(sto_count_min) + ' incidents per week for ' \
        #                  + str(sto_time_count) + ' consecutive ' + str(sto_time)

        # exist = self.manager.sto_data_string(self.table_ref, self.medicaid_id, self.name_in_line_edit)[2]
        #
        # string_data_combo_box = True if string_rep in exist else False
        #
        # if string_data_combo_box:
        #     self.error = 'This STO already exist'
        #     self.update_widgets()
        #
        # else:
        # table_reference, medicaid_id, name, sto_count_min, sto_count_max, sto_time_count, sto_time
        add_sto_error = self.manager.add_sto(self.table_ref, self.medicaid_id, self.name_in_line_edit,
                                             sto_count_min, sto_count_max, sto_time_count, sto_time)
        self.error = add_sto_error[1]
        self.update_widgets()


class ShowTableWindow(QMainWindow, table_MainWindow):
    def __init__(self, manager, medicaid_id, table_name, kid_name, name_in_combo_box, finish, user, parent=None):
        super(ShowTableWindow, self).__init__(parent)
        self.setupUi(self)

        self.message_label.setVisible(False)

        self.user = user
        self.manager = manager
        self.medicaid_id = medicaid_id
        self.name_in_combo_box = name_in_combo_box
        self.kid_name = kid_name
        self.table_name = table_name
        self.finish = finish
        self.quit_pushButton.clicked.connect(self.finish)

        name = QString(self.kid_name + ' Data')
        self.setWindowTitle(name)

        name_aux = 'Program'
        if self.table_name == 'behaviors':
            name_aux = 'Maladaptive Behavior'

        name_2 = u'{}: {}'.format(str(name_aux),
                                  str(self.name_in_combo_box).capitalize())
        self.name_behavior_program_label.setText(QString(name_2))

        self.table_data()

        self.ui_add_data = AddDataBehaviorProgramWindow(self.table_name, self.manager, self.medicaid_id, self.user,
                                                        self.name_in_combo_box, self.quit_add_data)

        self.addData.clicked.connect(self.add_data)

        self.download_data_button.clicked.connect(self.create_excel_def)

    # @pyqtSlot()
    def update_data(self):
        b, data_kid = self.manager.list_dates(self.table_name, self.medicaid_id, self.name_in_combo_box)
        if b:
            list_date = data_kid.keys()
            print 'list date ==>'
            print list_date
            for currentQTableWidgetItem in self.tableWidget.selectedItems():
                self.clear_error()
                bad_changed = False
                date_null = False

                row = currentQTableWidgetItem.row()
                column = currentQTableWidgetItem.column()
                text_changed = currentQTableWidgetItem.text()

                print 'row ' + str(row)
                print 'column ' + str(column)
                print 'text changed ' + str(text_changed)

                if column is 0:
                    columns_name = ['date']
                    if text_changed.isEmpty():
                        date_null = True
                if date_null:
                    print 'date null'
                    table_name_temp = u'data_{}'.format(self.table_name)
                    print 'table_name_temp ->' + table_name_temp
                    self.manager.delete_table_part(table_name_temp, self.medicaid_id, self.name_in_combo_box,
                                                   list_date[row])
                    self.error = 'Deleted Date'
                    self.update_widgets()
                    self.tableWidget.removeRow(row)
                else:
                    if column is 1:
                        if (not text_changed.isEmpty() and not self.tableWidget.item(row, 2) is None) or \
                                (text_changed.isEmpty() and self.tableWidget.item(row, 2) is None):
                            print 'column is 1'
                            bad_changed = True
                        columns_name = ['value']

                        if text_changed.isEmpty():
                            text_changed = -1
                        else:
                            text_changed = int(text_changed)
                    else:
                        print self.tableWidget.item(row, 1)
                        if (not text_changed.isEmpty() and not self.tableWidget.item(row, 1) is None) or \
                                (text_changed.isEmpty() and self.tableWidget.item(row, 1) is None):
                            print 'column is 2'
                            bad_changed = True
                        columns_name = ['comment']

                    table_name_temp = u'data_{}'.format(self.table_name)

                    print '[columns_name] ==> '
                    print columns_name

                    b, message = self.manager.update_components_table(table_name_temp, columns_name, [text_changed],
                                                                  self.medicaid_id, self.name_in_combo_box,
                                                                  column_aux='date',
                                                                  name_in_combo_box=str(list_date[row]))

                    if not bad_changed:
                        self.error = message
                        self.update_widgets()
                    elif bad_changed:
                        self.error = message + ' but there are date with value and comments, both at the same time.'
                        self.update_widgets()

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def update_widgets(self):
        self.message_label.setVisible(bool(self.error))
        self.message_label.setText(self.error)

    def table_data(self):
        count_rows = 0

        # dict[date] = (value, comment)

        b, data_kid = self.manager.list_dates(self.table_name, self.medicaid_id, self.name_in_combo_box)
        if b:

            list_date = data_kid.keys()

            list_data = data_kid.values()
            self.tableWidget.setRowCount(len(list_data))
            self.tableWidget.setColumnCount(3)
            while count_rows < len(list_date):
                self.tableWidget.setItem(count_rows, 0, QTableWidgetItem(list_date[count_rows]))
                if list_data[count_rows][0] is not (-1):
                    self.tableWidget.setItem(count_rows, 1, QTableWidgetItem(str(list_data[count_rows][0])))
                self.tableWidget.setItem(count_rows, 2, QTableWidgetItem(list_data[count_rows][1]))
                count_rows += 1

            self.tableWidget.resizeColumnsToContents()
            name = QString(self.kid_name + ' Data')

            self.tableWidget.setWindowTitle(name)

            self.tableWidget.setHorizontalHeaderLabels(QString("Date; Value; Comments").split(';'))

            self.tableWidget.show()
        else:
            self.error= 'Not exist data yet'
            self.update_widgets()

        self.tableWidget.itemChanged.connect(self.update_data)

    def create_excel_def(self):
        create_excel(self.user, [self.kid_name, self.medicaid_id])
        QMessageBox.information(self, "HEY", "Excel created successfully", QMessageBox.Ok)

    def add_data(self):
        self.ui_add_data.show()
        self.hide()

    def quit_add_data(self):
        self.show()
        self.ui_add_data.close()


# revisar aqui cdo se crea el monthly q recuerdo q habian cosas mal en el doc q creaba
class ShowKidWindow(QMainWindow, showKid_MainWindow):
    def __init__(self, manager, user, medicaid_id, finish, parent=None):
        super(ShowKidWindow, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.user = user
        self.medicaid_id = medicaid_id
        self.finish = finish
        self.message_label.setVisible(False)

        self.automatic = False

        self.show_all()

        self.edit_age.clicked.connect(self.edit_age_met)
        self.edit_last_name.clicked.connect(self.edit_last_name_met)
        self.edit_name.clicked.connect(self.edit_name_met)
        self.edit_analyst.clicked.connect(self.edit_analyst_met)

        self.editBehavior_pushButton.clicked.connect(self.edit_behavior)
        self.editProgram_pushButton.clicked.connect(self.edit_program)

        self.addBehavior.clicked.connect(self.add_behavior)
        self.addProgram.clicked.connect(self.add_program)

        self.table_name = ''
        self.addDataBehaviors_Button.clicked.connect(self.table_data_behavior)
        self.addDataProgram_Button.clicked.connect(self.table_data_program)

        self.delete_behavior_pushButton.clicked.connect(self.delete_behavior)
        self.delete_program_pushButton.clicked.connect(self.delete_program)

        self.finish_pushButton.clicked.connect(self.finish)

        self.kidAge_spinBox.valueChanged.connect(self.clear_error)
        self.lineEdit.textEdited.connect(self.clear_error)
        self.kidName_lineEdit.textEdited.connect(self.clear_error)
        self.lineEdit_2.textEdited.connect(self.clear_error)

        self.viewGrahics_behavior.clicked.connect(self.show_graphic_behavior)
        self.viewGrahics_program.clicked.connect(self.show_graphic_program)

        self.export_monthly_button.clicked.connect(self.export_monthly)

    def finish_add(self):
        self.update_combo_box()
        self.show()
        self.ui_addProgram.close()

    def finish_add_behavior(self):
        self.update_combo_box()
        self.show()
        self.ui_addBehavior.close()

    def update_combo_box(self):
        print 'estoy update_combo_box'
        print 'table name-->' + self.table_name
        list_name = self.manager.list_behavior_or_program(self.table_name, self.medicaid_id)
        print list_name
        if self.table_name is 'behaviors':
            print 'entre a behaviors'
            self.comboBox_3.clear()
            if list_name:
                self.comboBox_3.addItems(list_name)
        else:
            print 'entre a programs'
            self.comboBox.clear()
            if list_name:
                self.comboBox.addItems(list_name)

    def finish_edit_program_or_behavior(self):
        self.ui_edit_program_or_behavior.close()
        self.show()
        self.update_combo_box()

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def update_widgets(self):
        # self.acceptButton.setEnabled(len(str(self.userLineEdit.text()))>0
        #                                       and len(str(self.passLineEdit.text()))>0)
        self.message_label.setVisible(bool(self.error))
        self.message_label.setText(self.error)

    def show_all(self):
        # kid_name, last_name, kid_age, analyst
        bool_exist, string_exist, data = self.manager.kid_data(self.medicaid_id)
        if bool_exist:
            self.kidName_lineEdit.setText(data[0])
            self.lineEdit.setText(data[1])
            self.kidAge_spinBox.setValue(int(data[2]))
            self.lineEdit_2.setText(data[3])
            self.medicaidID_line_edit.setText(self.medicaid_id)

            list_behaviors = self.manager.list_behavior_or_program('behaviors', self.medicaid_id)
            list_programs = self.manager.list_behavior_or_program('programs', self.medicaid_id)

            self.comboBox_3.addItems(list_behaviors)
            self.comboBox.addItems(list_programs)

    def edit_age_met(self):
        age = self.kidAge_spinBox.value()
        bool_fine, string_error = self.manager.update_table('kids', 'kid_age', age, self.medicaid_id)
        self.error = string_error
        self.update_widgets()

    def edit_last_name_met(self):
        last_name = str(self.lineEdit.text())
        bool_fine, string_error = self.manager.update_table('kids', 'last_name', last_name, self.medicaid_id)
        self.error = string_error
        self.update_widgets()

    def edit_name_met(self):
        kid_name = str(self.kidName_lineEdit.text())
        bool_fine, string_error = self.manager.update_table('kids', 'kid_name', kid_name, self.medicaid_id)
        self.error = string_error
        self.update_widgets()

    def edit_analyst_met(self):
        analyst = str(self.lineEdit_2.text())
        bool_fine, string_error = self.manager.update_table('kids', 'analyst', analyst, self.medicaid_id)
        self.error = string_error
        self.update_widgets()

    def edit_behavior(self):
        self.clear_error()
        if self.comboBox_3.count() > 0:
            self.table_name = 'behaviors'
            name_behavior = str(self.comboBox_3.currentText())
            self.ui_edit_program_or_behavior = EditWindow('behaviors', self.manager,
                                                          self.finish_edit_program_or_behavior,
                                                          self.medicaid_id, name_behavior)
            self.close()
            self.ui_edit_program_or_behavior.show()
        else:
            self.error = 'Not exist Behavior yet'
            self.update_widgets()

    def edit_program(self):
        self.clear_error()
        if self.comboBox.count() > 0:
            self.table_name = 'programs'
            name_program = str(self.comboBox.currentText())
            self.ui_edit_program_or_behavior = EditWindow('programs', self.manager,
                                                          self.finish_edit_program_or_behavior,
                                                          self.medicaid_id, name_program)
            self.close()
            self.ui_edit_program_or_behavior.show()
        else:
            self.error = 'Not exist Program yet'
            self.update_widgets()

    def add_program(self):
        self.clear_error()
        self.close()
        self.table_name = 'programs'
        self.ui_addProgram = AddWindow(self.table_name, self.manager, self.finish_add, self.medicaid_id)
        self.ui_addProgram.show()

    def add_behavior(self):
        self.clear_error()
        self.close()
        self.table_name = 'behaviors'
        self.ui_addProgram = AddWindow(self.table_name, self.manager, self.finish_add, self.medicaid_id)
        self.ui_addProgram.show()

    def delete_behavior(self):
        text = str(self.comboBox_3.currentText())

        result = self.manager.delete_table('behaviors', self.medicaid_id, text)

        index = self.comboBox_3.currentIndex()
        self.comboBox_3.removeItem(index)

    def delete_program(self):
        text = str(self.comboBox.currentText())

        result = self.manager.delete_table('programs', self.medicaid_id, text)

        index = self.comboBox.currentIndex()
        self.comboBox.removeItem(index)

    def table_data_behavior(self):
        self.table_name = 'behaviors'
        name_in_combo_box = str(self.comboBox_3.currentText())
        self.table_data(name_in_combo_box)

    def table_data_program(self):
        self.table_name = 'programs'
        name_in_combo_box = str(self.comboBox.currentText())
        self.table_data(name_in_combo_box)

    def table_data(self, name_in_combo_box):
        kid_name = str(self.kidName_lineEdit.text() + ' ' + self.lineEdit.text())

        self.ui_show_table = ShowTableWindow(self.manager, self.medicaid_id, self.table_name, kid_name, name_in_combo_box,
                                            self.finish_table_view, self.user)
        self.ui_show_table.show()
        self.close()

    def finish_table_view(self):
        self.show()
        self.ui_show_table.close()

    # def show_graphic_behavior(self):
    #     self.message_label.setVisible(False)
    #     name_in_combo_box = str(self.comboBox_3.currentText())
    #     self.show_graphic('behaviors', "Maladaptive Behaviors Graph", name_in_combo_box)
    #
    # def show_graphic_program(self):
    #     self.message_label.setVisible(False)
    #     name_in_combo_box = str(self.comboBox.currentText())
    #     self.show_graphic('programs', "Programs Graph", name_in_combo_box)

    def show_graphic_behavior(self):
        self.message_label.setVisible(False)
        name_in_combo_box = str(self.comboBox_3.currentText())
        # self.show_graphic('behaviors', "Maladaptive Behaviors Graph", name_in_combo_box)

        kid_name = self.kidName_lineEdit.text() + ' ' + self.lineEdit.text()
        a = Graphics(self.manager, self.user, self.medicaid_id)
        print 'name in comb in no automatic'
        print name_in_combo_box
        print kid_name
        print '----------'
        a.show_graphic('behaviors', "Maladaptive Behaviors Graph", name_in_combo_box, kid_name)

    def show_graphic_program(self):
        self.message_label.setVisible(False)
        name_in_combo_box = str(self.comboBox.currentText())
        # self.show_graphic('programs', "Programs Graph", name_in_combo_box)

        kid_name = self.kidName_lineEdit.text() + ' ' + self.lineEdit.text()
        a = Graphics(self.manager, self.user, self.medicaid_id)
        a.show_graphic('programs', "Programs Graph", name_in_combo_box, kid_name)

    # def show_graphic(self, table_name, title, name_in_combo_box):
    #     if self.automatic:
    #         print 'estoy en automatic '
    #         kid_name = self.kid_name
    #     else:
    #         print 'no autoamtic'
    #         kid_name = self.kidName_lineEdit.text() + ' ' + self.lineEdit.text()
    #     matplotlib.rcParams["figure.figsize"] = [12, 9]
    #
    #     b, dict_dates_values = self.manager.list_dates(table_name, self.medicaid_id, name_in_combo_box)
    #     name_y = self.manager.measure(table_name, self.medicaid_id, name_in_combo_box)
    #     if b:
    #         plt.ioff()
    #
    #         list_dates = dict_dates_values.keys()
    #
    #         list_tuple_value_comment = dict_dates_values.values()
    #
    #         list_dates = dt.datestr2num(list_dates)
    #
    #         list_comments = []
    #         list_values = []
    #         for k, item in enumerate(list_dates):
    #             list_comments.append(list_tuple_value_comment[k][1])
    #             list_values.append(list_tuple_value_comment[k][0])
    #
    #         list_mastered = self.verify_sto(table_name, name_in_combo_box, dict_dates_values)
    #
    #         date_lto_mastered = self.verify_lto(table_name, name_in_combo_box, dict_dates_values, list_mastered)
    #
    #         list_dates = list(list_dates)
    #         if date_lto_mastered:
    #             # print '----------------------entro----------------------'
    #             date_aux = list_dates[date_lto_mastered[0]]
    #             if len(list_dates) > date_lto_mastered[0] + 1:
    #                 difference = list_dates[date_lto_mastered[0] + 1] - list_dates[date_lto_mastered[0]]
    #                 if difference is not 0:
    #                     date_aux = list_dates[date_lto_mastered[0]] + difference - 1
    #                 list_dates.insert(date_lto_mastered[0] + 1, date_aux)
    #                 list_comments.insert(date_lto_mastered[0] + 1, '')
    #                 list_values.insert(date_lto_mastered[0] + 1, -3)
    #             else:
    #                 list_dates.append(date_aux + 1)
    #                 list_comments.append('')
    #                 list_values.append(-3)
    #         count_mastered_list = []
    #         count_inserted = 0
    #         for index, item in enumerate(list_mastered):
    #             date_aux = list_dates[item[0] + count_inserted]
    #
    #             if len(list_dates) > item[0] + count_inserted + 1:
    #
    #                 difference = list_dates[item[0] + count_inserted + 1] - list_dates[item[0] + count_inserted]
    #
    #                 if difference is not 0:
    #                     date_aux = list_dates[item[0] + count_inserted] + difference - 1
    #
    #                 list_dates.insert(item[0] + 1 + count_inserted, date_aux)
    #                 print '---sto mastered'
    #                 print dt.num2date(date_aux)
    #                 list_comments.insert(item[0] + 1 + count_inserted, '')
    #                 list_values.insert(item[0] + 1 + count_inserted, -2)
    #                 count_mastered_list.append(item[1])
    #                 count_inserted += 1
    #
    #             else:
    #                 list_dates.append(date_aux + 1)
    #                 print dt.num2date(date_aux + 1)
    #                 list_comments.append('')
    #                 list_values.append(-2)
    #                 count_mastered_list.append(item[1])
    #
    #         baseline = self.manager.list_baseline(table_name, self.medicaid_id, name_in_combo_box)
    #
    #         y_values = ma.masked_where((np.array(list_values) == -1) | (np.array(list_values) == -2) |
    #                                    (np.array(list_values) == -3), list_values)
    #
    #         low = min(list_dates)
    #         if low > dt.datestr2num(baseline[3]):
    #             low = dt.datestr2num(baseline[3])
    #         high = max(list_dates)
    #
    #         plt.xlim(low - 14, high + 14)
    #         low = min(y_values)
    #         if low > baseline[0]:
    #             low = baseline[0]
    #         high = max(y_values)
    #         if high < baseline[0]:
    #             high = baseline[0]
    #
    #         plt.ylim([math.ceil(low - 0.5 * (high - low)), math.ceil(high + 0.5 * (high - low))])
    #
    #         plt.plot_date(list_dates, y_values, marker='*', linestyle='-', color='k')
    #
    #         # Haciendo anotaciones con los comments
    #         y_comments = ma.masked_where((np.array(list_comments) == ''), list_comments)
    #
    #         for i, item in enumerate(y_comments):
    #             if type(item) is not np.ma.core.MaskedConstant:
    #                 # if table_name == 'behaviors':
    #                 #     xytext = (list_dates[i], high)
    #                 # else:
    #                 #     xytext = (list_dates[i], low)
    #                 # xytext = (list_dates[i], high)
    #                 #     color='g'
    #                 # plt.annotate(item, xy=(list_dates[i], plt.ylim()[0]), xycoords='data',
    #                 #              xytext=xytext, ha='center',
    #                 #              fontsize=12, color='k', arrowprops=dict(arrowstyle="->")).draggable()
    #                 plt.axvline(list_dates[i], color='k', ls=":", lw=1.2)
    #                 plt.text(list_dates[i], high, item, fontsize=12, rotation=90.)
    #         xytext = (plt.ylim()[1] + high) / float(2)
    #
    #         count_mastered = 0
    #         for i, item in enumerate(list_values):
    #             if item is (-2):
    #                 plt.axvline(list_dates[i], color='k', ls="--", lw=1.2)
    #                 text = u'STO #{}'.format(count_mastered_list[count_mastered])
    #                 plt.text(list_dates[i], xytext, text, fontsize=12, rotation=90.)
    #                 count_mastered += 1
    #             elif item is (-3):
    #                 plt.axvline(list_dates[i], color='k', ls="--", lw=1.2)
    #                 plt.text(list_dates[i], xytext, 'LTO', fontsize=12)
    #
    #         # PLOTEANDO LOS BASELINES
    #         if baseline:
    #             count = baseline[0]
    #             if baseline[1] is 'Months':
    #                 count = baseline[0] / 4
    #
    #             y0 = np.array([count, -1])
    #             baseline_aux = np.array([dt.datestr2num(baseline[2]), dt.datestr2num(baseline[3])])
    #             # #print baseline_aux
    #             # #print [baseline_aux == dt.datestr2num(baseline[3])]
    #             y = ma.masked_where((baseline_aux == dt.datestr2num(baseline[3])), y0)
    #             # #print y
    #             plt.xticks(rotation=30)
    #
    #             plt.plot_date(baseline_aux, y, marker='*', linestyle='-', color='k', label=name_in_combo_box)
    #             plt.axvline(dt.datestr2num(baseline[3]), color='k', ls='-', lw=1.2)
    #             plt.text(dt.datestr2num(baseline[3]), xytext, 'BL', fontsize=12)
    #
    #         formatter = DateFormatter('%m/%d/%y')
    #
    #         plt.gcf().autofmt_xdate()
    #         plt.gca().xaxis.set_major_formatter(formatter)
    #
    #         plt.xticks(rotation=30)
    #         plt.legend().draggable()
    #         # plt.legend(prop={'size': 9}).draggable()
    #         plt.suptitle(kid_name, fontsize=15)
    #         # title = u"{} Graph".format(str(table_name).capitalize())
    #         plt.title(title)
    #         plt.xlabel("WEEKS")
    #         plt.ylabel(str(name_y[1]).upper())
    #
    #         # plt.get_current_fig_manager().window.state('zoomed')
    #         # mng = plt.get_current_fig_manager()
    #         # mng.window.showMaximized()
    #
    #         # fig_size = plt.rcParams["figure.figsize"]
    #         # print "Current size:", fig_size
    #         # fig_size[0] = 12
    #         # fig_size[1] = 9
    #         # matplotlib.rcParams["figure.figsize"] = [12, 9]
    #
    #         if self.automatic:
    #             name = name_in_combo_box.replace("/", ' ')
    #             name = name.replace(":", ' ')
    #             plt.savefig(os.path.join(os.path.join(os.getcwd(), 'GRAPHICS'),
    #                                      table_name + ' ' + kid_name + ' ' + name + '.png'))
    #             plt.close()
    #             # import os
    #             # plt.imsave(os.path.join(os.getcwd(), kid_name + ' ' + title + '.png'))
    #         else:
    #             plt.show()
    #
    #     else:
    #         self.error = 'Not exist kid`s data yet'
    #         self.update_widgets()
    #
    # def verify_sto(self, table_name, name_in_combo_box, dict_dates_values):
    #     list_dates = dict_dates_values.keys()
    #     list_values = dict_dates_values.values()
    #     b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)
    #
    #     # name_aux = u'sto_{}'.format(table_name)
    #     # for item in string_sto:
    #     #     id_item = item[2]
    #     #     item = item[1]
    #     #     s = str(item).split('(M')[0]
    #     #     self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'], [0, ''], self.medicaid_id,
    #     #                                          name_in_combo_box, name_in_combo_box=id_item)
    #     #
    #     # b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)
    #     # print 'string sto de nuevo'
    #     # print string_sto
    #
    #     # list_result --> [(sto number mastered, date mastered)]
    #     list_result = []
    #     import datetime
    #     current_date = datetime.datetime(1, 1, 1).date()
    #
    #     current_time_to_look = 0
    #     current_index_sto = -1
    #     current_sto_string = ''
    #
    #     new_string_sto = []
    #     if b:
    #         for j, item in enumerate(string_sto):
    #             if not item[0]:
    #                 new_string_sto = [(val[3], val[2]) for val in string_sto if not val[0]]
    #                 break
    #             else:
    #                 i = list_dates.index(item[1])
    #                 list_result.append((i, j + 1, item[1]))
    #                 current_date = string_sto[j][1]
    #
    #         minus = len(string_sto) - len(new_string_sto)
    #         difference = minus if not minus == len(string_sto) else 0
    #
    #         for j, item in enumerate(new_string_sto):
    #
    #             if j > 0 and not list_result:
    #                 break
    #             if current_index_sto < j - 1:
    #                 break
    #
    #             all_ok, _, data = self.manager.sto_data(table_name, self.medicaid_id, name_in_combo_box, str(item[0]))
    #
    #             if all_ok:
    #                 count = 0
    #
    #                 time_to_look = data[2] if not data[3] == 'months' else data[2] * 4
    #                 if current_time_to_look is not 0 and current_time_to_look is time_to_look \
    #                         and current_index_sto + 1 is j and not current_sto_string == str(item[0]):
    #                     print 'entre al unir dos sto'
    #                     if table_name == 'programs':
    #                         if max_data is not -1 and ((data[1] is not -1 and data[0] <= max_data <= data[1]) or (
    #                                         data[1] is -1 and data[0] <= max_data)):
    #                             current_index_sto = j
    #                             new_tuple = (list_result[-1][0], list_result[-1][1] + 1, list_result[-1][2])
    #                             list_result[-1] = new_tuple
    #                             name_aux = u'sto_{}'.format(table_name)
    #
    #                             self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
    #                                                                  [1, list_result[-1][2]], self.medicaid_id,
    #                                                                  name_in_combo_box, name_in_combo_box=item[1])
    #
    #                             print 'update ' + item[0] + ' ' + str(list_result[-1][2])
    #
    #                             continue
    #                     elif table_name == 'behaviors' and max_data is not -1 and data[0] <= max_data <= data[1]:
    #                         current_index_sto = j
    #                         new_tuple = (list_result[-1][0], list_result[-1][1] + 1, list_result[-1][2])
    #                         list_result[-1] = new_tuple
    #                         name_aux = u'sto_{}'.format(table_name)
    #
    #                         self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
    #                                                              [1, list_result[-1][2]], self.medicaid_id,
    #                                                              name_in_combo_box, name_in_combo_box=item[1])
    #                         print 'update ' + item[0] + ' ' + str(list_result[-1][2])
    #
    #                         continue
    #
    #                 current_time_to_look = time_to_look
    #                 current_sto_string = str(item[0])
    #                 max_data = -1
    #                 for i, date in enumerate(list_dates):
    #
    #                     if date <= str(current_date):
    #                         continue
    #
    #                     if table_name == 'programs':
    #                         if list_values[i][0] is not -1:
    #                             if data[1] is not -1 and data[0] <= list_values[i][0] <= data[1]:
    #                                 if list_values[i][0] < max_data:
    #                                     max_data = list_values[i][0]
    #                                 count += 1
    #                             elif data[1] is -1 and data[0] <= list_values[i][0]:
    #                                 if list_values[i][0] < max_data:
    #                                     max_data = list_values[i][0]
    #                                 count += 1
    #                             else:
    #                                 count = 0
    #
    #                             print count
    #
    #                     elif table_name == 'behaviors':
    #
    #                         if list_values[i][0] is not -1 and data[0] <= list_values[i][0] <= data[1]:
    #                             if list_values[i][0] > max_data:
    #                                 max_data = list_values[i][0]
    #                             count += 1
    #
    #                         elif list_values[i][0] is not -1:
    #                             count = 0
    #
    #                     if count is time_to_look:
    #                         name_aux = u'sto_{}'.format(table_name)
    #                         self.manager.update_components_table(name_aux, ['mastered', 'date_mastered'],
    #                                                              [1, date], self.medicaid_id,
    #                                                              name_in_combo_box, name_in_combo_box=item[1])
    #                         list_result.append((i, j + 1 + difference, date))
    #                         current_index_sto = j
    #                         current_date = date
    #                         break
    #
    #     return list_result
    #
    # def verify_lto(self, table_name, name_in_combo_box, dict_dates_values, last_sto_mastered):
    #     list_dates = dict_dates_values.keys()
    #     list_values = dict_dates_values.values()
    #     tuple_result = ()
    #
    #     b, _, string_sto = self.manager.sto_data_string(table_name, self.medicaid_id, name_in_combo_box)
    #
    #     if len(last_sto_mastered) < 1 or last_sto_mastered[-1][1] < len(string_sto):
    #         return tuple_result
    #     # tuple_result --> [(lto number mastered, date mastered)]
    #     index_date = False
    #     last_sto_mastered = last_sto_mastered[-1]
    #     # lto_count, lto_time_count, lto_time, mastered
    #     all_ok, _, data = self.manager.lto_data(table_name, self.medicaid_id, name_in_combo_box)
    #     if all_ok:
    #         count = 0
    #         time_to_look = data[1]
    #         if data[2] == 'Months':
    #             time_to_look = (data[1] * 4)
    #         elif data[2] == 'Days':
    #             time_to_look = round(data[1] / float(30))
    #
    #         for i, date in enumerate(list_dates):
    #
    #             if not str(date) == str(last_sto_mastered[2]) and not index_date:
    #                 continue
    #             elif str(date) == str(last_sto_mastered[2]):
    #                 index_date = True
    #                 continue
    #             if index_date:
    #                 if table_name == 'programs':
    #                     if list_values[i][0] is not -1 and list_values[i][0] >= data[0]:
    #                         print 'count += 1'
    #
    #                         count += 1
    #                     else:
    #
    #                         count = 0
    #                 elif table_name == 'behaviors':
    #                     if list_values[i][0] is not -1 and list_values[i][0] <= data[0]:
    #                         print 'count += 1'
    #
    #                         count += 1
    #                     else:
    #
    #                         count = 0
    #
    #                 if count is time_to_look:
    #                     # table_name, columns_name, columns_value, medicaid_id, name_in_line_edit,
    #                     #     name_in_combo_box
    #                     name_aux = u'lto_{}'.format(table_name)
    #                     self.manager.update_components_table(name_aux, ['mastered'], [1], self.medicaid_id,
    #                                                          name_in_combo_box)
    #                     tuple_result = (i, date)
    #
    #                     break
    #
    #     return tuple_result

    def export_monthly(self):
        self.graphic_automatic()
        name = self.manager.kid_data(self.medicaid_id)[2]
        if name:
            kid_name = name[0] + ' ' + name[1]
            create_monthly(self.user, self.medicaid_id, kid_name)
            QMessageBox.information(self, "HEY", "Monthly created successfully", QMessageBox.Ok)
        # self.error = 'Monthly created successfully'
        # self.update_widgets()

    def download_data(self):
        self.automatic = True

    def graphic_automatic(self):
        self.automatic = True
        name = self.manager.kid_data(self.medicaid_id)[2]
        if name:
            self.kid_name = name[0] + ' ' + name[1]
            a = Graphics(self.manager, self.user, self.medicaid_id)
            list_beh = self.manager.list_behavior_or_program('behaviors', self.medicaid_id)
            list_program = self.manager.list_behavior_or_program('programs', self.medicaid_id)

            for beh in list_beh:
                print 'name in comb in automatic'
                print str(beh)
                print self.kid_name
                print '----------'
                a.show_graphic('behaviors', "Maladaptive Behaviors Graph", str(beh), self.kid_name)
            for program in list_program:
                a.show_graphic('programs', "Programs Graph", str(program), self.kid_name)
            self.automatic = False
            print '--------------END AUTOMATIC GRAPHICS'

        else:
            self.error = 'A error ocurred'
            self.update_widgets()


class ListWindows(QMainWindow, listKids_MainWindow):
    def __init__(self, manager, user, accept, cancel, parent=None):
        super(ListWindows, self).__init__(parent)
        self.setupUi(self)
        self.manager = manager
        self.user = user
        self.accept = accept
        self.cancel = cancel
        self.index_combo = 0

        self.update_combo_box()
        self.add_Button.clicked.connect(self.add_kid)
        self.view_edit_pushButton.clicked.connect(self.view_or_edit)
        self.cancel_pushButton.clicked.connect(self.cancel)

        # self.data_kid_button.clicked.connect(self.add_data_kid)
        self.delete_pushButton.clicked.connect(self.delete_kid)

        max_len = self.max_len_in_combo()
        self.horizontalLayout.setGeometry(QRect(0, 0, self.width() + max_len, self.height()))
        self.download_all_button.clicked.connect(self.create_all_documents)
        self.import_data_button.clicked.connect(self.import_all_data)

    def max_len_in_combo(self):
        max_len = 0
        for i in range(0, self.comboBox.count()):
            if len(self.comboBox.itemText(i)) > max_len:
                max_len = len(self.comboBox.itemText(i))
        return max_len

    def finish(self):
        self.show()
        self.ui_showKid.close()
        self.update_combo_box()

    def update_combo_box(self):
        c = self.comboBox.count()
        self.comboBox.clear()
        list_kids = self.manager.list_kids(self.user)
        self.comboBox.addItems(list_kids)
        if self.comboBox.count() > c:
            self.comboBox.setCurrentIndex(self.comboBox.count() - 1)
        else:
            self.comboBox.setCurrentIndex(self.index_combo)

    def add_kid(self):
        self.index_combo = self.comboBox.currentIndex()
        self.ui_addKid = AddKidWindow(self.manager, self.accept_add, self.user)
        self.close()
        self.ui_addKid.show()

    def accept_add(self):
        self.show()
        self.ui_addKid.close()
        self.update_combo_box()

    def view_or_edit(self):
        text = str(self.comboBox.currentText())
        self.index_combo = self.comboBox.currentIndex()
        medicaid_id = str.rsplit(text, '-->')[0]
        self.ui_showKid = ShowKidWindow(self.manager, self.user, medicaid_id, self.finish)
        self.close()
        self.ui_showKid.show()

    def close_add_data(self):
        self.ui_addData.close()
        self.show()

    def delete_kid(self):
        text = str(self.comboBox.currentText())

        medicaid_id = str.rsplit(text, '-->')[0]
        print 'en list kids'
        print str.rsplit(text, '-->')
        print 'medi -> ' + medicaid_id
        if medicaid_id is '-->':
            medicaid_id = ''
        result = self.manager.delete_table('kids', medicaid_id)

        index = self.comboBox.currentIndex()
        self.comboBox.removeItem(index)

    def create_all_documents(self):
        g = Graphics(self.manager, self.user)
        g.graphic_automatic()
        # create_excel(self.user)
        create_monthly(self.user)
        QMessageBox.information(self, 'HEY', "Documents created successfully", QMessageBox.Ok)

    def import_all_data(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        dialog.setDirectory(os.path.join(os.getcwd(), 'DOCS'))
        if dialog.exec_() == QDialog.Accepted:
            address = str(dialog.selectedFiles()[0])
            read_data(self.user, address)
            QMessageBox.information(self, 'HEY', "Data imported successfully", QMessageBox.Ok)
            self.update_combo_box()


class LoginWindow(QMainWindow, login_MainWindow):
    def __init__(self, manager, cancel_login, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setupUi(self)

        self.manager = manager
        self.cancel_login = cancel_login

        self.acceptButton.clicked.connect(self.login)
        self.cancelButton.clicked.connect(self.cancel_login)
        self.userLineEdit.textChanged.connect(self.clear_error)
        self.passLineEdit.textChanged.connect(self.clear_error)

    def accept(self):
        self.ui_list.close()
        self.show()

    def close_list(self):
        self.show()
        self.ui_list.close()

    def update_widgets(self):
        self.acceptButton.setEnabled(len(str(self.userLineEdit.text())) > 0 and len(str(self.passLineEdit.text())) > 0)
        self.errorLabel.setVisible(bool(self.error))
        self.errorLabel.setText(self.error)

    def reset(self):
        self.error = ''
        self.userLineEdit.setText('')
        self.passLineEdit.setText('')
        self.update_widgets()

    def clear_error(self):
        self.error = ''
        self.update_widgets()

    def login(self):
        self.user = str(self.userLineEdit.text())
        password = str(self.passLineEdit.text())
        self.error = self.manager.login_user(self.user, password)
        if not self.error[0]:
            self.error = self.error[1]
            self.update_widgets()
        else:
            self.ui_list = ListWindows(self.manager, self.user, self.accept, self.close_list)
            self.ui_list.comboBox.currentIndex()
            self.ui_list.show()
            self.close()


class RegisterWindow(QMainWindow, register_MainWindow):
    def __init__(self, manager, cancel, parent=None):
        super(RegisterWindow, self).__init__(parent)
        self.setupUi(self)
        # self.ui_login = login_MainWindow()
        # self.ui_register = register_MainWindow()
        self.manager = manager
        self.cancel = cancel
        self.cancelButton.clicked.connect(self.cancel)
        self.registerButton.clicked.connect(self.register)
        self.userLineEdit.textChanged.connect(self.clear_error)
        self.passLineEdit.textChanged.connect(self.clear_error)
        self.confirm_passLineEdit.textChanged.connect(self.clear_error)

    def update_widgets(self):
        self.registerButton.setEnabled(len(str(self.userLineEdit.text())) > 0
                                              and len(str(self.passLineEdit.text())) > 0
                                              and len(str(self.confirm_passLineEdit.text())) > 0)
        self.errorLabel.setVisible(bool(self.error))
        self.errorLabel.setText(self.error)

    def reset(self):
        self.error = ''
        self.userLineEdit.setText('')
        self.passLineEdit.setText('')
        self.confirm_passLineEdit.setText('')
        self.update_widgets()

    def clear_error(self):
        self.error=''
        self.update_widgets()

    def register(self):
        user = str(self.userLineEdit.text())
        password = str(self.passLineEdit.text())
        confirm = str(self.confirm_passLineEdit.text())
        self.error = 'passwords not matched' if not password == confirm \
            else self.manager.register_user(user, password)[1]
        self.update_widgets()


class MainWindow(QMainWindow, main_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.register_Button.setVisible(False)
        self.login_Button.setVisible(False)

        self.actionLogin.triggered.connect(self.show_login)
        self.actionRegister.triggered.connect(self.show_register)

        self.image = self.label
        path_list = [os.path.join(os.getcwd(), 'resources\index.png'),
                     os.path.join(os.getcwd(), 'resources\index1.png'), os.path.join(os.getcwd(), 'resources\index2.png')]
        # pixmax = QPixmap(os.path.join(os.getcwd(), 'dog.png'))
        self.load_list_backgrounds(path_list)
        self.change_background()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.change_background)
        self.timer.start()

        self.setHidden(True)
        self.manager = Manager()

        self.ui_register = RegisterWindow(self.manager, self.cancel_register)

        # self.register_Button.clicked.connect(self.show_register)

        self.ui_login = LoginWindow(self.manager, self.cancel_login)

        # self.login_Button.clicked.connect(self.show_login)

    def show_login(self):
        self.ui_register.setHidden(True)
        self.ui_login.setVisible(True)
        self.ui_login.reset()
        self.close()
        self.ui_login.show()

    def show_register(self):
        self.ui_login.setHidden(True)
        self.ui_register.setVisible(True)
        self.ui_register.reset()
        self.close()
        self.ui_register.show()

    def cancel_login(self):
        self.ui_login.close()
        self.show()

    def cancel_register(self):
        self.ui_register.close()
        self.show()

    def change_background(self):
        # print 'tick'
        pixmax = self.list_pixmaps[self.index_image % len(self.list_pixmaps)]
        self.image.setGeometry(20, 20, pixmax.width(), pixmax.height())
        self.resize(pixmax.width(), pixmax.height())
        self.image.setPixmap(pixmax)
        self.index_image += 1

    def load_list_backgrounds(self, path_list):
        self.list_pixmaps = [QPixmap(p) for p in path_list]

        self.index_image = 0
