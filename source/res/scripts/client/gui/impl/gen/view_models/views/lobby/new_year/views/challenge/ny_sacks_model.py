# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/ny_sacks_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.sack_model import SackModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.sack_reward_model import SackRewardModel

class NySacksModel(ViewModel):
    __slots__ = ('onOpenSack', 'onOpenAnimationEnd')

    def __init__(self, properties=8, commands=2):
        super(NySacksModel, self).__init__(properties=properties, commands=commands)

    def getIsReady(self):
        return self._getBool(0)

    def setIsReady(self, value):
        self._setBool(0, value)

    def getMissionsCompleted(self):
        return self._getNumber(1)

    def setMissionsCompleted(self, value):
        self._setNumber(1, value)

    def getMissionsTotal(self):
        return self._getNumber(2)

    def setMissionsTotal(self, value):
        self._setNumber(2, value)

    def getMissionsCountdown(self):
        return self._getNumber(3)

    def setMissionsCountdown(self, value):
        self._setNumber(3, value)

    def getMissionDescription(self):
        return self._getString(4)

    def setMissionDescription(self, value):
        self._setString(4, value)

    def getSacks(self):
        return self._getArray(5)

    def setSacks(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSacksType():
        return SackModel

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return SackRewardModel

    def getIsOpening(self):
        return self._getBool(7)

    def setIsOpening(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NySacksModel, self)._initialize()
        self._addBoolProperty('isReady', False)
        self._addNumberProperty('missionsCompleted', 0)
        self._addNumberProperty('missionsTotal', 0)
        self._addNumberProperty('missionsCountdown', 0)
        self._addStringProperty('missionDescription', '')
        self._addArrayProperty('sacks', Array())
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isOpening', False)
        self.onOpenSack = self._addCommand('onOpenSack')
        self.onOpenAnimationEnd = self._addCommand('onOpenAnimationEnd')
