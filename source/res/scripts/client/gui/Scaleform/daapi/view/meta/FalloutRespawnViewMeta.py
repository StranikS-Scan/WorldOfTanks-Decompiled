# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FalloutRespawnViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onVehicleSelected(self, vehicleID):
        self._printOverrideError('onVehicleSelected')

    def onPostmortemBtnClick(self):
        self._printOverrideError('onPostmortemBtnClick')

    def as_initializeS(self, mainData, slotsData):
        return self.flashObject.as_initialize(mainData, slotsData) if self._isDAAPIInited() else None

    def as_updateTimerS(self, mainTimer, slotsStateData):
        return self.flashObject.as_updateTimer(mainTimer, slotsStateData) if self._isDAAPIInited() else None

    def as_updateS(self, selectedVehicleName, slotsStateData):
        return self.flashObject.as_update(selectedVehicleName, slotsStateData) if self._isDAAPIInited() else None

    def as_showGasAttackModeS(self):
        return self.flashObject.as_showGasAttackMode() if self._isDAAPIInited() else None
