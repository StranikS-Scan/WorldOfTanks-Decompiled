# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/additional_bonus_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel

class PremiumXpBonusRestriction(IntEnum):
    NORESTRICTION = 0
    ISAPPLIED = 1
    INVALIDBATTLETYPE = 2
    ISNOTVICTORY = 3
    DEPRECATEDRESULTS = 4
    NOVEHICLE = 5
    NOCREW = 6
    FASTEREDUCATIONCREWNOTACTIVE = 7
    FASTEREDUCATIONCREWACTIVE = 8
    NOTAPPLYINGERROR = 9


class BonusStates(IntEnum):
    PREMIUMINFO = 0
    PREMIUMBONUS = 1
    PREMIUMEARNINGS = 2
    PREMIUMADVERTISING = 3
    PLUSINFO = 4
    PLUSEARNINGS = 5
    PLUSYOUROCK = 6


class WotPlusTypeEnum(Enum):
    NONE = 'none'
    CORE = 'core'
    PRO = 'pro'


class AdditionalBonusModel(ViewModel):
    __slots__ = ('onPremiumXpBonusApplied', 'onLocalStorageUpdated', 'onShowDetails')

    def __init__(self, properties=16, commands=3):
        super(AdditionalBonusModel, self).__init__(properties=properties, commands=commands)

    def getHasPremium(self):
        return self._getBool(0)

    def setHasPremium(self, value):
        self._setBool(0, value)

    def getWasPremium(self):
        return self._getBool(1)

    def setWasPremium(self, value):
        self._setBool(1, value)

    def getHasAnyPremium(self):
        return self._getBool(2)

    def setHasAnyPremium(self, value):
        self._setBool(2, value)

    def getWotPlusType(self):
        return WotPlusTypeEnum(self._getString(3))

    def setWotPlusType(self, value):
        self._setString(3, value.value)

    def getHasBasicPremium(self):
        return self._getBool(4)

    def setHasBasicPremium(self, value):
        self._setBool(4, value)

    def getHasPenalties(self):
        return self._getBool(5)

    def setHasPenalties(self, value):
        self._setBool(5, value)

    def getIsXpBonusEnabled(self):
        return self._getBool(6)

    def setIsXpBonusEnabled(self, value):
        self._setBool(6, value)

    def getBonusMultiplier(self):
        return self._getNumber(7)

    def setBonusMultiplier(self, value):
        self._setNumber(7, value)

    def getXpDiff(self):
        return self._getNumber(8)

    def setXpDiff(self, value):
        self._setNumber(8, value)

    def getDailyAppliedAdditionalXP(self):
        return self._getNumber(9)

    def setDailyAppliedAdditionalXP(self, value):
        self._setNumber(9, value)

    def getLeftBonusCount(self):
        return self._getNumber(10)

    def setLeftBonusCount(self, value):
        self._setNumber(10, value)

    def getRestriction(self):
        return PremiumXpBonusRestriction(self._getNumber(11))

    def setRestriction(self, value):
        self._setNumber(11, value.value)

    def getState(self):
        return BonusStates(self._getNumber(12))

    def setState(self, value):
        self._setNumber(12, value.value)

    def getLocalStorage(self):
        return self._getString(13)

    def setLocalStorage(self, value):
        self._setString(13, value)

    def getCreditsThreshold(self):
        return self._getNumber(14)

    def setCreditsThreshold(self, value):
        self._setNumber(14, value)

    def getDurationInDays(self):
        return self._getNumber(15)

    def setDurationInDays(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(AdditionalBonusModel, self)._initialize()
        self._addBoolProperty('hasPremium', False)
        self._addBoolProperty('wasPremium', False)
        self._addBoolProperty('hasAnyPremium', False)
        self._addStringProperty('wotPlusType', WotPlusTypeEnum.NONE.value)
        self._addBoolProperty('hasBasicPremium', False)
        self._addBoolProperty('hasPenalties', False)
        self._addBoolProperty('isXpBonusEnabled', False)
        self._addNumberProperty('bonusMultiplier', 0)
        self._addNumberProperty('xpDiff', 0)
        self._addNumberProperty('dailyAppliedAdditionalXP', 0)
        self._addNumberProperty('leftBonusCount', 0)
        self._addNumberProperty('restriction', PremiumXpBonusRestriction.NORESTRICTION.value)
        self._addNumberProperty('state')
        self._addStringProperty('localStorage', '')
        self._addNumberProperty('creditsThreshold', 0)
        self._addNumberProperty('durationInDays', 0)
        self.onPremiumXpBonusApplied = self._addCommand('onPremiumXpBonusApplied')
        self.onLocalStorageUpdated = self._addCommand('onLocalStorageUpdated')
        self.onShowDetails = self._addCommand('onShowDetails')
