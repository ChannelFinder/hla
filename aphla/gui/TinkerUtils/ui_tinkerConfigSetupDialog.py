# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tinkerConfigSetupDialog.ui'
#
# Created: Fri Feb 28 21:07:13 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(702, 605)
        self.verticalLayout_6 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(9)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_configDBView = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_configDBView.setMargin(0)
        self.gridLayout_configDBView.setObjectName(_fromUtf8("gridLayout_configDBView"))
        self.widget_configDBView = QtGui.QWidget(self.layoutWidget)
        self.widget_configDBView.setObjectName(_fromUtf8("widget_configDBView"))
        self.gridLayout_5 = QtGui.QGridLayout(self.widget_configDBView)
        self.gridLayout_5.setMargin(0)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.gridLayout_configDBView.addWidget(self.widget_configDBView, 0, 0, 2, 1)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.pushButton_addRow = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_addRow.setObjectName(_fromUtf8("pushButton_addRow"))
        self.verticalLayout_5.addWidget(self.pushButton_addRow)
        self.pushButton_removeRow = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_removeRow.setObjectName(_fromUtf8("pushButton_removeRow"))
        self.verticalLayout_5.addWidget(self.pushButton_removeRow)
        self.gridLayout_configDBView.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 18, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_configDBView.addItem(spacerItem, 1, 1, 1, 1)
        self.layoutWidget1 = QtGui.QWidget(self.splitter)
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.gridLayout_7 = QtGui.QGridLayout(self.layoutWidget1)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.checkBox_synced_group_weight = QtGui.QCheckBox(self.layoutWidget1)
        self.checkBox_synced_group_weight.setChecked(True)
        self.checkBox_synced_group_weight.setObjectName(_fromUtf8("checkBox_synced_group_weight"))
        self.gridLayout_4.addWidget(self.checkBox_synced_group_weight, 0, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.layoutWidget1)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 1, 0, 1, 1)
        self.lineEdit_ref_step_size = QtGui.QLineEdit(self.layoutWidget1)
        self.lineEdit_ref_step_size.setObjectName(_fromUtf8("lineEdit_ref_step_size"))
        self.gridLayout_4.addWidget(self.lineEdit_ref_step_size, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.layoutWidget1)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)
        self.lineEdit_masar_id = QtGui.QLineEdit(self.layoutWidget1)
        self.lineEdit_masar_id.setObjectName(_fromUtf8("lineEdit_masar_id"))
        self.gridLayout_4.addWidget(self.lineEdit_masar_id, 2, 1, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(self.layoutWidget1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_config_name = QtGui.QLineEdit(self.layoutWidget1)
        self.lineEdit_config_name.setObjectName(_fromUtf8("lineEdit_config_name"))
        self.gridLayout_3.addWidget(self.lineEdit_config_name, 0, 1, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.layoutWidget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout_3.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.textEdit = QtGui.QTextEdit(self.layoutWidget1)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout_3.addWidget(self.textEdit, 1, 1, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_3, 0, 1, 3, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem2, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.pushButton_import = QtGui.QPushButton(self.layoutWidget1)
        self.pushButton_import.setObjectName(_fromUtf8("pushButton_import"))
        self.verticalLayout_4.addWidget(self.pushButton_import)
        self.pushButton_export = QtGui.QPushButton(self.layoutWidget1)
        self.pushButton_export.setObjectName(_fromUtf8("pushButton_export"))
        self.verticalLayout_4.addWidget(self.pushButton_export)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.comboBox_import = QtGui.QComboBox(self.layoutWidget1)
        self.comboBox_import.setMinimumSize(QtCore.QSize(115, 0))
        self.comboBox_import.setObjectName(_fromUtf8("comboBox_import"))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.comboBox_import.addItem(_fromUtf8(""))
        self.verticalLayout_3.addWidget(self.comboBox_import)
        self.comboBox_export = QtGui.QComboBox(self.layoutWidget1)
        self.comboBox_export.setMinimumSize(QtCore.QSize(115, 0))
        self.comboBox_export.setObjectName(_fromUtf8("comboBox_export"))
        self.comboBox_export.addItem(_fromUtf8(""))
        self.comboBox_export.addItem(_fromUtf8(""))
        self.comboBox_export.addItem(_fromUtf8(""))
        self.comboBox_export.addItem(_fromUtf8(""))
        self.verticalLayout_3.addWidget(self.comboBox_export)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.verticalLayout_6.addWidget(self.splitter)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButton_preferences = QtGui.QPushButton(Dialog)
        self.pushButton_preferences.setObjectName(_fromUtf8("pushButton_preferences"))
        self.horizontalLayout_2.addWidget(self.pushButton_preferences)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Setup Dialog for Tinker Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_addRow.setText(QtGui.QApplication.translate("Dialog", "Add Row", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_removeRow.setText(QtGui.QApplication.translate("Dialog", "Remove Row", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_synced_group_weight.setText(QtGui.QApplication.translate("Dialog", "Sync weights within each group", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Reference Step Size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "MASAR ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Config Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_import.setText(QtGui.QApplication.translate("Dialog", "Import from", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_export.setText(QtGui.QApplication.translate("Dialog", "Export to", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(0, QtGui.QApplication.translate("Dialog", "Channel Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(1, QtGui.QApplication.translate("Dialog", "Database", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(2, QtGui.QApplication.translate("Dialog", "Loaded Snapshot", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(3, QtGui.QApplication.translate("Dialog", "HDF5 File", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(4, QtGui.QApplication.translate("Dialog", "JSON File", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_import.setItemText(5, QtGui.QApplication.translate("Dialog", "Text File", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_export.setItemText(0, QtGui.QApplication.translate("Dialog", "Database", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_export.setItemText(1, QtGui.QApplication.translate("Dialog", "HDF5 File", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_export.setItemText(2, QtGui.QApplication.translate("Dialog", "JSON File", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_export.setItemText(3, QtGui.QApplication.translate("Dialog", "Text File", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_preferences.setText(QtGui.QApplication.translate("Dialog", "Preferences", None, QtGui.QApplication.UnicodeUTF8))

