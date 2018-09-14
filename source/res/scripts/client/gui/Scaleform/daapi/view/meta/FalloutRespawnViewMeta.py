# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FalloutRespawnViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onVehicleSelected(self, vehicleID):
        """
        :param vehicleID:
        :return :
        """
        self._printOverrideError('onVehicleSelected')

    def onPostmortemBtnClick(self):
        """
        :return :
        """
        self._printOverrideError('onPostmortemBtnClick')

    def as_initializeS(self, mainData, slotsData):
        """
        :param mainData:
        :param slotsData:
        :return :
        """
        return self.flashObject.as_initialize(mainData, slotsData) if self._isDAAPIInited() else None

    def as_updateTimerS(self, mainTimer, slotsStateData):
        """
        :param mainTimer:
        :param slotsStateData:
        :return :
        """
        return self.flashObject.as_updateTimer(mainTimer, slotsStateData) if self._isDAAPIInited() else None

    def as_updateS(self, selectedVehicleName, slotsStateData):
        """
        :param selectedVehicleName:
        :param slotsStateData:
        :return :
        """
        return self.flashObject.as_update(selectedVehicleName, slotsStateData) if self._isDAAPIInited() else None

    def as_showGasAttackModeS(self):
        """
        :return :
        """
        return self.flashObject.as_showGasAttackMode() if self._isDAAPIInited() else None
