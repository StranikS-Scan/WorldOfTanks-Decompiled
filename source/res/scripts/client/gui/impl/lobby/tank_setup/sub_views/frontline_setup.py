# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/frontline_setup.py
from gui.game_control.epic_meta_game_ctrl import EpicBattleScreens
from gui.impl.lobby.tank_setup.configurations.epic_battle_ability import EpicBattleTabsController, EpicBattleDealPanel
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEpicBattleMetaGameController
from CurrentVehicle import g_currentVehicle
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons, EpicBattleLogAdditionalInfo
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger

class EpicBattleSetupSubView(BaseEquipmentSetupSubView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__currentCategory', '__tooltipMgr', '__uiEpicBattleLogger')

    def __init__(self, viewModel, interactor):
        super(EpicBattleSetupSubView, self).__init__(viewModel, interactor)
        self.__currentCategory = ''
        self.__tooltipMgr = None
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()
        app = self._appLoader.getApp()
        if app is not None:
            self.__tooltipMgr = app.getToolTipMgr()
        with self._viewModel.transaction() as vm:
            vehicle = g_currentVehicle.item
            vm.setVehicleType(vehicle.type)
            vm.setIsTypeSelected(False)
        return

    def onLoading(self, currentSlotID, *args, **kwargs):
        super(EpicBattleSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.OPEN.value, item=EpicBattleLogKeys.SETUP_VIEW.value, parentScreen=EpicBattleLogKeys.HANGAR.value)
        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.SETUP_VIEW.value)

    def finalize(self):
        super(EpicBattleSetupSubView, self).finalize()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLOSE.value, item=EpicBattleLogKeys.SETUP_VIEW.value, parentScreen=EpicBattleLogKeys.HANGAR.value)
        self.__uiEpicBattleLogger.reset()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        self._viewModel.setIsLocked(self.__hasBattleAbilities())
        super(EpicBattleSetupSubView, self).updateSlots(slotID, True, updateData)
        slot = first(self._viewModel.getSlots())
        itemCategory = slot.getCategory() if slot is not None else ''
        if self.__currentCategory != itemCategory:
            self.__currentCategory = itemCategory
            self._viewModel.setSelectedCategory(itemCategory)
        return

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    def _onDealConfirmed(self, _=None):
        super(EpicBattleSetupSubView, self)._onDealConfirmed(_)
        info = EpicBattleLogAdditionalInfo.APPLY_TO_CLASS.value if self._viewModel.getIsTypeSelected() else EpicBattleLogAdditionalInfo.APPLY_TO_VEHICLE.value
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CONFIRM.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value, info=info)

    def _onDealCancelled(self, _=None):
        super(EpicBattleSetupSubView, self)._onDealCancelled(_)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CANCEL.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def _createTabsController(self):
        return EpicBattleTabsController()

    def _getDealPanel(self):
        return EpicBattleDealPanel

    def _addListeners(self):
        super(EpicBattleSetupSubView, self)._addListeners()
        self._viewModel.showBattleAbilitiesSetup += self.__showBattleAbilitiesSetup
        self._viewModel.onChangeApplyAbilitiesToTypeSettings += self.__onChangeApplyAbilitiesToTypeSettings

    def _removeListeners(self):
        self._viewModel.showBattleAbilitiesSetup -= self.__showBattleAbilitiesSetup
        self._viewModel.onChangeApplyAbilitiesToTypeSettings -= self.__onChangeApplyAbilitiesToTypeSettings
        super(EpicBattleSetupSubView, self)._removeListeners()

    def __onChangeApplyAbilitiesToTypeSettings(self, *_):
        state = not self._viewModel.getIsTypeSelected()
        self._interactor.setCheckboxState(state)
        self._viewModel.setIsTypeSelected(state)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CHECKBOX.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def __showBattleAbilitiesSetup(self, *_):
        self.__epicController.showCustomScreen(EpicBattleScreens.RESERVES)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.RESERVES.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def __hasBattleAbilities(self):
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED))
