# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/frontline_setup.py
from gui.game_control.epic_meta_game_ctrl import EpicBattleScreens
from gui.impl.lobby.tank_setup.configurations.epic_battle_ability import EpicBattleTabsController, EpicBattleDealPanel
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattleSetupSubView(BaseEquipmentSetupSubView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__currentCategory',)

    def __init__(self, viewModel, interactor):
        super(EpicBattleSetupSubView, self).__init__(viewModel, interactor)
        self.__currentCategory = ''

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        self._viewModel.setIsLocked(self.__hasBattleAbilities())
        super(EpicBattleSetupSubView, self).updateSlots(slotID, True, updateData)
        slots = self._viewModel.getSlots()
        itemCategory = slots[slotID].getCategory() if len(slots) >= slotID else ''
        if self.__currentCategory != itemCategory:
            self.__currentCategory = itemCategory
            self._viewModel.setSelectedCategory(itemCategory)

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    def _createTabsController(self):
        return EpicBattleTabsController()

    def _getDealPanel(self):
        return EpicBattleDealPanel

    def _addListeners(self):
        super(EpicBattleSetupSubView, self)._addListeners()
        self._viewModel.showBattleAbilitiesSetup += self.__showBattleAbilitiesSetup

    def _removeListeners(self):
        self._viewModel.showBattleAbilitiesSetup -= self.__showBattleAbilitiesSetup
        super(EpicBattleSetupSubView, self)._removeListeners()

    def __showBattleAbilitiesSetup(self, *_):
        self.__epicController.showCustomScreen(EpicBattleScreens.RESERVES)

    def __hasBattleAbilities(self):
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED))
