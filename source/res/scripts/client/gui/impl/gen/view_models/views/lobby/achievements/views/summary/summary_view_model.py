# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/summary/summary_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.background_model import BackgroundModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.other_player_info_model import OtherPlayerInfoModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.ribbon_model import RibbonModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.statistic_item_model import StatisticItemModel

class EditState(Enum):
    AVAILABLE = 'available'
    NOT_ENOUGH_ACHIEVEMENTS = 'notEnoughAchievements'
    DISABLED = 'disabled'


class SummaryViewModel(ViewModel):
    __slots__ = ('onAchievementsSettings', 'onCustomizationConfirmed', 'onCustomizationDiscard', 'onSetBackgroundDraft', 'onSetRibbonDraft', 'onSetIsInCustomizationMode')

    def __init__(self, properties=35, commands=6):
        super(SummaryViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def otherPlayerInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getOtherPlayerInfoType():
        return OtherPlayerInfoModel

    @property
    def background(self):
        return self._getViewModel(1)

    @staticmethod
    def getBackgroundType():
        return BackgroundModel

    @property
    def backgroundDraft(self):
        return self._getViewModel(2)

    @staticmethod
    def getBackgroundDraftType():
        return BackgroundModel

    @property
    def ribbon(self):
        return self._getViewModel(3)

    @staticmethod
    def getRibbonType():
        return RibbonModel

    @property
    def ribbonDraft(self):
        return self._getViewModel(4)

    @staticmethod
    def getRibbonDraftType():
        return RibbonModel

    def getIsSummaryEnabled(self):
        return self._getBool(5)

    def setIsSummaryEnabled(self, value):
        self._setBool(5, value)

    def getIsWTREnabled(self):
        return self._getBool(6)

    def setIsWTREnabled(self, value):
        self._setBool(6, value)

    def getIsEditOpened(self):
        return self._getBool(7)

    def setIsEditOpened(self, value):
        self._setBool(7, value)

    def getIsOtherPlayer(self):
        return self._getBool(8)

    def setIsOtherPlayer(self, value):
        self._setBool(8, value)

    def getCurrentRatingRank(self):
        return self._getNumber(9)

    def setCurrentRatingRank(self, value):
        self._setNumber(9, value)

    def getPrevCurrentRatingRank(self):
        return self._getNumber(10)

    def setPrevCurrentRatingRank(self, value):
        self._setNumber(10, value)

    def getCurrentRatingSubRank(self):
        return self._getNumber(11)

    def setCurrentRatingSubRank(self, value):
        self._setNumber(11, value)

    def getPrevCurrentRatingSubRank(self):
        return self._getNumber(12)

    def setPrevCurrentRatingSubRank(self, value):
        self._setNumber(12, value)

    def getPersonalScore(self):
        return self._getNumber(13)

    def setPersonalScore(self, value):
        self._setNumber(13, value)

    def getPrevPersonalScore(self):
        return self._getNumber(14)

    def setPrevPersonalScore(self, value):
        self._setNumber(14, value)

    def getRequiredNumberOfBattles(self):
        return self._getNumber(15)

    def setRequiredNumberOfBattles(self, value):
        self._setNumber(15, value)

    def getBattlesLeftCount(self):
        return self._getNumber(16)

    def setBattlesLeftCount(self, value):
        self._setNumber(16, value)

    def getStatistic(self):
        return self._getArray(17)

    def setStatistic(self, value):
        self._setArray(17, value)

    @staticmethod
    def getStatisticType():
        return StatisticItemModel

    def getEditState(self):
        return EditState(self._getString(18))

    def setEditState(self, value):
        self._setString(18, value.value)

    def getNumberOfUniqueAwards(self):
        return self._getNumber(19)

    def setNumberOfUniqueAwards(self, value):
        self._setNumber(19, value)

    def getTotalAwards(self):
        return self._getNumber(20)

    def setTotalAwards(self, value):
        self._setNumber(20, value)

    def getCurrentMastery(self):
        return self._getNumber(21)

    def setCurrentMastery(self, value):
        self._setNumber(21, value)

    def getTotalMastery(self):
        return self._getNumber(22)

    def setTotalMastery(self, value):
        self._setNumber(22, value)

    def getAchievementRibbonLength(self):
        return self._getNumber(23)

    def setAchievementRibbonLength(self, value):
        self._setNumber(23, value)

    def getSignificantAchievements(self):
        return self._getArray(24)

    def setSignificantAchievements(self, value):
        self._setArray(24, value)

    @staticmethod
    def getSignificantAchievementsType():
        return AchievementModel

    def getRegistrationDate(self):
        return self._getString(25)

    def setRegistrationDate(self, value):
        self._setString(25, value)

    def getLastVisitDate(self):
        return self._getString(26)

    def setLastVisitDate(self, value):
        self._setString(26, value)

    def getLastVisitTime(self):
        return self._getString(27)

    def setLastVisitTime(self, value):
        self._setString(27, value)

    def getIsSuccessfullyEdited(self):
        return self._getBool(28)

    def setIsSuccessfullyEdited(self, value):
        self._setBool(28, value)

    def getIsCustomizationButtonVisible(self):
        return self._getBool(29)

    def setIsCustomizationButtonVisible(self, value):
        self._setBool(29, value)

    def getIsCustomizationButtonEnabled(self):
        return self._getBool(30)

    def setIsCustomizationButtonEnabled(self, value):
        self._setBool(30, value)

    def getCustomizationButtonTooltip(self):
        return self._getString(31)

    def setCustomizationButtonTooltip(self, value):
        self._setString(31, value)

    def getBackgroundOptions(self):
        return self._getArray(32)

    def setBackgroundOptions(self, value):
        self._setArray(32, value)

    @staticmethod
    def getBackgroundOptionsType():
        return BackgroundModel

    def getRibbonOptions(self):
        return self._getArray(33)

    def setRibbonOptions(self, value):
        self._setArray(33, value)

    @staticmethod
    def getRibbonOptionsType():
        return RibbonModel

    def getIsInCustomizationMode(self):
        return self._getBool(34)

    def setIsInCustomizationMode(self, value):
        self._setBool(34, value)

    def _initialize(self):
        super(SummaryViewModel, self)._initialize()
        self._addViewModelProperty('otherPlayerInfo', OtherPlayerInfoModel())
        self._addViewModelProperty('background', BackgroundModel())
        self._addViewModelProperty('backgroundDraft', BackgroundModel())
        self._addViewModelProperty('ribbon', RibbonModel())
        self._addViewModelProperty('ribbonDraft', RibbonModel())
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
        self._addBoolProperty('isCustomizationButtonVisible', False)
        self._addBoolProperty('isCustomizationButtonEnabled', False)
        self._addStringProperty('customizationButtonTooltip', '')
        self._addArrayProperty('backgroundOptions', Array())
        self._addArrayProperty('ribbonOptions', Array())
        self._addBoolProperty('isInCustomizationMode', False)
        self.onAchievementsSettings = self._addCommand('onAchievementsSettings')
        self.onCustomizationConfirmed = self._addCommand('onCustomizationConfirmed')
        self.onCustomizationDiscard = self._addCommand('onCustomizationDiscard')
        self.onSetBackgroundDraft = self._addCommand('onSetBackgroundDraft')
        self.onSetRibbonDraft = self._addCommand('onSetRibbonDraft')
        self.onSetIsInCustomizationMode = self._addCommand('onSetIsInCustomizationMode')
