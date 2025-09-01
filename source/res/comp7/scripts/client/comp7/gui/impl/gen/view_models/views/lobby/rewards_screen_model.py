# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/rewards_screen_model.py
from enum import Enum, IntEnum
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank, SeasonName
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.comp7_bonus_model import Comp7BonusModel
from comp7.gui.impl.gen.view_models.views.lobby.qualification_battle import QualificationBattle
from comp7.gui.impl.gen.view_models.views.lobby.season_result import SeasonResult
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

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


class ShopInfoType(Enum):
    NONE = 'none'
    OPEN = 'open'
    DISCOUNT = 'discount'


class VideoState(IntEnum):
    NOTSTARTED = 0
    STARTED = 1
    PAUSED = 2
    RESUMED = 3
    ENDED = 4


class RewardsScreenModel(ViewModel):
    __slots__ = ('onClose', 'onOpenShop', 'onChangeType', 'onOpenNextScreen', 'onVideoStateChange')

    def __init__(self, properties=17, commands=5):
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

    def getVideoState(self):
        return VideoState(self._getNumber(13))

    def setVideoState(self, value):
        self._setNumber(13, value.value)

    def getSeasonsResults(self):
        return self._getArray(14)

    def setSeasonsResults(self, value):
        self._setArray(14, value)

    @staticmethod
    def getSeasonsResultsType():
        return SeasonResult

    def getShowSeasonResults(self):
        return self._getBool(15)

    def setShowSeasonResults(self, value):
        self._setBool(15, value)

    def getHasNextScreen(self):
        return self._getBool(16)

    def setHasNextScreen(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(RewardsScreenModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addStringProperty('seasonName')
        self._addNumberProperty('type')
        self._addNumberProperty('rank')
        self._addBoolProperty('hasRankInactivity', False)
        self._addNumberProperty('division')
        self._addStringProperty('shopInfoType', ShopInfoType.NONE.value)
        self._addNumberProperty('tokensCount', 0)
        self._addArrayProperty('rankList', Array())
        self._addArrayProperty('qualificationBattles', Array())
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self._addBoolProperty('hasYearlyVehicle', False)
        self._addNumberProperty('videoState')
        self._addArrayProperty('seasonsResults', Array())
        self._addBoolProperty('showSeasonResults', False)
        self._addBoolProperty('hasNextScreen', False)
        self.onClose = self._addCommand('onClose')
        self.onOpenShop = self._addCommand('onOpenShop')
        self.onChangeType = self._addCommand('onChangeType')
        self.onOpenNextScreen = self._addCommand('onOpenNextScreen')
        self.onVideoStateChange = self._addCommand('onVideoStateChange')
