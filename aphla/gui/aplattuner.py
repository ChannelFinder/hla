#! /usr/bin/env python
'''
TODO
*) Select all channels by default after apchx search finishes in config setup
*) Double-click an array item, then open an array dialog with list of array
   elements (together with its plot on the side, if the array is a number list,
   not a string list)
*) Open dialog to select which columns to save when saving config/snapshot file.
*) Weight & Step Size should be NaN for all the channels that do not have
   pvsp.
*) allow customize significant digits for display and saving in text format
*) being able to set the wait time (< 1 sec) between the time SP sent from PC
and the time caget() sent to all relevant PV's for updating.

*) Open dialog at start-up to allow user either create a new config
or open existing configs
*) Use Qt Undo Framework for non-EPICS commands
*) Use UNION like the following to combine server & client database:
SELECT uid, name FROM DB1.Users UNION SELECT uid, name FROM DB2.Users ;
*) Allow simultaneous weight change within a group if the weight cell on
group level is in edit mode. Only when all the weights in a group are
the same, show group-level weight value.
*) Do not allow (show) group-level step size cell at any time.
'''

"""

GUI application for adjusting lattice parameters with certain ratios
between different groups of parameters.

:author: Yoshiteru Hidaka
:license:

This GUI application is a lattice turning program that allows a user to
define a set of lattice devices to be simultaneously adjusted with
certain step size ratios between them.

"""

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)


import sys, os
from subprocess import Popen, PIPE
from time import time, strftime, localtime
from math import floor
from copy import copy
import types
import numpy as np

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (QObject, QSize, SIGNAL, Qt, QEvent, QRect)
from PyQt4.QtGui import (
    QApplication, QMainWindow, QStandardItemModel, QStandardItem, QDockWidget,
    QWidget, QGridLayout, QSplitter, QTreeView, QTableView, QTabWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QCheckBox,
    QLineEdit, QLabel, QTextEdit, QAction, QSortFilterProxyModel,
    QAbstractItemView, QMenu, QComboBox, QStackedWidget, QActionGroup, QIcon,
    QKeySequence, QCursor, QToolButton, QStyle)

from cothread.catools import caget, caput, camonitor, FORMAT_TIME

from Qt4Designer_files.ui_lattice_tuner_for_reference import Ui_MainWindow

import aphla.gui.utils.gui_icons
import TunerUtils.config as const
from TunerUtils import tunerConfigSetupDialog as TunerConfigSetupDialog
from TunerUtils.tunerModels import (
    TreeItem, TreeModel, TunerConfigSetupBaseModel, TunerConfigSetupTableModel,
    TunerConfigSetupTreeModel, TunerSnapshotBaseModel, TunerSnapshotTableModel,
    TunerSnapshotTreeModel)

import aphla as ap
if ap.machines._lat is None:
    ap.machines.load('nsls2', use_cache=False)

#----------------------------------------------------------------------
def datestr(time_in_seconds_from_Epoch):
    """"""

    frac_sec = time_in_seconds_from_Epoch - floor(time_in_seconds_from_Epoch)
    time_format = '%Y-%m-%d (%a) %H:%M:%S.' + str(frac_sec)[2:]

    return strftime(time_format, localtime(time_in_seconds_from_Epoch))



