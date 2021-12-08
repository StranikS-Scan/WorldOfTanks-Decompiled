# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_progress_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class NewYearChallengeProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearChallengeProgressModel, self).__init__(properties=properties, commands=commands)

    def getRewardLevel(self):
        return self._getNumber(0)

    def setRewardLevel(self, value):
        self._setNumber(0, value)

    def getStyleRewardIdx(self):
        return self._getNumber(1)

    def setStyleRewardIdx(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(NewYearChallengeProgressModel, self)._initialize()
        self._addNumberProperty('rewardLevel', 0)
        self._addNumberProperty('styleRewardIdx', -1)
        self._addArrayProperty('rewards', Array())
