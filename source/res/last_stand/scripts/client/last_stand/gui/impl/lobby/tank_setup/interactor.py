# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tank_setup/interactor.py
import BigWorld
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from adisp import adisp_process
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from gui.shared.gui_items.processors import Processor
from gui.shared.utils import decorators
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from LSAccountEquipmentController import getLSConsumables

class ActionTypes(object):
    BUY_AND_INSTALL_LS_CONSUMABLES_ACTION = 'buyAndInstallLSConsumables'


class LastStandInteractor(ConsumableInteractor):
    CONFIRM_ACTION = ActionTypes.BUY_AND_INSTALL_LS_CONSUMABLES_ACTION

    def getName(self):
        return LSTankSetupConstants.LS_CONSUMABLES

    @adisp_process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(self.CONFIRM_ACTION, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def getInstalledLayout(self):
        return getLSConsumables(self.getItem()).installed

    def getCurrentLayout(self):
        return getLSConsumables(self.getItem()).layout

    def getVehicleAfterInstall(self):
        vehicle = super(LastStandInteractor, self).getVehicleAfterInstall()
        getLSConsumables(vehicle).installed = getLSConsumables(self.getItem()).layout.copy()
        return vehicle

    def revert(self):
        getLSConsumables(self.getItem()).layout = self.getInstalledLayout().copy()
        super(LastStandInteractor, self).revert()

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(LastStandInteractor, self).updateFrom(vehicle, onlyInstalled)
        getLSConsumables(self.getItem()).installed = getLSConsumables(vehicle).installed.copy()
        getLSConsumables(self.getItem()).isAutoEquip = getLSConsumables(vehicle).isAutoEquip
        self._playerLayout = getLSConsumables(vehicle).layout.copy()
        if not onlyInstalled:
            getLSConsumables(self.getItem()).layout = getLSConsumables(vehicle).layout.copy()

    def _createAutoRenewal(self):
        return LSDefConsumableAutoRenewal(self.getItem())


class LSVehicleAutoEquipProcessor(Processor):

    def __init__(self, vehicle, value):
        super(LSVehicleAutoEquipProcessor, self).__init__()
        self._value = value
        self._vehicle = vehicle

    def _request(self, callback):
        eqCtrl = BigWorld.player().LSAccountEquipmentController
        eqCtrl.setAutoMaintenanceEnabled(self._vehicle.invID, self._value, lambda requestID, code, errStr: self._response(code, callback, errStr=errStr))


class LSDefConsumableAutoRenewal(BaseAutoRenewal):

    def getValue(self):
        return getLSConsumables(self._vehicle).isAutoEquip

    @decorators.adisp_process('techMaintenance')
    def processVehicleAutoRenewal(self, callback):
        yield LSVehicleAutoEquipProcessor(self._vehicle, self.getLocalValue()).request()
        self.setLocalValue(None)
        callback(None)
        return