#########################################################################
#class TunerConfigModelOld(AbstractTunerConfigModel):
    #""""""

    ##----------------------------------------------------------------------
    #def __init__(self, config_dict=None):
        #"""Constructor"""

        #AbstractTunerConfigModel.__init__(self,config_dict=config_dict,
                                          #col_name_list=const.ALL_COL_NAMES)
        ##AbstractTunerConfigModel.__init__(self,config_dict=config_dict,
                                          ##col_name_list=const.DEFAULT_VISIBLE_COL_LIST_FOR_CONFIG_VIEW)

        #self.username = getusername()
        #self.time_created = time() # current time in seconds from Epoch

        #if len(self.channel_group_list) == 0:
            #self.ref_channel_group = {'name:':'', 'weight':0., 'channel_name_list':[]}
        #else:
            #self.ref_channel_group = self.channel_group_list[0]

        #self.ref_step_size = 0.

        #self.update_normalized_weight_list()

        #self.update_step_size_list()

        #self._get_channel_name_flat_list()

        #self._get_pv_flat_list()

        #self._update_pv_values()

        #self._init_RB = self._current_RB[:]
        #self._init_SP = self._current_SP[:]
        #self._init_RB_time = self._current_RB_time[:]
        #self._init_SP_time = self._current_SP_time[:]

        #self._target_SP = self._init_SP[:]

        #self._update_derived_pv_values()

        #self._update_model()

    ##----------------------------------------------------------------------
    #def _update_model(self):
        #""""""

        #self.updateGroupBasedModel()



    ##----------------------------------------------------------------------
    #def _update_pv_values(self):
        #""""""

        #pv_results = caget(self._pv_flat_list,format=FORMAT_TIME)
        #pvrb_results = pv_results[:len(self._pvrb_flat_list)]
        #pvsp_results = pv_results[len(self._pvrb_flat_list):]

        ##compact_current_RB = np.array([(p.real,p.timestamp) for p in pvrb_results])
        ##compact_current_SP = np.array([(p.real,p.timestamp) for p in pvsp_results])

        ##self._current_RB = np.array([float('NaN') for c in self._all_channel_name_flat_list])
        ##for (ind,val_and_timestamp) in zip(self._pvrb_nonempty_ind_list, compact_current_RB):
            ##self._current_RB[ind] = val_and_timestamp

        #pvrb_dict_keys = self._pvrb_dict.keys()
        #self._current_RB = np.array([pvrb_results[self._pvrb_dict[c]].real
                                     #if c in pvrb_dict_keys
                                     #else float('NaN')
                                     #for c in self._all_channel_name_flat_list])
        #self._current_RB_time = np.array([pvrb_results[self._pvrb_dict[c]].timestamp
                                          #if c in pvrb_dict_keys
                                          #else float('NaN')
                                          #for c in self._all_channel_name_flat_list])

        #pvsp_dict_keys = self._pvsp_dict.keys()
        #self._current_SP = np.array([pvsp_results[self._pvsp_dict[c]].real
                                     #if c in pvsp_dict_keys
                                     #else float('NaN')
                                     #for c in self._all_channel_name_flat_list])
        #self._current_SP_time = np.array([pvsp_results[self._pvsp_dict[c]].timestamp
                                          #if c in pvsp_dict_keys
                                          #else float('NaN')
                                          #for c in self._all_channel_name_flat_list])

    ##----------------------------------------------------------------------
    #def _update_derived_pv_values(self):
        #""""""

        #self._D_target_SP_current_SP = self._target_SP - self._current_SP
        #self._D_current_RB_init_RB = self._current_RB - self._init_RB
        #self._D_current_SP_init_SP = self._current_SP - self._init_SP
        #self._D_current_RB_current_SP = self._current_RB - self._current_SP


    ##----------------------------------------------------------------------
    #def update_normalized_weight_list(self):
        #""""""

        #weight_list = [cg['weight'] for cg in self.channel_group_list]

        #ref_weight = self.ref_channel_group['weight']

        #if (ref_weight == 0.) or (ref_weight == float('NaN')):
            #self.normalized_weight_list = [float('NaN') for w in weight_list]
        #else:
            #self.normalized_weight_list = [w/ref_weight for w in weight_list]



    ##----------------------------------------------------------------------
    #def update_step_size_list(self):
        #""""""

        #self.step_size_list = [self.ref_step_size*nw for nw in self.normalized_weight_list]


    ##----------------------------------------------------------------------
    #def _get_channel_name_flat_list(self):
        #""""""

        #self._all_channel_name_flat_list = []
        #for g in self.channel_group_list:
            #self._all_channel_name_flat_list.extend(g['channel_name_list'])

    ##----------------------------------------------------------------------
    #def _get_pv_flat_list(self):
        #""""""

        #self._pvrb_flat_list = []
        ##self._pvrb_nonempty_ind_list = []
        #self._pvrb_dict = {}
        #self._pvsp_flat_list = []
        ##self._pvsp_nonempty_ind_list = []
        #self._pvsp_dict = {}
        #for (i,ch) in enumerate(self._all_channel_name_flat_list):
            #elemName, fieldName = ch.split('.')
            #elem = ap.getElements(elemName)[0]
            #pv = elem.pv(field=fieldName,handle='readback')
            #if len(pv) == 1:
                #self._pvrb_flat_list.append(pv[0])
                ##self._pvrb_nonempty_ind_list.append(i)
                #self._pvrb_dict[ch] = len(self._pvrb_flat_list)-1
            #elif len(pv) == 0:
                #pass
            #else:
                #raise ValueError("Multiple pv's found for readback: "+str(pv))
            #pv = elem.pv(field=fieldName,handle='setpoint')
            #if len(pv) == 1:
                #self._pvsp_flat_list.append(pv[0])
                ##self._pvsp_nonempty_ind_list.append(i)
                #self._pvsp_dict[ch] = len(self._pvsp_flat_list)-1
            #elif len(pv) == 0:
                #pass
            #else:
                #raise ValueError("Multiple pv's found for setpoint: "+str(pv))

        #self._pv_flat_list = self._pvrb_flat_list + self._pvsp_flat_list



########################################################################
class TunerSnapshotModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_base_model, settings=None):
        """Constructor"""

        QObject.__init__(self)

        self.settings = settings

        self.base_model = TunerSnapshotBaseModel(config_base_model)
        self.table_model = TunerSnapshotTableModel(
            base_model=self.base_model)
        self.tree_model = TunerSnapshotTreeModel(
            self.base_model.all_col_name_list, base_model=self.base_model)

        # Metadata
        self.time_snapshot_taken = time() # current time in seconds from Epoch



        self.all_channel_name_flat_list = []
        self.pvrb_values = [] #[(val1,timestamp1),(val2,timestamp2)] # in the order of flat channel list
        self.pvsp_values = [] #[(val1,timestamp1),(val2,timestamp2)]


