# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/vehicle_selection_models/selected_reward_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SelectedRewardName(Enum):
    VEHICLE_FOR_GIFT = 'vehicleForGift'
    VEHICLE_DISCOUNT = 'vehicleDiscount'
    BLUEPRINTS = 'blueprints'


class SelectedRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SelectedRewardModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getVehicleLvl(self):
        return self._getNumber(1)

    def setVehicleLvl(self, value):
        self._setNumber(1, value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getCreditDiscount(self):
        return self._getNumber(3)

    def setCreditDiscount(self, value):
        self._setNumber(3, value)

    def getNation(self):
        return self._getString(4)

    def setNation(self, value):
        self._setString(4, value)

    def getCount(self):
        return self._getNumber(5)

    def setCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SelectedRewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addStringProperty('userName', '')
        self._addNumberProperty('creditDiscount', 0)
        self._addStringProperty('nation', '')
        self._addNumberProperty('count', 0)
