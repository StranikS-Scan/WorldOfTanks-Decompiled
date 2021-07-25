# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/frontline.py
from async import await, async
from BWUtil import AsyncReturn
from adisp import process
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.event_dispatcher import showBattleAbilitiesConfirmDialog
from gui.shared.gui_items.items_actions import factory as ActionsFactory

class FrontlineInteractor(BaseEquipmentInteractor):
    __slots__ = ()

    def getName(self):
        return TankSetupConstants.BATTLE_ABILITIES

    def getInstalledLayout(self):
        return self.getItem().battleAbilities.installed

    def getCurrentLayout(self):
        return self.getItem().battleAbilities.layout

    def revert(self):
        self.getItem().battleAbilities.setLayout(*self.getPlayerLayout())
        self._resetInstalledIndices()
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    def updateFrom(self, vehicle, onlyInstalled=True):
        self.getItem().battleAbilities.setInstalled(*vehicle.battleAbilities.installed)
        self._playerLayout = vehicle.battleAbilities.layout.copy()
        if not onlyInstalled:
            self.getItem().battleAbilities.setLayout(*vehicle.battleAbilities.layout)

    @process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.INSTALL_BATTLE_ABILITIES, self.getItem())
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @async
    def showExitConfirmDialog(self):
        changedItems = self.getChangedList()
        result = yield await(showBattleAbilitiesConfirmDialog(items=changedItems, withInstall=bool(changedItems)))
        raise AsyncReturn(result)