########################################################################
class TitleRenameLineEdit(QLineEdit):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""

        QLineEdit.__init__(self, parent)

        self.connect(self, SIGNAL('editingFinished()'),
                     self.finalizeText)

        self.setWindowFlags(Qt.CustomizeWindowHint)

        self.hide()

    #----------------------------------------------------------------------
    def setText(self, text):
        """"""

        QLineEdit.setText(self, text)
        title_label = self.parent().title
        label_rect = title_label.geometry()
        w = self.fontMetrics().width(text+'extra')
        h = self.fontMetrics().height()*2
        self.setGeometry(QRect(0,label_rect.y(),w,h))
        self.setFocus()
        self.selectAll()
        self.show()

    #----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """"""

        if (event.key() == Qt.Key_Escape):
            QLineEdit.setText(self, '')
            self.hide()
        else:
            QLineEdit.keyPressEvent(self, event)

    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""

        QLineEdit.focusOutEvent(self, event)

        self.emit(SIGNAL('editingFinished()'))

    #----------------------------------------------------------------------
    def finalizeText(self):
        """"""

        if self.text() != '':
            self.parent().title.setText(self.text())

        self.hide()

        self.emit(SIGNAL('dockTitleChangeFinalized'))


########################################################################
class TitleLabel(QLabel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QLabel.__init__(self, *args)

        self._editor = TitleRenameLineEdit(self.parent())
        self.connect(self._editor, SIGNAL('dockTitleChangeFinalized'),
                     self.emitTitleChangedSignal)

    #----------------------------------------------------------------------
    def emitTitleChangedSignal(self):
        """"""

        self.emit(SIGNAL('dockTitleChanged'))

    #----------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """"""

        self.edit()

        event.accept()

    #----------------------------------------------------------------------
    def edit(self):
        """"""

        self._editor.setText(self.text())

########################################################################
class CustomDockWidgetTitleBar(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentDockWidget):
        """Constructor"""

        QWidget.__init__(self, parentDockWidget)

        self.dockWidget = parentDockWidget

        self.title = TitleLabel(self)
        self.title.setText('untitled')
        self.connect(self.title, SIGNAL('dockTitleChanged'),
                     self._emitTitleChangeSignal)

        min_button_height = 10

        self.minimizeButton = QToolButton(self)
        #self.minimizeButton.setIcon(QIcon(':/up_arrow.png'))
        self.minimizeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarMinButton) )
        self.minimizeButton.setToolTip('Minimize')
        self.minimizeButton.setMinimumHeight(min_button_height)
        #
        self.maximizeButton = QToolButton(self)
        self.maximizeButton.setToolTip('Maximize')
        self.maximizeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarMaxButton) )
        self.maximizeButton.setMinimumHeight(min_button_height)
        #
        self.restoreButton = QToolButton(self)
        self.restoreButton.setToolTip('Restore')
        self.restoreButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.restoreButton.setMinimumHeight(min_button_height)
        #
        self.undockButton = QToolButton(self)
        self.undockButton.setToolTip('Undock')
        self.undockButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.undockButton.setMinimumHeight(min_button_height)
        #
        self.dockButton = QToolButton(self)
        self.dockButton.setToolTip('Dock')
        self.dockButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.dockButton.setMinimumHeight(min_button_height)
        #
        self.closeButton = QToolButton(self)
        self.closeButton.setToolTip('Close')
        self.closeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarCloseButton) )
        self.closeButton.setMinimumHeight(min_button_height)

        self.connect(self.minimizeButton,SIGNAL('clicked()'),
                     self.minimizeDockWidget)
        self.connect(self.maximizeButton,SIGNAL('clicked()'),
                     self.maximizeDockWidget)
        self.connect(self.restoreButton,SIGNAL('clicked()'),
                     self.restoreDockWidget)
        self.connect(self.undockButton,SIGNAL('clicked()'),
                     self.undockDockWidget)
        self.connect(self.dockButton,SIGNAL('clicked()'),
                     self.dockDockWidget)
        self.connect(self.closeButton,SIGNAL('clicked()'),
                     self.closeDockWidget)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        hbox = QHBoxLayout(self)
        #
        hbox.addWidget(self.title)
        hbox.addWidget(self.minimizeButton)
        hbox.addWidget(self.restoreButton)
        hbox.addWidget(self.maximizeButton)
        hbox.addWidget(self.undockButton)
        hbox.addWidget(self.dockButton)
        hbox.addWidget(self.closeButton)
        #
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)

        self.window_state = Qt.WindowNoState
        self.float_state = False
        self.updateButtons()

        self.connect(self.dockWidget,
                     SIGNAL('topLevelChanged(bool)'),
                     self.updateButtons)

    #----------------------------------------------------------------------
    def renameTitle(self):
        """"""

        self.title.edit()

    #----------------------------------------------------------------------
    def _emitTitleChangeSignal(self):
        """"""
        self.emit(SIGNAL('customDockTitleChanged'))

    #----------------------------------------------------------------------
    def updateButtons(self, floating=None):
        """"""

        if floating is None:
            floating = self.dockWidget.isFloating()

        if floating:
            self.dockButton.show()
            self.undockButton.hide()
            self.minimizeButton.show()
            if self.window_state == Qt.WindowMaximized:
                self.restoreButton.show()
                self.maximizeButton.hide()
            else:
                self.restoreButton.hide()
                self.maximizeButton.show()
        else:
            self.dockButton.hide()
            self.undockButton.show()
            self.minimizeButton.hide()
            self.restoreButton.hide()
            self.maximizeButton.hide()

    #----------------------------------------------------------------------
    def minimizeDockWidget(self):
        """"""

        if self.dockWidget.windowState() not in (Qt.WindowNoState,
                                                 Qt.WindowMaximized,
                                                 Qt.WindowFullScreen,
                                                 Qt.WindowActive):
            self.dockWidget.setWindowState(Qt.WindowActive)
        '''This section is needed because when the dockWidget is undocked by
        dragging, the window state is somehow set to WindowMinimized,
        even though the window is floating WITHOUT being minimized.
        Therefore, nothing happens when minimize button is pressed.
        So, the window state must be changed to something other than
        WindowMinimized for the minimization process to happen. Here,
        WindowActive state is being used for that purpose.
        '''

        self.dockWidget.showMinimized()
        ## or
        #self.dockWidget.setWindowState(Qt.WindowMinimized)

        self.window_state = Qt.WindowMinimized
        self.updateButtons()

    #----------------------------------------------------------------------
    def maximizeDockWidget(self):
        """"""

        self.dockWidget.showMaximized()

        self.window_state = Qt.WindowMaximized
        self.updateButtons()

    #----------------------------------------------------------------------
    def restoreDockWidget(self):
        """"""

        self.dockWidget.showNormal()

        self.window_state = Qt.WindowNoState
        self.updateButtons()

    #----------------------------------------------------------------------
    def undockDockWidget(self):
        """"""

        self.dockWidget.setFloating(True)

        self.updateButtons()

    #----------------------------------------------------------------------
    def dockDockWidget(self):
        """"""

        self.dockWidget.setFloating(False)

        self.updateButtons()

    #----------------------------------------------------------------------
    def closeDockWidget(self):
        """"""
        self.dockWidget.close()


