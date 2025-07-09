# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/battle_booster_setup.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.tank_setup.configurations.battle_booster import BattleBoostersTabsController, BattleBoosterTabs, BattleBoostersIntroductionController
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView

class BattleBoosterSetupSubView(BaseEquipmentSetupSubView):
    __slots__ = ()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        item = self._interactor.getCurrentLayout()[slotID]
        if item is not None:
            tab = BattleBoosterTabs.OPT_DEVICE
            if item.isCrewBooster():
                tab = BattleBoosterTabs.CREW
            elif item.isEconomicBooster():
                tab = BattleBoosterTabs.ECONOMIC
            self._setTab(tab)
        if item is not None and item.isHidden and not item.isInInventory:
            self._interactor.changeSlotItem(slotID, None)
            self._interactor.getAutoRenewal().setLocalValue(False)
        self._introductionUpdate(self._viewModel.tabs.getSelectedTabName())
        super(BattleBoosterSetupSubView, self).updateSlots(slotID, fullUpdate, updateData)
        return

    def _updateSlots(self, fullUpdate=True, updateData=True):
        super(BattleBoosterSetupSubView, self)._updateSlots(fullUpdate, updateData)
        self._introductionUpdate(self._viewModel.tabs.getSelectedTabName())

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    def _createTabsController(self):
        return BattleBoostersTabsController()

    def _addListeners(self):
        super(BattleBoosterSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.ADD_ONE_SLOT_ACTION, self.__onAdd)
        self._viewModel.onIntroPassed += self._onIntroPassed
        self._viewModel.showInfoPage += self._showInfoPage

    def _removeListeners(self):
        self._viewModel.onIntroPassed -= self._onIntroPassed
        self._viewModel.showInfoPage -= self._showInfoPage
        super(BattleBoosterSetupSubView, self)._removeListeners()

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            super(BattleBoosterSetupSubView, self)._setTab(tabName)
            self._introductionUpdate(tabName, True)

    def __onAdd(self, args):
        itemIntCD = int(args.get('intCD'))
        self._interactor.buyMore(itemIntCD)

    def _introductionUpdate(self, tabName, forceUpdateTabs=False):
        hasItems = len(self._provider.getItems()) > 0
        introduction = BattleBoostersIntroductionController.getIntroduction(tabName, hasItems)
        self._viewModel.setIntroductionType(introduction or '')
        self._viewModel.setWithIntroduction(introduction is not None)
        if not introduction or forceUpdateTabs:
            self._updateTabs()
        return

    def _onIntroPassed(self):
        BattleBoostersIntroductionController.setIntroductionValue(self._viewModel.getIntroductionType())
        self._introductionUpdate(self._currentTabName)

    @args2params(str)
    def _showInfoPage(self, tabName):
        introductionType = BattleBoostersIntroductionController.getIntroductionType(tabName)
        self._viewModel.setIntroductionType(introductionType)
        self._viewModel.setWithIntroduction(bool(introductionType))
        if introductionType:
            self._updateTabs()
