# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleBuyWindowMeta(AbstractWindowView):

    def submit(self, data):
        self._printOverrideError('submit')

    def stateChange(self, data):
        self._printOverrideError('stateChange')

    def selectTab(self, tabIndex):
        self._printOverrideError('selectTab')

    def onTradeInClearVehicle(self):
        self._printOverrideError('onTradeInClearVehicle')

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, value):
        return self.flashObject.as_setCredits(value) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_updateTradeOffVehicleS(self, vehicleBuyTradeOffVo):
        return self.flashObject.as_updateTradeOffVehicle(vehicleBuyTradeOffVo) if self._isDAAPIInited() else None

    def as_setTradeInWarningMessagegeS(self, message):
        return self.flashObject.as_setTradeInWarningMessagege(message) if self._isDAAPIInited() else None

    def as_setStateS(self, academyEnabled, schoolEnabled, freeEnabled, submitEnabled):
        return self.flashObject.as_setState(academyEnabled, schoolEnabled, freeEnabled, submitEnabled) if self._isDAAPIInited() else None