########################################################################
class TunerDockWidget(QDockWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, parent):
        """Constructor"""

        self._initUI(parent)

        self.model = model
        isinstance(model,TunerSnapshotModel)

        # Set up table view
        tbV = self.tableView
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.model.table_model)
        proxyModel.setDynamicSortFilter(False)
        tbV.setModel(proxyModel)
        tbV.setCornerButtonEnabled(True)
        tbV.setShowGrid(True)
        tbV.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tbV.setSelectionBehavior(QAbstractItemView.SelectItems)
        tbV.setAlternatingRowColors(True)
        tbV.setSortingEnabled(False)
        horizHeader = tbV.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)

        # Set up tree view
        trV = self.treeView
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.model.tree_model)
        proxyModel.setDynamicSortFilter(False)
        trV.setModel(proxyModel)
        trV.setItemsExpandable(True)
        trV.setRootIsDecorated(True)
        trV.setAllColumnsShowFocus(True)
        trV.setHeaderHidden(False)
        trV.setSortingEnabled(True)
        trV.setSelectionMode(QAbstractItemView.ExtendedSelection)
        horizHeader = trV.header()
        horizHeader.setSortIndicatorShown(True)
        horizHeader.setStretchLastSection(True)
        horizHeader.setMovable(False)
        self._expandAll_and_resizeColumn()

        self.connect(self.pushButton_step_up,SIGNAL('toggled(bool)'),
                     self.onStepUpPushed)

        self.actionRename = QAction(QIcon(), 'Rename', self)
        self.addRobustShortcut(self.actionRename, Qt.Key_F2)
        self.connect(self.actionRename, SIGNAL('triggered()'),
                     self.renameTitle)
        #
        self.actionViewGroupBased = QAction(QIcon(), 'Group-based', self)
        self.addRobustShortcut(self.actionViewGroupBased,
                               QKeySequence(Qt.ControlModifier + Qt.Key_1))
        self.actionViewGroupBased.setCheckable(True)
        self.actionViewChannelBased = QAction(QIcon(), 'Channel-based', self)
        self.addRobustShortcut(self.actionViewChannelBased,
                               QKeySequence(Qt.ControlModifier + Qt.Key_2))
        self.actionViewChannelBased.setCheckable(True)
        self.actionGroupViewMode = QActionGroup(self) # Action Group for View Mode (Group-based vs. Channel-based)
        self.actionGroupViewMode.setExclusive(True)
        self.actionViewGroupBased.setActionGroup(self.actionGroupViewMode)
        self.actionViewChannelBased.setActionGroup(self.actionGroupViewMode)
        default_action = self.actionViewChannelBased
        default_action.setChecked(True)
        self.onViewModeActionGroupTriggered(default_action)
        self.connect(self.actionGroupViewMode, SIGNAL('triggered(QAction *)'),
                     self.onViewModeActionGroupTriggered)
        self.menuViewMode = QMenu('View Mode')
        self.menuViewMode.addAction(self.actionViewGroupBased)
        self.menuViewMode.addAction(self.actionViewChannelBased)
        #
        self.actionColumns = QAction(QIcon(), 'Columns...', self)
        self.connect(self.actionColumns, SIGNAL('triggered()'),
                     self.launchColumnSelector)
        #
        self.actionStepMode = QAction(QIcon(), 'Step Mode', self)
        self.actionStepMode.setCheckable(True)
        self.actionStepMode.setChecked(True)
        self.connect(self.actionStepMode, SIGNAL('triggered()'),
                     self.showStepModeTab)
        self.actionRampMode = QAction(QIcon(), 'Ramp Mode', self)
        self.actionRampMode.setCheckable(True)
        self.actionRampMode.setChecked(True)
        self.connect(self.actionRampMode, SIGNAL('triggered()'),
                     self.showRampModeTab)
        #
        self.actionConfigMetadata = QAction(QIcon(), 'Config Metadata', self)
        self.actionConfigMetadata.setCheckable(True)
        self.actionConfigMetadata.setChecked(True)
        self.connect(self.actionConfigMetadata, SIGNAL('triggered()'),
                     self.showConfigMetaTab)
        self.actionSnapshotMetadata = QAction(QIcon(), 'Snapshot Metadata', self)
        self.actionSnapshotMetadata.setCheckable(True)
        self.actionSnapshotMetadata.setChecked(True)
        self.connect(self.actionSnapshotMetadata, SIGNAL('triggered()'),
                     self.showSnapshotMetaTab)
        #
        self.actionTakeSnapshot = QAction(QIcon(), '&Take snapshot...', self)
        self.addRobustShortcut(self.actionTakeSnapshot,
                               QKeySequence(Qt.ControlModifier + Qt.Key_T))
        self.connect(self.actionTakeSnapshot, SIGNAL('triggered()'), self.takeSnapshot)
        #
        self.actionSaveAs = QAction(QIcon(), '&Save as...', self)
        self.addRobustShortcut(self.actionSaveAs,
                               QKeySequence(Qt.ControlModifier + Qt.Key_S))
        self.connect(self.actionSaveAs, SIGNAL('triggered()'), self.saveAs)
        #
        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.actionRename)
        self.contextMenu.addSeparator()
        self.contextMenu.addMenu(self.menuViewMode)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionColumns)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionStepMode)
        self.contextMenu.addAction(self.actionRampMode)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionConfigMetadata)
        self.contextMenu.addAction(self.actionSnapshotMetadata)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionTakeSnapshot)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionSaveAs)
        #
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)

        self.customTitleBar = CustomDockWidgetTitleBar(self)
        self.setTitleBarWidget(self.customTitleBar)
        self.connect(self.customTitleBar, SIGNAL('customDockTitleChanged'),
                     self._updateWindowTitle)

    #----------------------------------------------------------------------
    def _updateWindowTitle(self):
        """
        As the built-in window title does not get automatically changed,
        when the custom window title is changed, this update is being
        performed in this function.
        """

        # This title appears at the top of the dock either when docked,
        # tabified, or floated. And this is editable.
        dock_title = self.customTitleBar.title.text()

        # This tile appears at the bottom of the dock tab only when more than
        # one docks are tabified. And this is not editable.
        self.setWindowTitle(dock_title)

        self.update()

        print 'Updating window title'

    #----------------------------------------------------------------------
    def onViewModeActionGroupTriggered(self, action):
        """"""

        self.showMinimized()

        if action == self.actionViewChannelBased:
            self.stackedWidget.setCurrentWidget(self.page_table)
        elif action == self.actionViewGroupBased:
            self.stackedWidget.setCurrentWidget(self.page_tree)
        else:
            raise ValueError('Unexpected action:'+str(action))

    #----------------------------------------------------------------------
    def addRobustShortcut(self, action, shortcut_key):
        """"""

        action.setShortcut(shortcut_key)

        if action not in self.actions():
            self.addAction(action)
        ''' This addAction is critical for the shortcut to always work for
        context menus. For the shortcut to work, the widget to which
        the desired action is added must be listening for key events.

        '''

    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""

        self.contextMenu.exec_(QCursor.pos())

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        event.accept()

    #----------------------------------------------------------------------
    def _initUI(self, parent):
        """"""

        QDockWidget.__init__(self, parent)

        dockWidgetContents = QWidget()
        top_gridLayout = QGridLayout(dockWidgetContents)
        #
        self.splitter = QSplitter(dockWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        #
        self.stackedWidget = QStackedWidget(self.splitter)
        #
        self.page_tree = QWidget()
        gridLayout = QGridLayout(self.page_tree)
        self.treeView = QTreeView(self.page_tree)
        gridLayout.addWidget(self.treeView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_tree)
        #
        self.page_table = QWidget()
        gridLayout = QGridLayout(self.page_table)
        self.tableView = QTableView(self.page_table)
        gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_table)

        ##
        self.tabWidget_mode = QTabWidget(self.splitter)
        #
        self.tab_step_mode = QWidget()
        verticalLayout_1 = QVBoxLayout(self.tab_step_mode)
        horizontalLayout_1 = QHBoxLayout()
        self.pushButton_step_up = QPushButton(self.tab_step_mode)
        self.pushButton_step_up.setText('Up')
        horizontalLayout_1.addWidget(self.pushButton_step_up)
        self.pushButton_step_down = QPushButton(self.tab_step_mode)
        self.pushButton_step_down.setText('Down')
        horizontalLayout_1.addWidget(self.pushButton_step_down)
        spacerItem_1 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_1.addItem(spacerItem_1)
        verticalLayout_1.addLayout(horizontalLayout_1)
        horizontalLayout_2 = QHBoxLayout()
        self.pushButton_update = QPushButton(self.tab_step_mode)
        self.pushButton_update.setText('Update')
        horizontalLayout_2.addWidget(self.pushButton_update)
        self.checkBox_auto = QCheckBox(self.tab_step_mode)
        self.checkBox_auto.setMinimumSize(QSize(141,0))
        self.checkBox_auto.setText('Auto: Interval [s]')
        horizontalLayout_2.addWidget(self.checkBox_auto)
        self.lineEdit_auto_update_interval = QLineEdit(self.tab_step_mode)
        horizontalLayout_2.addWidget(self.lineEdit_auto_update_interval)
        spacerItem_2 = QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_2.addItem(spacerItem_2)
        verticalLayout_1.addLayout(horizontalLayout_2)
        self.tabWidget_mode.addTab(self.tab_step_mode,'Step Mode')
        #
        self.tab_ramp_mode = QWidget()
        horizontalLayout_10 = QHBoxLayout(self.tab_ramp_mode)
        verticalLayout_tab_ramp_1 = QVBoxLayout()
        horizontalLayout_tab_ramp_2 = QHBoxLayout()
        self.pushButton_copy = QPushButton(self.tab_ramp_mode)
        self.pushButton_copy.setText('Copy')
        horizontalLayout_tab_ramp_2.addWidget(self.pushButton_copy)
        self.comboBox_setpoint_copy_source = QComboBox(self.tab_ramp_mode)
        self.comboBox_setpoint_copy_source.addItem('Current')
        self.comboBox_setpoint_copy_source.addItem('Initial')
        self.comboBox_setpoint_copy_source.addItem('Snapshot')
        horizontalLayout_tab_ramp_2.addWidget(self.comboBox_setpoint_copy_source)
        label_tab_ramp_3 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_3.setText('setpoints into target setpoints')
        horizontalLayout_tab_ramp_2.addWidget(label_tab_ramp_3)
        spacerItem = QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_tab_ramp_2.addItem(spacerItem)
        verticalLayout_tab_ramp_1.addLayout(horizontalLayout_tab_ramp_2)
        horizontalLayout_tab_ramp_1 = QHBoxLayout()
        label_tab_ramp_1 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_1.setText('Number of Steps:')
        horizontalLayout_tab_ramp_1.addWidget(label_tab_ramp_1)
        self.lineEdit_nSteps = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_tab_ramp_1.addWidget(self.lineEdit_nSteps)
        label_tab_ramp_2 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_2.setText('Wait after Each Step [s]:')
        horizontalLayout_tab_ramp_1.addWidget(label_tab_ramp_2)
        self.lineEdit_wait_after_each_step = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_tab_ramp_1.addWidget(self.lineEdit_wait_after_each_step)
        verticalLayout_tab_ramp_1.addLayout(horizontalLayout_tab_ramp_1)
        horizontalLayout_10.addLayout(verticalLayout_tab_ramp_1)
        self.pushButton_start = QPushButton(self.tab_ramp_mode)
        self.pushButton_start.setText('Start')
        horizontalLayout_10.addWidget(self.pushButton_start)
        self.pushButton_stop = QPushButton(self.tab_ramp_mode)
        self.pushButton_stop.setText('Stop')
        horizontalLayout_10.addWidget(self.pushButton_stop)
        self.pushButton_revert = QPushButton(self.tab_ramp_mode)
        self.pushButton_revert.setText('Revert')
        horizontalLayout_10.addWidget(self.pushButton_revert)
        spacerItem = QSpacerItem(137,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_10.addItem(spacerItem)
        self.tabWidget_mode.addTab(self.tab_ramp_mode,'Ramp Mode')

        ##
        self.tabWidget_metadata = QTabWidget(self.splitter)
        #
        self.tab_config_metadata = QWidget()
        verticalLayout_21 = QVBoxLayout(self.tab_config_metadata)
        horizontalLayout_21 = QHBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('Created by')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_username = QLineEdit(self.tab_config_metadata)
        horizontalLayout_21.addWidget(self.lineEdit_config_username)
        label = QLabel(self.tab_config_metadata)
        label.setText('Created on')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_timestamp = QLineEdit(self.tab_config_metadata)
        horizontalLayout_21.addWidget(self.lineEdit_config_timestamp)
        spacerItem_5 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_21.addItem(spacerItem_5)
        verticalLayout_21.addLayout(horizontalLayout_21)
        horizontalLayout_22 = QHBoxLayout()
        verticalLayout_22 = QVBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('Description')
        verticalLayout_22.addWidget(label)
        spacerItem_6 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        verticalLayout_22.addItem(spacerItem_6)
        horizontalLayout_22.addLayout(verticalLayout_22)
        self.textEdit_config_description = QTextEdit(self.tab_config_metadata)
        horizontalLayout_22.addWidget(self.textEdit_config_description)
        verticalLayout_21.addLayout(horizontalLayout_22)
        self.tabWidget_metadata.addTab(self.tab_config_metadata,'Config Metadata')
        #
        self.tab_snapshot_metadata = QWidget()
        verticalLayout_31 = QVBoxLayout(self.tab_snapshot_metadata)
        horizontalLayout_31 = QHBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created by')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_username = QLineEdit(self.tab_snapshot_metadata)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_username)
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created on')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_timestamp = QLineEdit(self.tab_snapshot_metadata)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_timestamp)
        spacerItem_7 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_31.addItem(spacerItem_7)
        verticalLayout_31.addLayout(horizontalLayout_31)
        horizontalLayout_32 = QHBoxLayout()
        verticalLayout_32 = QVBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Description')
        verticalLayout_32.addWidget(label)
        spacerItem_8 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        verticalLayout_32.addItem(spacerItem_8)
        horizontalLayout_32.addLayout(verticalLayout_32)
        self.textEdit_snapshot_description = QTextEdit(self.tab_snapshot_metadata)
        horizontalLayout_32.addWidget(self.textEdit_snapshot_description)
        verticalLayout_31.addLayout(horizontalLayout_32)
        self.tabWidget_metadata.addTab(self.tab_snapshot_metadata,'Snapshot Metadata')

        top_gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.setWidget(dockWidgetContents)


    #----------------------------------------------------------------------
    def onStepUpPushed(self, garbage):
        """"""

        self.emit(SIGNAL('stepUpPushed'))


    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self):
        """"""

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

    #----------------------------------------------------------------------
    def renameTitle(self):
        """"""

        self.titleBarWidget().renameTitle()

    #----------------------------------------------------------------------
    def launchColumnSelector(self):
        """"""

        pass

    #----------------------------------------------------------------------
    def showStepModeTab(self):
        """"""
        pass
    #----------------------------------------------------------------------
    def showRampModeTab(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def showConfigMetaTab(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def showSnapshotMetaTab(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def takeSnapshot(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def saveAs(self):
        """"""
        pass



########################################################################
class TunerModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.model_list = [] # A list of TunerSnapshotModel objects

    #----------------------------------------------------------------------
    def createNewConfig(self, config_dict):
        """"""

        newConfigModel = TunerConfigModel(config_name=config_dict['config_name'],
            description=config_dict['description'],channel_group_list=[],
            col_name_list=[])

        self.model_list.append(newConfigModel)

        self.emit(SIGNAL('newConfigModelCreated'),newConfigModel)

    #----------------------------------------------------------------------
    def addNewSnapshotModel(self, config_base_model):
        """"""

        if config_base_model is None:
            return

        new_snapshot_model = TunerSnapshotModel(config_base_model)

        self.model_list.append(new_snapshot_model)

        index = len(self.model_list)-1
        self.emit(SIGNAL('newSnapshotModelAdded'), index)


########################################################################
class TunerView(QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model):
        """Constructor"""

        QMainWindow.__init__(self)

        self.model = model

        self.setupUi(self)
        self.dockWidget_example.deleteLater()

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralWidget().hide()

        self.setDockNestingEnabled(True)

        tab_position = QTabWidget.South
        self.setTabPosition(QtCore.Qt.TopDockWidgetArea, tab_position)
        self.setTabPosition(QtCore.Qt.BottomDockWidgetArea, tab_position)
        self.setTabPosition(QtCore.Qt.RightDockWidgetArea, tab_position)
        self.setTabPosition(QtCore.Qt.LeftDockWidgetArea, tab_position)

        self.configDockWidgetList = []

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)

    #----------------------------------------------------------------------
    def openContextMenu(self):
        """
        Default context menu would show nothing if no dockwidget has been
        created yet. However, once a dockwidget is created, it will show
        the list of dockwidgets to allow users to show/hide dockwidgets.

        Instead of this default context menu, a custom context menu will be shown.
        """

        pass

    #----------------------------------------------------------------------
    def createTunerDockWidget(self, index):
        """"""

        snapshot_model = self.model.model_list[index]
        base_model = snapshot_model.base_model

        isinstance(snapshot_model,TunerSnapshotModel)
        isinstance(base_model,TunerConfigSetupBaseModel)

        dockWidget = TunerDockWidget(snapshot_model, self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), dockWidget)

        dockWidget.lineEdit_config_username.setReadOnly(True)
        dockWidget.lineEdit_config_timestamp.setReadOnly(True)
        dockWidget.textEdit_config_description.setReadOnly(True)
        dockWidget.lineEdit_snapshot_username.setReadOnly(True)
        dockWidget.lineEdit_snapshot_timestamp.setReadOnly(True)
        dockWidget.textEdit_snapshot_description.setReadOnly(True)

        self.configDockWidgetList.append(dockWidget)
        dockWidget.setObjectName('configDock'+str(len(self.configDockWidgetList)))

        if base_model.isSnapshot():
            dock_title = base_model.getName('snapshot')
        else:
            dock_title = base_model.getName('config')
        if dock_title == '': dock_title = 'untitled'

        # This tile appears at the bottom of the dock tab only when more than
        # one docks are tabified. And this is not editable.
        dockWidget.setWindowTitle(dock_title)
        # This title appears at the top of the dock either when docked,
        # tabified, or floated. And this is editable.
        dockWidget.customTitleBar.title.setText(dock_title)

        dockWidget.setFloating(False) # Dock the new dockwidget by default
        if len(self.configDockWidgetList) >= 2:
            #self.splitDockWidget(self.configDockWidgetList[-2], dockWidget,
                                 #QtCore.Qt.Horizontal)
            self.tabifyDockWidget(self.configDockWidgetList[-2], dockWidget)
        #dockWidget.raise_()

        dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_table)
        #dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_tree)

        self.updateMetadataTab(dockWidget, base_model, page='config')
        if base_model.isSnapshot():
            self.updateMetadataTab(dockWidget, base_model, page='snapshot')


    #----------------------------------------------------------------------
    def updateMetadataTab(self, dockWidget, base_model, page='config'):
        """"""

        if page not in ('config','snapshot'):
            raise ValueError('"page" argument must be either "config" or "snapshot".')

        dockWidget.lineEdit_config_username.setText(
            base_model.getUserInfo(page)[-1])
        dockWidget.lineEdit_config_timestamp.setText(
            datestr( base_model.getTimeCreated(page) ))
        dockWidget.textEdit_config_description.setText(
            base_model.getDescription(page,include_appended=True)
        )

    #----------------------------------------------------------------------
    def createTunerConfigDockWidget(self, configModel):
        """"""

        dockWidget = TunerDockWidget(configModel, self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), dockWidget)

        self.configDockWidgetList.append(dockWidget)
        dockWidget.setObjectName('configDock'+str(len(self.configDockWidgetList)))
        dockWidget.setWindowTitle(dockWidget.objectName())

        dockWidget.setFloating(False) # Dock the new dockwidget by default
        if len(self.configDockWidgetList) >= 2:
            #self.splitDockWidget(self.configDockWidgetList[-2], dockWidget,
                                 #QtCore.Qt.Horizontal)
            self.tabifyDockWidget(self.configDockWidgetList[-2], dockWidget)
        #dockWidget.raise_()





