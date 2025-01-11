# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_vehicle_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_animation_params import Pm3AnimationParams
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_reward_item_model import Pm3RewardItemModel

class State(Enum):
    INPROGRESS = 'inProgress'
    ININVENTORY = 'inInventory'
    PURCHASABLE = 'purchasable'
    LOCKED = 'locked'


class VehicleViewTooltipStates(Enum):
    QUESTSWIDGET = 'questsWidget'


class Pm3VehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(Pm3VehicleModel, self).__init__(properties=properties, commands=commands)

    @property
    def animationParams(self):
        return self._getViewModel(9)

    @staticmethod
    def getAnimationParamsType():
        return Pm3AnimationParams

    def getState(self):
        return State(self._getString(10))

    def setState(self, value):
        self._setString(10, value.value)

    def getDefaultState(self):
        return State(self._getString(11))

    def setDefaultState(self, value):
        self._setString(11, value.value)

    def getHonorState(self):
        return State(self._getString(12))

    def setHonorState(self, value):
        self._setString(12, value.value)

    def getProgress(self):
        return self._getNumber(13)

    def setProgress(self, value):
        self._setNumber(13, value)

    def getToUnlock(self):
        return self._getNumber(14)

    def setToUnlock(self, value):
        self._setNumber(14, value)

    def getBadges(self):
        return self._getArray(15)

    def setBadges(self, value):
        self._setArray(15, value)

    @staticmethod
    def getBadgesType():
        return Pm3RewardItemModel

    def getRestorePrice(self):
        return self._getNumber(16)

    def setRestorePrice(self, value):
        self._setNumber(16, value)

    def getRestoreSeconds(self):
        return self._getNumber(17)

    def setRestoreSeconds(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(Pm3VehicleModel, self)._initialize()
        self._addViewModelProperty('animationParams', Pm3AnimationParams())
        self._addStringProperty('state')
        self._addStringProperty('defaultState')
        self._addStringProperty('honorState')
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('toUnlock', 0)
        self._addArrayProperty('badges', Array())
        self._addNumberProperty('restorePrice', 0)
        self._addNumberProperty('restoreSeconds', 0)
