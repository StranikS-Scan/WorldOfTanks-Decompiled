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

    def as_setMultiselectionModeS(self, enabled, formattedMessage, showSlots, slots):
        if self._isDAAPIInited():
            return self.flashObject.as_setMultiselectionMode(enabled, formattedMessage, showSlots, slots)

    def as_setMultiselectionButtonLabelsS(self, activateLabel, deactivateLabel, disabledTooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setMultiselectionButtonLabels(activateLabel, deactivateLabel, disabledTooltip)

    def as_updateMultiselectionDataS(self, multiselectData):
        if self._isDAAPIInited():
            return self.flashObject.as_updateMultiselectionData(multiselectData)

    def as_setCarouselFilterS(self, filter):
        if self._isDAAPIInited():
            return self.flashObject.as_setCarouselFilter(filter)

    def as_setParamsS(self, params):
        if self._isDAAPIInited():
            return self.flashObject.as_setParams(params)

    def as_updateVehiclesS(self, vehiclesData, isSet):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVehicles(vehiclesData, isSet)

    def as_showVehiclesS(self, compactDescrList):
        if self._isDAAPIInited():
            return self.flashObject.as_showVehicles(compactDescrList)