########################################################################
class TunerApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, use_cached_lattice=False):
        """Constructor"""

        QObject.__init__(self)

        self.use_cached_lattice = use_cached_lattice

        self._initModel()
        self._initView(self.model)

        self.connect(self.view.actionNewConfig,SIGNAL('triggered(bool)'),
                     self.openNewConfigSetupDialog)
        #self.connect(self, SIGNAL('tunerConfigDictLoaded'),
                     #self.model.createNewConfig)
        #self.connect(self.model, SIGNAL('newConfigModelCreated'),
                     #self.view.createTunerConfigDockWidget)
        self.connect(self.model, SIGNAL('newSnapshotModelAdded'),
                     self.view.createTunerDockWidget)

    #----------------------------------------------------------------------
    def _initModel(self):
        """"""

        self.model = TunerModel()

    #----------------------------------------------------------------------
    def _initView(self, model):
        """"""

        self.view = TunerView(model)


    #----------------------------------------------------------------------
    def openNewConfigSetupDialog(self, garbage):
        """"""

        result = TunerConfigSetupDialog.make(
            isModal=True, parentWindow=self.view,
            use_cached_lattice=self.use_cached_lattice)

        config_base_model = result.model.output

        self.model.addNewSnapshotModel(config_base_model)


#----------------------------------------------------------------------
def make(use_cached_lattice=False):
    """"""

    app = TunerApp(use_cached_lattice=use_cached_lattice)
    app.view.show()

    return app

#----------------------------------------------------------------------
def isCothreadUsed():
    """"""

    g = copy(globals())

    using_cothread = False
    for (k,v) in g.iteritems():
        if isinstance(v, types.ModuleType):
            if v.__name__ == 'cothread':
                using_cothread = True
                break

    return using_cothread

#----------------------------------------------------------------------
def main(args):
    """"""

    if len(args) == 2:
        if args[1].lower() == 'true':
            use_cached_lattice = True
        else:
            use_cached_lattice = False

    using_cothread = isCothreadUsed()

    if using_cothread:
        # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
        # before any work is done with Qt. Without this line below, the GUI window will not
        # show up and freeze the program.
        # Note that for a dialog box to be modal, i.e., blocking the application
        # execution until user input is given, you need to set the input
        # argument "user_timer" to be True.
        #cothread.iqt(use_timer = True)
        cothread.iqt()
    else:
        qapp = QApplication(args)


    app = make(use_cached_lattice=use_cached_lattice)

    if using_cothread:
        cothread.WaitForQuit()
    else:
        exit_status = qapp.exec_()
        sys.exit(exit_status)



#----------------------------------------------------------------------
if __name__ == "__main__" :
    main(sys.argv)

