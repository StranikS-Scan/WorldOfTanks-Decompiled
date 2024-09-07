# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/tooltips/selected_reward_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SelectedRewardName(Enum):
    VEHICLE_FOR_GIFT = 'vehicleForGift'
    VEHICLE_DISCOUNT = 'vehicleDiscount'
    BLUEPRINTS = 'blueprints'


class SelectedRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
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

    def getExpDiscount(self):
        return self._getNumber(3)

    def setExpDiscount(self, value):
        self._setNumber(3, value)

    def getCreditDiscount(self):
        return self._getNumber(4)

    def setCreditDiscount(self, value):
        self._setNumber(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getCount(self):
        return self._getNumber(6)

    def setCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(SelectedRewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addStringProperty('userName', '')
        self._addNumberProperty('expDiscount', 0)
        self._addNumberProperty('creditDiscount', 0)
        self._addStringProperty('nation', '')
        self._addNumberProperty('count', 0)
