# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareViewMeta.py
from gui.Scaleform.framework.entities.View import View

class VehicleCompareViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def closeView(self):
        self._printOverrideError('closeView')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onGoToPreviewClick(self, vehicleID):
        self._printOverrideError('onGoToPreviewClick')

    def onGoToHangarClick(self, vehicleID):
        self._printOverrideError('onGoToHangarClick')

    def onSelectModulesClick(self, vehicleID, index):
        self._printOverrideError('onSelectModulesClick')

    def onParamDeltaRequested(self, index, paramID):
        self._printOverrideError('onParamDeltaRequested')

    def onCrewLevelChanged(self, index, crewLevelID):
        self._printOverrideError('onCrewLevelChanged')

    def onRemoveVehicle(self, index):
        self._printOverrideError('onRemoveVehicle')

    def onRemoveAllVehicles(self):
        self._printOverrideError('onRemoveAllVehicles')

    def as_setStaticDataS(self, data):
        """
        :param data: Represented by VehCompareStaticDataVO (AS)
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setParamsDeltaS(self, data):
        """
        :param data: Represented by VehCompareParamsDeltaVO (AS)
        """
        return self.flashObject.as_setParamsDelta(data) if self._isDAAPIInited() else None

    def as_setVehicleParamsDataS(self, data):
        return self.flashObject.as_setVehicleParamsData(data) if self._isDAAPIInited() else None

    def as_getVehiclesDPS(self):
        return self.flashObject.as_getVehiclesDP() if self._isDAAPIInited() else None

    def as_setVehiclesCountTextS(self, text):
        return self.flashObject.as_setVehiclesCountText(text) if self._isDAAPIInited() else None

    def as_setAttentionVisibleS(self, value):
        return self.flashObject.as_setAttentionVisible(value) if self._isDAAPIInited() else None
