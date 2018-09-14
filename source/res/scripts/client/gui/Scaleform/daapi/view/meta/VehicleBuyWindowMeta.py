# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleBuyWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def submit(self, data):
        self._printOverrideError('submit')

    def selectTab(self, tabIndex):
        self._printOverrideError('selectTab')

    def onTradeInClearVehicle(self):
        self._printOverrideError('onTradeInClearVehicle')

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, value):
        return self.flashObject.as_setCredits(value) if self._isDAAPIInited() else None

    def as_setEnabledSubmitBtnS(self, enabled):
        return self.flashObject.as_setEnabledSubmitBtn(enabled) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data: Represented by VehicleBuyVo (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_updateTradeOffVehicleS(self, vehicleBuyTradeOffVo):
        """
        :param vehicleBuyTradeOffVo: Represented by VehicleBuyTradeOffVo (AS)
        """
        return self.flashObject.as_updateTradeOffVehicle(vehicleBuyTradeOffVo) if self._isDAAPIInited() else None

    def as_setTradeInWarningMessagegeS(self, message):
        return self.flashObject.as_setTradeInWarningMessagege(message) if self._isDAAPIInited() else None
