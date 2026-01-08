# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.resource_well.reward_model import RewardModel

class ProgressionState(Enum):
    ACTIVE = 'active'
    FORBIDDEN = 'forbidden'
    NOPROGRESS = 'noProgress'
    NOVEHICLES = 'noVehicles'
    BEFOREEVENT = 'beforeEvent'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onPreview', 'onAboutClick', 'onResourcesContribute', 'onResourcesReturn', 'onHangarShow', 'onViewLoaded', 'onClose')

    def __init__(self, properties=12, commands=7):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getTimeLeft(self):
        return self._getNumber(2)

    def setTimeLeft(self, value):
        self._setNumber(2, value)

    def getBeforeEventTimeLeft(self):
        return self._getNumber(3)

    def setBeforeEventTimeLeft(self, value):
        self._setNumber(3, value)

    def getServerTimestamp(self):
        return self._getNumber(4)

    def setServerTimestamp(self, value):
        self._setNumber(4, value)

    def getIsEventEndingSoon(self):
        return self._getBool(5)

    def setIsEventEndingSoon(self, value):
        self._setBool(5, value)

    def getTopRewardPlayersCount(self):
        return self._getNumber(6)

    def setTopRewardPlayersCount(self, value):
        self._setNumber(6, value)

    def getRegularRewardVehiclesCount(self):
        return self._getNumber(7)

    def setRegularRewardVehiclesCount(self, value):
        self._setNumber(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def getProgressionState(self):
        return ProgressionState(self._getString(9))

    def setProgressionState(self, value):
        self._setString(9, value.value)

    def getProgression(self):
        return self._getNumber(10)

    def setProgression(self, value):
        self._setNumber(10, value)

    def getVehicleName(self):
        return self._getString(11)

    def setVehicleName(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('beforeEventTimeLeft', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self._addBoolProperty('isEventEndingSoon', False)
        self._addNumberProperty('topRewardPlayersCount', 0)
        self._addNumberProperty('regularRewardVehiclesCount', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('progressionState')
        self._addNumberProperty('progression', 0)
        self._addStringProperty('vehicleName', '')
        self.onPreview = self._addCommand('onPreview')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onResourcesContribute = self._addCommand('onResourcesContribute')
        self.onResourcesReturn = self._addCommand('onResourcesReturn')
        self.onHangarShow = self._addCommand('onHangarShow')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onClose = self._addCommand('onClose')
