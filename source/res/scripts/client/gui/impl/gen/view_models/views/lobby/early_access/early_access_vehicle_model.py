# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_vehicle_model.py
from enum import Enum
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_animation_params import EarlyAccessAnimationParams

class State(Enum):
    INPROGRESS = 'inProgress'
    ININVENTORY = 'inInventory'
    LOCKED = 'locked'
    PURCHASABLE = 'purchasable'


class VehicleViewTooltipStates(Enum):
    QUESTSWIDGET = 'questsWidget'


class EarlyAccessVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(EarlyAccessVehicleModel, self).__init__(properties=properties, commands=commands)

    @property
    def commonPrice(self):
        return self._getViewModel(9)

    @staticmethod
    def getCommonPriceType():
        return PriceModel

    @property
    def animationParams(self):
        return self._getViewModel(10)

    @staticmethod
    def getAnimationParamsType():
        return EarlyAccessAnimationParams

    def getState(self):
        return State(self._getString(11))

    def setState(self, value):
        self._setString(11, value.value)

    def getPrice(self):
        return self._getNumber(12)

    def setPrice(self, value):
        self._setNumber(12, value)

    def getUnlockPriceAfterEA(self):
        return self._getNumber(13)

    def setUnlockPriceAfterEA(self, value):
        self._setNumber(13, value)

    def getIsPostProgression(self):
        return self._getBool(14)

    def setIsPostProgression(self, value):
        self._setBool(14, value)

    def getIsAffordable(self):
        return self._getBool(15)

    def setIsAffordable(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(EarlyAccessVehicleModel, self)._initialize()
        self._addViewModelProperty('commonPrice', PriceModel())
        self._addViewModelProperty('animationParams', EarlyAccessAnimationParams())
        self._addStringProperty('state')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('unlockPriceAfterEA', 0)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('isAffordable', False)
