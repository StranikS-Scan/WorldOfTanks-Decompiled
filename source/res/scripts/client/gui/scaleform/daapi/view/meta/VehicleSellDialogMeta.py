# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSellDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSellDialogMeta(AbstractWindowView):

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

    def onChangeConfiguration(self, optDevices):
        self._printOverrideError('onChangeConfiguration')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_checkGoldS(self, gold):
        return self.flashObject.as_checkGold(gold) if self._isDAAPIInited() else None

    def as_visibleControlBlockS(self, value):
        return self.flashObject.as_visibleControlBlock(value) if self._isDAAPIInited() else None

    def as_enableButtonS(self, value):
        return self.flashObject.as_enableButton(value) if self._isDAAPIInited() else None

    def as_setControlQuestionDataS(self, isGold, value, question):
        return self.flashObject.as_setControlQuestionData(isGold, value, question) if self._isDAAPIInited() else None
