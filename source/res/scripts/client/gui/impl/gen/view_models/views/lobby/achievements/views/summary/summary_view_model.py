# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/summary/summary_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.other_player_info_model import OtherPlayerInfoModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.statistic_item_model import StatisticItemModel

class EditState(Enum):
    AVAILABLE = 'available'
    NOT_ENOUGH_ACHIEVEMENTS = 'notEnoughAchievements'
    DISABLED = 'disabled'


class SummaryViewModel(ViewModel):
    __slots__ = ('onAchievementsSettings',)

    def __init__(self, properties=25, commands=1):
        super(SummaryViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def otherPlayerInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getOtherPlayerInfoType():
        return OtherPlayerInfoModel

    def getIsSummaryEnabled(self):
        return self._getBool(1)

    def setIsSummaryEnabled(self, value):
        self._setBool(1, value)

    def getIsWTREnabled(self):
        return self._getBool(2)

    def setIsWTREnabled(self, value):
        self._setBool(2, value)

    def getIsEditOpened(self):
        return self._getBool(3)

    def setIsEditOpened(self, value):
        self._setBool(3, value)

    def getIsOtherPlayer(self):
        return self._getBool(4)

    def setIsOtherPlayer(self, value):
        self._setBool(4, value)

    def getCurrentRatingRank(self):
        return self._getNumber(5)

    def setCurrentRatingRank(self, value):
        self._setNumber(5, value)

    def getPrevCurrentRatingRank(self):
        return self._getNumber(6)

    def setPrevCurrentRatingRank(self, value):
        self._setNumber(6, value)

    def getCurrentRatingSubRank(self):
        return self._getNumber(7)

    def setCurrentRatingSubRank(self, value):
        self._setNumber(7, value)

    def getPrevCurrentRatingSubRank(self):
        return self._getNumber(8)

    def setPrevCurrentRatingSubRank(self, value):
        self._setNumber(8, value)

    def getPersonalScore(self):
        return self._getNumber(9)

    def setPersonalScore(self, value):
        self._setNumber(9, value)

    def getPrevPersonalScore(self):
        return self._getNumber(10)

    def setPrevPersonalScore(self, value):
        self._setNumber(10, value)

    def getRequiredNumberOfBattles(self):
        return self._getNumber(11)

    def setRequiredNumberOfBattles(self, value):
        self._setNumber(11, value)

    def getBattlesLeftCount(self):
        return self._getNumber(12)

    def setBattlesLeftCount(self, value):
        self._setNumber(12, value)

    def getStatistic(self):
        return self._getArray(13)

    def setStatistic(self, value):
        self._setArray(13, value)

    @staticmethod
    def getStatisticType():
        return StatisticItemModel

    def getEditState(self):
        return EditState(self._getString(14))

    def setEditState(self, value):
        self._setString(14, value.value)

    def getNumberOfUniqueAwards(self):
        return self._getNumber(15)

    def setNumberOfUniqueAwards(self, value):
        self._setNumber(15, value)

    def getTotalAwards(self):
        return self._getNumber(16)

    def setTotalAwards(self, value):
        self._setNumber(16, value)

    def getCurrentMastery(self):
        return self._getNumber(17)

    def setCurrentMastery(self, value):
        self._setNumber(17, value)

    def getTotalMastery(self):
        return self._getNumber(18)

    def setTotalMastery(self, value):
        self._setNumber(18, value)

    def getAchievementRibbonLength(self):
        return self._getNumber(19)

    def setAchievementRibbonLength(self, value):
        self._setNumber(19, value)

    def getSignificantAchievements(self):
        return self._getArray(20)

    def setSignificantAchievements(self, value):
        self._setArray(20, value)

    @staticmethod
    def getSignificantAchievementsType():
        return AchievementModel

    def getRegistrationDate(self):
        return self._getString(21)

    def setRegistrationDate(self, value):
        self._setString(21, value)

    def getLastVisitDate(self):
        return self._getString(22)

    def setLastVisitDate(self, value):
        self._setString(22, value)

    def getLastVisitTime(self):
        return self._getString(23)

    def setLastVisitTime(self, value):
        self._setString(23, value)

    def getIsSuccessfullyEdited(self):
        return self._getBool(24)

    def setIsSuccessfullyEdited(self, value):
        self._setBool(24, value)

    def _initialize(self):
        super(SummaryViewModel, self)._initialize()
        self._addViewModelProperty('otherPlayerInfo', OtherPlayerInfoModel())
        self._addBoolProperty('isSummaryEnabled', True)
        self._addBoolProperty('isWTREnabled', True)
        self._addBoolProperty('isEditOpened', False)
        self._addBoolProperty('isOtherPlayer', False)
        self._addNumberProperty('currentRatingRank', 0)
        self._addNumberProperty('prevCurrentRatingRank', 0)
        self._addNumberProperty('currentRatingSubRank', 0)
        self._addNumberProperty('prevCurrentRatingSubRank', 0)
        self._addNumberProperty('personalScore', 0)
        self._addNumberProperty('prevPersonalScore', 0)
        self._addNumberProperty('requiredNumberOfBattles', 0)
        self._addNumberProperty('battlesLeftCount', 0)
        self._addArrayProperty('statistic', Array())
        self._addStringProperty('editState')
        self._addNumberProperty('numberOfUniqueAwards', 0)
        self._addNumberProperty('totalAwards', 0)
        self._addNumberProperty('currentMastery', 0)
        self._addNumberProperty('totalMastery', 0)
        self._addNumberProperty('achievementRibbonLength', 0)
        self._addArrayProperty('significantAchievements', Array())
        self._addStringProperty('registrationDate', '')
        self._addStringProperty('lastVisitDate', '')
        self._addStringProperty('lastVisitTime', '')
        self._addBoolProperty('isSuccessfullyEdited', False)
        self.onAchievementsSettings = self._addCommand('onAchievementsSettings')
