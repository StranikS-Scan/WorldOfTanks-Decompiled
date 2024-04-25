# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/base_frontman_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.ability_model import AbilityModel
from historical_battles.gui.impl.gen.view_models.views.common.base_vehicle_model import BaseVehicleModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_progresive_model import QuestProgresiveModel

class FrontmanRole(Enum):
    ENGINEER = 'engineer'
    AVIATION = 'aviation'
    ARTILLERY = 'artillery'


class FrontmanState(Enum):
    DEFAULT = 'default'
    INBATTLE = 'inBattle'
    INPLATOON = 'inPlatoon'


class BaseFrontmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BaseFrontmanModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return BaseVehicleModel

    @property
    def progress(self):
        return self._getViewModel(1)

    @staticmethod
    def getProgressType():
        return QuestProgresiveModel

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getRole(self):
        return FrontmanRole(self._getString(3))

    def setRole(self, value):
        self._setString(3, value.value)

    def getState(self):
        return FrontmanState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def getIsProfiledVehicle(self):
        return self._getBool(5)

    def setIsProfiledVehicle(self, value):
        self._setBool(5, value)

    def getHasNewVehicle(self):
        return self._getBool(6)

    def setHasNewVehicle(self, value):
        self._setBool(6, value)

    def getCanSwitchVehicle(self):
        return self._getBool(7)

    def setCanSwitchVehicle(self, value):
        self._setBool(7, value)

    def getPerkId(self):
        return self._getNumber(8)

    def setPerkId(self, value):
        self._setNumber(8, value)

    def getPerkName(self):
        return self._getString(9)

    def setPerkName(self, value):
        self._setString(9, value)

    def getPolygon(self):
        return self._getString(10)

    def setPolygon(self, value):
        self._setString(10, value)

    def getAbilities(self):
        return self._getArray(11)

    def setAbilities(self, value):
        self._setArray(11, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def _initialize(self):
        super(BaseFrontmanModel, self)._initialize()
        self._addViewModelProperty('vehicle', BaseVehicleModel())
        self._addViewModelProperty('progress', QuestProgresiveModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('role')
        self._addStringProperty('state')
        self._addBoolProperty('isProfiledVehicle', True)
        self._addBoolProperty('hasNewVehicle', False)
        self._addBoolProperty('canSwitchVehicle', True)
        self._addNumberProperty('perkId', 0)
        self._addStringProperty('perkName', '')
        self._addStringProperty('polygon', '')
        self._addArrayProperty('abilities', Array())
