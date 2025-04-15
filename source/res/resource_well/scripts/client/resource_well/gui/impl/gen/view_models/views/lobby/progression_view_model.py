# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array
from resource_well.gui.impl.gen.view_models.views.lobby.enums import EventMode
from frameworks.wulf import ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.reward_model import RewardModel

class ProgressionState(Enum):
    ACTIVE = 'active'
    FORBIDDEN = 'forbidden'
    NOPROGRESS = 'noProgress'
    NOVEHICLES = 'noVehicles'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onPreview', 'onAboutClick', 'onResourcesContribute', 'onResourcesReturn', 'onHangarShow', 'onClose', 'onRewardSelected')

    def __init__(self, properties=8, commands=7):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def getIsEventEndingSoon(self):
        return self._getBool(2)

    def setIsEventEndingSoon(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def getProgressionState(self):
        return ProgressionState(self._getString(4))

    def setProgressionState(self, value):
        self._setString(4, value.value)

    def getEventMode(self):
        return EventMode(self._getString(5))

    def setEventMode(self, value):
        self._setString(5, value.value)

    def getCurrentRewardId(self):
        return self._getString(6)

    def setCurrentRewardId(self, value):
        self._setString(6, value)

    def getProgression(self):
        return self._getNumber(7)

    def setProgression(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isEventEndingSoon', False)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('progressionState')
        self._addStringProperty('eventMode')
        self._addStringProperty('currentRewardId', '')
        self._addNumberProperty('progression', 0)
        self.onPreview = self._addCommand('onPreview')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onResourcesContribute = self._addCommand('onResourcesContribute')
        self.onResourcesReturn = self._addCommand('onResourcesReturn')
        self.onHangarShow = self._addCommand('onHangarShow')
        self.onClose = self._addCommand('onClose')
        self.onRewardSelected = self._addCommand('onRewardSelected')
