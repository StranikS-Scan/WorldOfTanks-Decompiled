# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSellDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSellDialogMeta(AbstractWindowView):

    def setDialogSettings(self, isOpen):
        self._printOverrideError('setDialogSettings')

    def sell(self):
        self._printOverrideError('sell')

    def setUserInput(self, value):
        self._printOverrideError('setUserInput')

    def setCrewDismissal(self, value):
        self._printOverrideError('setCrewDismissal')

    def onSelectionChanged(self, itemID, toInventory, currency):
        self._printOverrideError('onSelectionChanged')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_visibleControlBlockS(self, value):
        return self.flashObject.as_visibleControlBlock(value) if self._isDAAPIInited() else None

    def as_enableButtonS(self, value, tooltip):
        return self.flashObject.as_enableButton(value, tooltip) if self._isDAAPIInited() else None

    def as_setSellEnabledS(self, value, message):
        return self.flashObject.as_setSellEnabled(value, message) if self._isDAAPIInited() else None

    def as_setControlQuestionDataS(self, isGold, value, question):
        return self.flashObject.as_setControlQuestionData(isGold, value, question) if self._isDAAPIInited() else None

    def as_setTotalS(self, common, total):
        return self.flashObject.as_setTotal(common, total) if self._isDAAPIInited() else None

    def as_updateAccountMoneyS(self, currency, value):
        return self.flashObject.as_updateAccountMoney(currency, value) if self._isDAAPIInited() else None

    def as_updateDeviceS(self, item):
        return self.flashObject.as_updateDevice(item) if self._isDAAPIInited() else None
