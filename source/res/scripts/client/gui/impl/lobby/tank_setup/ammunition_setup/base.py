# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/base.py
from account_helpers.settings_core.settings_constants import CONTROLS
from async import async, await, await_callback
from BWUtil import AsyncReturn
from frameworks.wulf import ViewStatus
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_setup_view_model import AmmunitionSetupViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.tank_setup_helper import setLastSlotAction
from gui.impl.lobby.tank_setup.tank_setup_sounds import playOptDeviceSlotEnter
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache

class BaseAmmunitionSetupView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_ammunitionPanel', '_tankSetup', '_vehItem')

    def __init__(self, settings):
        super(BaseAmmunitionSetupView, self).__init__(settings)
        self._ammunitionPanel = None
        self._tankSetup = None
        self._vehItem = None
        return

    @property
    def viewModel(self):
        return super(BaseAmmunitionSetupView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self._getBackportTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(BaseAmmunitionSetupView, self).createToolTip(event)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = self._getBackportContextMenuData(event)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(BaseAmmunitionSetupView, self).createContextMenuContent(event)

    def _onLoading(self, **kwargs):
        super(BaseAmmunitionSetupView, self)._onLoading(**kwargs)
        self._vehItem = self._createVehicleItem()
        self._tankSetup = self._createMainTankSetup()
        self._tankSetup.onLoading(**kwargs)
        self._ammunitionPanel = self._createAmmunitionPanel()
        self._ammunitionPanel.onLoading(**kwargs)

    def _initialize(self, *args, **kwargs):
        super(BaseAmmunitionSetupView, self)._initialize()
        self._ammunitionPanel.initialize()
        self._tankSetup.initialize()
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        self._ammunitionPanel.finalize()
        self._tankSetup.finalize()
        self._vehItem = None
        super(BaseAmmunitionSetupView, self)._finalize()
        return

    def _resetVehicleItem(self):
        if self._vehItem is None:
            self._createVehicleItem()
        else:
            self._recreateVehicleItem()
        return

    def _resetVehicleSetups(self):
        if self._vehItem is None:
            self._createVehicleItem()
        else:
            self._recreateVehicleSetups()
        return

    def _createVehicleItem(self):
        raise NotImplementedError

    def _recreateVehicleSetups(self):
        raise NotImplementedError

    def _recreateVehicleItem(self):
        raise NotImplementedError

    def _createMainTankSetup(self):
        raise NotImplementedError

    def _createAmmunitionPanel(self):
        raise NotImplementedError

    def _addListeners(self):
        self._vehItem.onItemUpdated += self._onVehicleItemUpdated
        self._vehItem.onSlotAction += self._onSlotAction
        self.viewModel.onClose += self._onClose
        self.viewModel.ammunitionPanel.onSectionSelect += self._onPanelSelected
        self.viewModel.ammunitionPanel.onSlotClear += self._onPanelSlotClear
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self._onChangeSetupIndex
        self.__settingsCore.onSettingsApplied += self.__onSettingsApplied

    def _removeListeners(self):
        self._vehItem.onItemUpdated -= self._onVehicleItemUpdated
        self._vehItem.onSlotAction -= self._onSlotAction
        self.viewModel.onClose -= self._onClose
        self.viewModel.ammunitionPanel.onSectionSelect -= self._onPanelSelected
        self.viewModel.ammunitionPanel.onSlotClear -= self._onPanelSlotClear
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex
        self.__settingsCore.onSettingsApplied -= self.__onSettingsApplied

    def _getBackportTooltipData(self, event):
        return None

    def _getBackportContextMenuData(self, event):
        return None

    @async
    def _onPanelSelected(self, args):
        sectionName, slotID = args.get('selectedSection'), int(args.get('selectedSlot'))
        if self._vehItem.getItem().isOnlyForEventBattles and sectionName == TankSetupConstants.SHELLS:
            return
        if sectionName:
            switch = yield await(self._tankSetup.switch(sectionName, slotID))
            if switch and self.viewStatus == ViewStatus.LOADED:
                if sectionName == TankSetupConstants.OPT_DEVICES:
                    playOptDeviceSlotEnter(self._vehItem.getItem(), slotID)
                self._ammunitionPanel.changeSelectedSection(sectionName, slotID)
                self._updateAmmunitionPanel()

    def _onPanelSlotClear(self, args):
        slotID = int(args.get('slotId'))
        self._tankSetup.getCurrentSubView().revertItem(slotID)
        self._tankSetup.update()

    @async
    def _doChangeSetupLayoutIndex(self, groupID, layoutIdx):
        changeSetupLayout = True
        self._tankSetup.setLocked(True)
        sections = self._ammunitionPanel.getSectionsByGroup(groupID)
        currentSection = self._tankSetup.getSelectedSetup()
        if sections and currentSection in sections:
            changeSetupLayout = yield await(self._tankSetup.canQuit(skipApplyAutoRenewal=True))
        if changeSetupLayout:
            yield await_callback(self._ammunitionPanel.onChangeSetupLayoutIndex)(groupID, layoutIdx)
        self._tankSetup.setLocked(False)
        if changeSetupLayout:
            self._tankSetup.update()
        raise AsyncReturn(changeSetupLayout)

    def _onChangeSetupIndex(self, args):
        hudGroupID = int(args.get('groupId', None))
        newLayoutIdx = int(args.get('currentIndex', None))
        if hudGroupID is None or newLayoutIdx is None:
            return
        else:
            if self._ammunitionPanel.isNewSetupLayoutIndexValid(hudGroupID, newLayoutIdx):
                self._doChangeSetupLayoutIndex(hudGroupID, newLayoutIdx)
            return

    def _updateAmmunitionPanel(self, sectionName=None):
        if sectionName is None:
            self._ammunitionPanel.update(self._vehItem.getItem())
        else:
            self._ammunitionPanel.updateSection(sectionName)
        return

    def _onVehicleItemUpdated(self, sectionName):
        self._updateAmmunitionPanel(sectionName)

    def _onSlotAction(self, *args, **kwargs):
        setLastSlotAction(self.viewModel, self._vehItem.getItem(), *args, **kwargs)

    def _onClose(self):
        pass

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            self._ammunitionPanel.updateSectionsWithKeySettings()
