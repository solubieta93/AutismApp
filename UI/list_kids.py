# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Yessica\UI\list_kids.ui'
#
# Created: Wed Oct 17 09:17:19 2018
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

import os

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QPixmap

from resources.button_class import PicButton

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(508, 154)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.horizontalLayout11 = QtGui.QHBoxLayout()
        self.horizontalLayout11.setObjectName(_fromUtf8("horizontalLayout11"))

        self.cancel_pushButton = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\camill_back.png")))
        self.cancel_pushButton.setToolTip("Back")
        self.horizontalLayout11.addWidget(self.cancel_pushButton)
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout11.addItem(spacerItem12)
        self.verticalLayout.addLayout(self.horizontalLayout11)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))

        self.add_Button = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\add_user_person-128.png")))
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.add_Button.sizePolicy().hasHeightForWidth())
        # self.add_Button.setSizePolicy(sizePolicy)
        self.add_Button.setToolTip("Add Kid")
        self.horizontalLayout.addWidget(self.add_Button)

        self.label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.horizontalLayout.addWidget(self.comboBox)

        spacerItem11 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem11)

        # import os

        # self.view_edit_pushButton = QtGui.QPushButton(self.centralwidget)
        self.view_edit_pushButton = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\add_user_person_persona-2-128.png")))
        # self.view_edit_pushButton.setIcon(icono)
        self.view_edit_pushButton.setToolTip("View\Edit")

        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.view_edit_pushButton.sizePolicy().hasHeightForWidth())
        # self.view_edit_pushButton.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.view_edit_pushButton.setFont(font)
        # self.view_edit_pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.view_edit_pushButton.setObjectName(_fromUtf8("view_edit_pushButton"))
        self.horizontalLayout.addWidget(self.view_edit_pushButton)

        # self.delete_pushButton = QtGui.QPushButton(self.centralwidget)
        self.delete_pushButton = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\delete_user_minus_one_person_people_team-128.png")))
        self.delete_pushButton.setToolTip("Delete Kid")
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.delete_pushButton.sizePolicy().hasHeightForWidth())
        # self.delete_pushButton.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.delete_pushButton.setFont(font)
        # self.delete_pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.delete_pushButton.setObjectName(_fromUtf8("delete_pushButton"))
        self.horizontalLayout.addWidget(self.delete_pushButton)

        # self.data_kid_button = QtGui.QPushButton(self.centralwidget)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.data_kid_button.sizePolicy().hasHeightForWidth())
        # self.data_kid_button.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.data_kid_button.setFont(font)
        # self.data_kid_button.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.data_kid_button.setObjectName(_fromUtf8("data_kid_button"))
        # self.horizontalLayout.addWidget(self.data_kid_button)

        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        spacerItem22 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem22)


        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)

        # self.add_Button = QtGui.QPushButton(self.centralwidget)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.add_Button.sizePolicy().hasHeightForWidth())
        # self.add_Button.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.add_Button.setFont(font)
        # self.add_Button.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.add_Button.setObjectName(_fromUtf8("add_Button"))

        self.import_data_button = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\table-import-128.png")))
        self.import_data_button.setToolTip("Import Data")
        self.horizontalLayout_3.addWidget(self.import_data_button)

        # self.cancel_pushButton = QtGui.QPushButton(self.centralwidget)
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.cancel_pushButton.setFont(font)
        # self.cancel_pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.cancel_pushButton.setObjectName(_fromUtf8("cancel_pushButton"))
        self.download_all_button = PicButton(QPixmap(os.path.join(os.getcwd(), "icon\\Download-Computer-128.png")))

        self.download_all_button.setToolTip("Download all")
        self.horizontalLayout_3.addWidget(self.download_all_button)

        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 508, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "User data", None))
        self.label.setText(_translate("MainWindow", "List of kids:", None))
        # self.view_edit_pushButton.setText(_translate("MainWindow", "View/Edit", None))
        self.delete_pushButton.setText(_translate("MainWindow", "Delete Kid", None))
        # self.data_kid_button.setText(_translate("MainWindow", "Add data", None))
        self.add_Button.setText(_translate("MainWindow", "Add a kid", None))
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel", None))

