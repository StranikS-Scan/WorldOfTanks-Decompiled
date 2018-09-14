# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSellDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSellDialogMeta(AbstractWindowView):

    def getDialogSettings(self):
        self._printOverrideError('getDialogSettings')

    def setDialogSettings(self, isOpen):
        self._printOverrideError('setDialogSettings')

    def sell(self, vehicleData, shells, eqs, optDevices, inventory, isDismissCrew):
        self._printOverrideError('sell')

    def setUserInput(self, value):
        self._printOverrideError('setUserInput')

    def setResultCredit(self, isGold, value):
        self._printOverrideError('setResultCredit')

    def checkControlQuestion(self, dismiss):
        self._printOverrideError('checkControlQuestion')

    def as_setDataS(self, vehicle, onVehicle, inInventory, removePrices, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(vehicle, onVehicle, inInventory, removePrices, gold)

    def as_checkGoldS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_checkGold(gold)

    def as_visibleControlBlockS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_visibleControlBlock(value)

    def as_enableButtonS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_enableButton(value)

    def as_setCtrlQuestionS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCtrlQuestion(value)

    def as_setControlNumberS(self, isGold, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setControlNumber(isGold, value)

    def as_cleanInputSummS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_cleanInputSumm()
