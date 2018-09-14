# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TankCarouselMeta(DAAPIModule):

    def vehicleChange(self, vehicleInventoryId):
        self._printOverrideError('vehicleChange')

    def buySlot(self):
        self._printOverrideError('buySlot')

    def buyTankClick(self):
        self._printOverrideError('buyTankClick')

    def setVehiclesFilter(self, nation, tankType, ready):
        self._printOverrideError('setVehiclesFilter')

    def setFalloutFilter(self, falloutVehVisible):
        self._printOverrideError('setFalloutFilter')

    def getVehicleTypeProvider(self):
        self._printOverrideError('getVehicleTypeProvider')

    def as_setCarouselFilterS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCarouselFilter(data)

    def as_setParamsS(self, params):
        if self._isDAAPIInited():
            return self.flashObject.as_setParams(params)

    def as_updateVehiclesS(self, vehiclesData, isSet):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVehicles(vehiclesData, isSet)

    def as_showVehiclesS(self, compactDescrList):
        if self._isDAAPIInited():
            return self.flashObject.as_showVehicles(compactDescrList)

    def as_setIsEventS(self, isEvent):
        if self._isDAAPIInited():
            return self.flashObject.as_setIsEvent(isEvent)
