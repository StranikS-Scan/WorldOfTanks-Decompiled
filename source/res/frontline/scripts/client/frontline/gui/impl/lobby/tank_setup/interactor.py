# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tank_setup/interactor.py
from BWUtil import AsyncReturn
from adisp import adisp_process
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineConst
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.event_dispatcher import showFrontlineConfirmDialog
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from wg_async import wg_await, wg_async, await_callback
from frontline.gui.frontline_helpers import becomeNonPlayerState

class ReservesAutoRenewal(BaseAutoRenewal):
    __slots__ = ()

    def getValue(self):
        return True

    @adisp_process
    def processVehicleAutoRenewal(self, callback):
        action = ActionsFactory.getAction(ActionsFactory.FRONTLINE_INSTALL_RESERVES, vehicle=self._vehicle, skillsInteractor=None, skipConfirm=True)
        if action is not None:
            result = yield action.doAction()
            if not result:
                callback(result)
                return
        self.setLocalValue(None)
        callback(None)
        return


class FrontlineInteractor(BaseEquipmentInteractor):
    __slots__ = ('_checkboxState',)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, vehItem):
        super(FrontlineInteractor, self).__init__(vehItem)
        self._checkboxState = False

    def getName(self):
        return FrontlineConst.BATTLE_ABILITIES

    def getInstalledLayout(self):
        return self.getItem().battleAbilities.installed

    def getCurrentLayout(self):
        return self.getItem().battleAbilities.layout

    def getSetupLayout(self):
        return self.getItem().battleAbilities.setupLayouts

    def getCheckboxState(self):
        return self._checkboxState

    def applyAutoRenewal(self, callback):
        super(FrontlineInteractor, self).applyAutoRenewal(callback)
        self._checkboxState = False

    def revert(self):
        if self.hasItem and not becomeNonPlayerState():
            self.getItem().battleAbilities.setLayout(*self.getPlayerLayout())
            self._resetInstalledIndices()
            self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
            self.onRevert()

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(FrontlineInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().battleAbilities
        items.setInstalled(*vehicle.battleAbilities.installed)
        items.setupLayouts.setSetups(vehicle.battleAbilities.setupLayouts.setups)
        self._playerLayout = vehicle.battleAbilities.layout.copy()
        if not onlyInstalled:
            self.getItem().battleAbilities.setLayout(*vehicle.battleAbilities.layout)

    def getPendingPurchaseSkillIds(self):
        epicSkills = self.__epicController.getEpicSkills()
        return [ epicSkills[item.innationID].skillID for item in self.getChangedList() if not epicSkills[item.innationID].isActivated ]

    @adisp_process
    def confirm(self, callback, skipDialog=True):
        action = ActionsFactory.getAction(ActionsFactory.BUY_BATTLE_ABILITIES, self.getPendingPurchaseSkillIds())
        yield action.doAction()
        vehicle = self.getItem()
        action = ActionsFactory.getAction(ActionsFactory.FRONTLINE_INSTALL_RESERVES, vehicle=vehicle, skillsInteractor=self, skipConfirm=True)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @wg_async
    def applyQuit(self, callback, skipApplyAutoRenewal):
        if not becomeNonPlayerState():
            if not self.isPlayerLayout():
                yield await_callback(self.confirm)(skipDialog=True)
            super(FrontlineInteractor, self).applyQuit(callback, skipApplyAutoRenewal)

    def setCheckboxState(self, state):
        self._checkboxState = state

    @wg_async
    def showExitConfirmDialog(self):
        vehicle = self.getItem()
        result = None
        if not becomeNonPlayerState():
            result = yield wg_await(showFrontlineConfirmDialog(skillsInteractor=self, vehicleType=vehicle.type))
        raise AsyncReturn(result)
        return

    def getChangedList(self):
        return self.getCurrentLayout() or [] if self._checkboxState else super(FrontlineInteractor, self).getChangedList() or []

    def _createAutoRenewal(self):
        return ReservesAutoRenewal(self.getItem())
