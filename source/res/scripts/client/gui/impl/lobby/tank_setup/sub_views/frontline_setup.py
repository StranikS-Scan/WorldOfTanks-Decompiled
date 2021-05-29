# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/frontline_setup.py
from gui.game_control.event_progression_controller import EventProgressionScreens
from gui.impl.lobby.tank_setup.configurations.frontline import FrontlineTabsController, FrontlineDealPanel
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController

class FrontlineSetupSubView(BaseEquipmentSetupSubView):
    __progressionController = dependency.descriptor(IEventProgressionController)
    __slots__ = ()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        self._viewModel.setIsLocked(self.__hasBattleAbilities())
        super(FrontlineSetupSubView, self).updateSlots(slotID, fullUpdate, updateData)

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    def _createTabsController(self):
        return FrontlineTabsController()

    def _getDealPanel(self):
        return FrontlineDealPanel

    def _addListeners(self):
        super(FrontlineSetupSubView, self)._addListeners()
        self._viewModel.showBattleAbilitiesSetup += self.__showBattleAbilitiesSetup

    def _removeListeners(self):
        self._viewModel.showBattleAbilitiesSetup -= self.__showBattleAbilitiesSetup
        super(FrontlineSetupSubView, self)._removeListeners()

    def __showBattleAbilitiesSetup(self, *_):
        self.__progressionController.showCustomScreen(EventProgressionScreens.FRONTLINE_RESERVES)

    def __hasBattleAbilities(self):
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED))
