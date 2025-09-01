# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicles_inventory_model.py
from frameworks.wulf import ViewModel

class VehiclesInventoryModel(ViewModel):
    __slots__ = ('onBuySlot', 'onGoBuyVehicle', 'onGoRecoverVehicle', 'onSelect')
    NO_VEHICLE_ID = -1
    ENABLED = 'enabled'
    DISABLED = 'disabled'
    PAUSED = 'paused'

    def __init__(self, properties=10, commands=4):
        super(VehiclesInventoryModel, self).__init__(properties=properties, commands=commands)

    def getCurrentVehicleIntCD(self):
        return self._getNumber(0)

    def setCurrentVehicleIntCD(self, value):
        self._setNumber(0, value)

    def getCurrentVehicleInventoryId(self):
        return self._getNumber(1)

    def setCurrentVehicleInventoryId(self, value):
        self._setNumber(1, value)

    def getFreeSlotsCount(self):
        return self._getNumber(2)

    def setFreeSlotsCount(self, value):
        self._setNumber(2, value)

    def getRecoverableVehicleCount(self):
        return self._getNumber(3)

    def setRecoverableVehicleCount(self, value):
        self._setNumber(3, value)

    def getSlotPrice(self):
        return self._getNumber(4)

    def setSlotPrice(self, value):
        self._setNumber(4, value)

    def getDefaultSlotPrice(self):
        return self._getNumber(5)

    def setDefaultSlotPrice(self, value):
        self._setNumber(5, value)

    def getBpEntityValid(self):
        return self._getBool(6)

    def setBpEntityValid(self, value):
        self._setBool(6, value)

    def getBpStatus(self):
        return self._getString(7)

    def setBpStatus(self, value):
        self._setString(7, value)

    def getSlotPriceCurrency(self):
        return self._getString(8)

    def setSlotPriceCurrency(self, value):
        self._setString(8, value)

    def getHasDiscont(self):
        return self._getBool(9)

    def setHasDiscont(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(VehiclesInventoryModel, self)._initialize()
        self._addNumberProperty('currentVehicleIntCD', -1)
        self._addNumberProperty('currentVehicleInventoryId', -1)
        self._addNumberProperty('freeSlotsCount', 0)
        self._addNumberProperty('recoverableVehicleCount', 0)
        self._addNumberProperty('slotPrice', 0)
        self._addNumberProperty('defaultSlotPrice', 0)
        self._addBoolProperty('bpEntityValid', False)
        self._addStringProperty('bpStatus', '')
        self._addStringProperty('slotPriceCurrency', '')
        self._addBoolProperty('hasDiscont', False)
        self.onBuySlot = self._addCommand('onBuySlot')
        self.onGoBuyVehicle = self._addCommand('onGoBuyVehicle')
        self.onGoRecoverVehicle = self._addCommand('onGoRecoverVehicle')
        self.onSelect = self._addCommand('onSelect')
