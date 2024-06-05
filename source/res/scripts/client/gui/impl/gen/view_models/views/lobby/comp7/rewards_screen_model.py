# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/rewards_screen_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.qualification_battle import QualificationBattle
from gui.impl.gen.view_models.views.lobby.comp7.season_result import SeasonResult

class Type(IntEnum):
    RANK = 0
    DIVISION = 1
    RANKREWARDS = 2
    TOKENSREWARDS = 3
    QUALIFICATIONREWARDS = 4
    QUALIFICATIONRANK = 5
    YEARLYVEHICLE = 6
    YEARLYREWARDS = 7
    SELECTEDREWARDS = 8


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


class ShopInfoType(Enum):
    NONE = 'none'
    OPEN = 'open'
    DISCOUNT = 'discount'


class RewardsScreenModel(ViewModel):
    __slots__ = ('onClose', 'onOpenShop')

    def __init__(self, properties=15, commands=2):
        super(RewardsScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getSeasonName(self):
        return SeasonName(self._getString(1))

    def setSeasonName(self, value):
        self._setString(1, value.value)

    def getType(self):
        return Type(self._getNumber(2))

    def setType(self, value):
        self._setNumber(2, value.value)

    def getRank(self):
        return Rank(self._getNumber(3))

    def setRank(self, value):
        self._setNumber(3, value.value)

    def getHasRankInactivity(self):
        return self._getBool(4)

    def setHasRankInactivity(self, value):
        self._setBool(4, value)

    def getDivision(self):
        return Division(self._getNumber(5))

    def setDivision(self, value):
        self._setNumber(5, value.value)

    def getShopInfoType(self):
        return ShopInfoType(self._getString(6))

    def setShopInfoType(self, value):
        self._setString(6, value.value)

    def getTokensCount(self):
        return self._getNumber(7)

    def setTokensCount(self, value):
        self._setNumber(7, value)

    def getRankList(self):
        return self._getArray(8)

    def setRankList(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRankListType():
        return Rank

    def getQualificationBattles(self):
        return self._getArray(9)

    def setQualificationBattles(self, value):
        self._setArray(9, value)

    @staticmethod
    def getQualificationBattlesType():
        return QualificationBattle

    def getMainRewards(self):
        return self._getArray(10)

    def setMainRewards(self, value):
        self._setArray(10, value)

    @staticmethod
    def getMainRewardsType():
        return Comp7BonusModel

    def getAdditionalRewards(self):
        return self._getArray(11)

    def setAdditionalRewards(self, value):
        self._setArray(11, value)

    @staticmethod
    def getAdditionalRewardsType():
        return Comp7BonusModel

    def getHasYearlyVehicle(self):
        return self._getBool(12)

    def setHasYearlyVehicle(self, value):
        self._setBool(12, value)

    def getSeasonsResults(self):
        return self._getArray(13)

    def setSeasonsResults(self, value):
        self._setArray(13, value)

    @staticmethod
    def getSeasonsResultsType():
        return SeasonResult

    def getShowSeasonResults(self):
        return self._getBool(14)

    def setShowSeasonResults(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(RewardsScreenModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addStringProperty('seasonName')
        self._addNumberProperty('type')
        self._addNumberProperty('rank')
        self._addBoolProperty('hasRankInactivity', False)
        self._addNumberProperty('division')
        self._addStringProperty('shopInfoType')
        self._addNumberProperty('tokensCount', 0)
        self._addArrayProperty('rankList', Array())
        self._addArrayProperty('qualificationBattles', Array())
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self._addBoolProperty('hasYearlyVehicle', False)
        self._addArrayProperty('seasonsResults', Array())
        self._addBoolProperty('showSeasonResults', False)
        self.onClose = self._addCommand('onClose')
        self.onOpenShop = self._addCommand('onOpenShop')
