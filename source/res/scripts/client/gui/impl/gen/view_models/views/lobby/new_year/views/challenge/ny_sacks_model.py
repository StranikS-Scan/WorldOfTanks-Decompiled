# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/ny_sacks_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.sack_reward_model import SackRewardModel

class NySacksModel(ViewModel):
    __slots__ = ('onOpenSack', 'onOpenAnimationStart', 'onOpenAnimationEnd')

    def __init__(self, properties=10, commands=3):
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

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getCount(self):
        return self._getNumber(6)

    def setCount(self, value):
        self._setNumber(6, value)

    def getIsSacksMarkerShown(self):
        return self._getBool(7)

    def setIsSacksMarkerShown(self, value):
        self._setBool(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return SackRewardModel

    def getIsOpening(self):
        return self._getBool(9)

    def setIsOpening(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(NySacksModel, self)._initialize()
        self._addBoolProperty('isReady', False)
        self._addNumberProperty('missionsCompleted', 0)
        self._addNumberProperty('missionsTotal', 0)
        self._addNumberProperty('missionsCountdown', 0)
        self._addStringProperty('missionDescription', '')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isSacksMarkerShown', False)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isOpening', False)
        self.onOpenSack = self._addCommand('onOpenSack')
        self.onOpenAnimationStart = self._addCommand('onOpenAnimationStart')
        self.onOpenAnimationEnd = self._addCommand('onOpenAnimationEnd')
