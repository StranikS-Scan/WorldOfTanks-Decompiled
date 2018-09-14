# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TankCarouselMeta(BaseDAAPIComponent):

    def vehicleChange(self, vehicleInventoryId):
        self._printOverrideError('vehicleChange')

    def buySlot(self):
        self._printOverrideError('buySlot')

    def buyTankClick(self):
        self._printOverrideError('buyTankClick')

    def setVehiclesFilter(self, nation, tankType, ready, gameModeFilter):
        self._printOverrideError('setVehiclesFilter')

    def getVehicleTypeProvider(self):
        self._printOverrideError('getVehicleTypeProvider')

    def setVehicleSelected(self, vehicleInventoryId, selected):
        self._printOverrideError('setVehicleSelected')

    def moveVehiclesSelectionSlot(self, vehicleInventoryId):
        self._printOverrideError('moveVehiclesSelectionSlot')

    def as_setMultiselectionModeS(self, data):
        return self.flashObject.as_setMultiselectionMode(data) if self._isDAAPIInited() else None

    def as_setMultiselectionButtonLabelsS(self, activateLabel, deactivateLabel, disabledTooltip):
        return self.flashObject.as_setMultiselectionButtonLabels(activateLabel, deactivateLabel, disabledTooltip) if self._isDAAPIInited() else None

    def as_updateMultiselectionDataS(self, multiselectData):
        return self.flashObject.as_updateMultiselectionData(multiselectData) if self._isDAAPIInited() else None

    def as_setCarouselFilterS(self, filter):
        return self.flashObject.as_setCarouselFilter(filter) if self._isDAAPIInited() else None

    def as_setParamsS(self, params):
        return self.flashObject.as_setParams(params) if self._isDAAPIInited() else None

    def as_updateVehiclesS(self, vehiclesData, isSet):
        return self.flashObject.as_updateVehicles(vehiclesData, isSet) if self._isDAAPIInited() else None

    def as_showVehiclesS(self, compactDescrList):
        return self.flashObject.as_showVehicles(compactDescrList) if self._isDAAPIInited() else None
