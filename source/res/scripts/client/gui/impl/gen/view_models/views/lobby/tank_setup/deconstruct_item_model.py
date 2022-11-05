# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/deconstruct_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.tank_setup.slot_vehicle_info_model import SlotVehicleInfoModel

class DeconstructItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(DeconstructItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return SlotVehicleInfoModel

    @property
    def bonuses(self):
        return self._getViewModel(1)

    @staticmethod
    def getBonusesType():
        return BonusesModel

    def getDeviceID(self):
        return self._getNumber(2)

    def setDeviceID(self, value):
        self._setNumber(2, value)

    def getDeviceName(self):
        return self._getString(3)

    def setDeviceName(self, value):
        self._setString(3, value)

    def getDeviceImage(self):
        return self._getResource(4)

    def setDeviceImage(self, value):
        self._setResource(4, value)

    def getDeviceLevel(self):
        return self._getNumber(5)

    def setDeviceLevel(self, value):
        self._setNumber(5, value)

    def getEffect(self):
        return self._getResource(6)

    def setEffect(self, value):
        self._setResource(6, value)

    def getEquipCoinsForDeconstruction(self):
        return self._getNumber(7)

    def setEquipCoinsForDeconstruction(self, value):
        self._setNumber(7, value)

    def getStorageCount(self):
        return self._getNumber(8)

    def setStorageCount(self, value):
        self._setNumber(8, value)

    def getSelectedCount(self):
        return self._getNumber(9)

    def setSelectedCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(DeconstructItemModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', SlotVehicleInfoModel())
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addNumberProperty('deviceID', 0)
        self._addStringProperty('deviceName', '')
        self._addResourceProperty('deviceImage', R.invalid())
        self._addNumberProperty('deviceLevel', 1)
        self._addResourceProperty('effect', 1)
        self._addNumberProperty('equipCoinsForDeconstruction', 0)
        self._addNumberProperty('storageCount', 0)
        self._addNumberProperty('selectedCount', 0)
