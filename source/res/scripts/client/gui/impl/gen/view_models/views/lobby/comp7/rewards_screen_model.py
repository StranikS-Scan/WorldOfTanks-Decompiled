# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/rewards_screen_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.qualification_battle import QualificationBattle

class Type(IntEnum):
    RANK = 0
    DIVISION = 1
    RANKREWARDS = 2
    TOKENSREWARDS = 3
    QUALIFICATIONREWARDS = 4
    QUALIFICATIONRANK = 5


class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class Division(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class SeasonName(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class RewardsScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=10, commands=1):
        super(RewardsScreenModel, self).__init__(properties=properties, commands=commands)

    def getSeasonName(self):
        return SeasonName(self._getString(0))

    def setSeasonName(self, value):
        self._setString(0, value.value)

    def getType(self):
        return Type(self._getNumber(1))

    def setType(self, value):
        self._setNumber(1, value.value)

    def getRank(self):
        return Rank(self._getNumber(2))

    def setRank(self, value):
        self._setNumber(2, value.value)

    def getHasRankInactivity(self):
        return self._getBool(3)

    def setHasRankInactivity(self, value):
        self._setBool(3, value)

    def getDivision(self):
        return Division(self._getNumber(4))

    def setDivision(self, value):
        self._setNumber(4, value.value)

    def getTokensCount(self):
        return self._getNumber(5)

    def setTokensCount(self, value):
        self._setNumber(5, value)

    def getRankList(self):
        return self._getArray(6)

    def setRankList(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRankListType():
        return Rank

    def getQualificationBattleList(self):
        return self._getArray(7)

    def setQualificationBattleList(self, value):
        self._setArray(7, value)

    @staticmethod
    def getQualificationBattleListType():
        return QualificationBattle

    def getMainRewards(self):
        return self._getArray(8)

    def setMainRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getMainRewardsType():
        return Comp7BonusModel

    def getAdditionalRewards(self):
        return self._getArray(9)

    def setAdditionalRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getAdditionalRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(RewardsScreenModel, self)._initialize()
        self._addStringProperty('seasonName')
        self._addNumberProperty('type')
        self._addNumberProperty('rank')
        self._addBoolProperty('hasRankInactivity', False)
        self._addNumberProperty('division')
        self._addNumberProperty('tokensCount', 0)
        self._addArrayProperty('rankList', Array())
        self._addArrayProperty('qualificationBattleList', Array())
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
