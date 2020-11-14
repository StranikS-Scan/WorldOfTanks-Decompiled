# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/class_progress_achvs.py
from abstract import ClassProgressAchievement
from abstract.mixins import Deprecated, Fortification, NoProgressBar
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from gui.shared.gui_items.dossier.achievements import validators

class BattleTestedAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(BattleTestedAchievement, self).__init__('battleTested', _AB.TEAM_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('achievesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'battleTested')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'awardCount')


class GuardsmanAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, 'guardsman', _AB.HISTORICAL, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'guardsman')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'weakVehiclesWins')


class ForTacticalOperationsAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ForTacticalOperationsAchievement, self).__init__('forTacticalOperations', _AB.TEAM_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'forTacticalOperations')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getTeam7x7Stats().getWinsCount()


class MarkI100Years(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MarkI100Years, self).__init__('markI100Years', _AB.TOTAL, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)


class MakerOfHistoryAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, 'makerOfHistory', _AB.HISTORICAL, dossier, value)

    def getNextLevelInfo(self):
        return ('pairWinsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'makerOfHistory')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'bothSidesWins')


class MedalAbramsAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalAbramsAchievement, self).__init__('medalAbrams', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalAbrams')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getWinAndSurvived() + dossier.getTeam7x7Stats().getWinAndSurvived() + dossier.getFortBattlesStats().getWinAndSurvived() + dossier.getFortSortiesStats().getWinAndSurvived() + dossier.getGlobalMapStats().getWinAndSurvived()


class MedalCariusAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalCariusAchievement, self).__init__('medalCarius', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalCarius')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getFragsCount() - dossier.getClanStats().getFragsCount() + dossier.getTeam7x7Stats().getFragsCount() + dossier.getFortBattlesStats().getFragsCount() + dossier.getFortSortiesStats().getFragsCount() + dossier.getGlobalMapStats().getFragsCount()


class MedalEkinsAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalEkinsAchievement, self).__init__('medalEkins', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalEkins')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getFrags8p() + dossier.getTeam7x7Stats().getFrags8p() + dossier.getFortBattlesStats().getFrags8p() + dossier.getFortSortiesStats().getFrags8p() + dossier.getGlobalMapStats().getFrags8p()


class MedalKayAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalKayAchievement, self).__init__('medalKay', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('heroesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalKay')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'battleHeroes')


class MedalKnispelAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalKnispelAchievement, self).__init__('medalKnispel', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('damageLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalKnispel')

    def _readCurrentProgressValue(self, dossier):
        random = dossier.getRandomStats()
        clans = dossier.getClanStats()
        fortBattles = dossier.getFortBattlesStats()
        fortSorties = dossier.getFortSortiesStats()
        globalMap = dossier.getGlobalMapStats()
        return random.getDamageDealt() + random.getDamageReceived() - (clans.getDamageDealt() + clans.getDamageReceived()) + dossier.getTeam7x7Stats().getDamageDealt() + dossier.getTeam7x7Stats().getDamageReceived() + fortBattles.getDamageDealt() + fortBattles.getDamageReceived() + fortSorties.getDamageDealt() + fortSorties.getDamageReceived() + globalMap.getDamageDealt() + globalMap.getDamageReceived()


class MedalLavrinenkoAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalLavrinenkoAchievement, self).__init__('medalLavrinenko', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('dropPointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalLavrinenko')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getDroppedCapturePoints() - dossier.getClanStats().getDroppedCapturePoints() + dossier.getTeam7x7Stats().getDroppedCapturePoints() + dossier.getFortBattlesStats().getDroppedCapturePoints() + dossier.getFortSortiesStats().getDroppedCapturePoints() + dossier.getGlobalMapStats().getDroppedCapturePoints()


class MedalLeClercAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalLeClercAchievement, self).__init__('medalLeClerc', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('capturePointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalLeClerc')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getCapturePoints() - dossier.getClanStats().getCapturePoints() + dossier.getTeam7x7Stats().getCapturePoints() + dossier.getFortBattlesStats().getCapturePoints() + dossier.getFortSortiesStats().getCapturePoints() + dossier.getGlobalMapStats().getCapturePoints()


class MedalPoppelAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalPoppelAchievement, self).__init__('medalPoppel', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalPoppel')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getSpottedEnemiesCount() - dossier.getClanStats().getSpottedEnemiesCount() + dossier.getTeam7x7Stats().getSpottedEnemiesCount() + dossier.getFortBattlesStats().getSpottedEnemiesCount() + dossier.getFortSortiesStats().getSpottedEnemiesCount() + dossier.getGlobalMapStats().getSpottedEnemiesCount()


class MedalRotmistrovAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MedalRotmistrovAchievement, self).__init__('medalRotmistrov', _AB.CLAN, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.CLAN, 'medalRotmistrov')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getGlobalMapStats().getBattlesCount()


class RankedStayingPowerAchievement(ClassProgressAchievement):
    __slots__ = ()
    __ACHIEVEMENT_NAME = 'rankedStayingPower'
    __ACHIEVEMENT_COUNTER = 'rankedStayingCounter'
    __DEFAULT_LEVEL = 0

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, self.__ACHIEVEMENT_NAME, _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('stepsLeft', self._lvlUpValue)

    def _readValue(self, dossier):
        return self.__getLvlValue(dossier)

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, self.__ACHIEVEMENT_COUNTER)

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        return cls.__getLvlValue(dossier) > cls.__DEFAULT_LEVEL if dossier is not None else False

    def _readProgressValue(self, dossier):
        return self.__getLvlValue(dossier)

    @classmethod
    def __getLvlValue(cls, dossier):
        return dossier.getRecordValue(_AB.TOTAL, cls.__ACHIEVEMENT_NAME)


class RankedDivisionFighterAchievement(ClassProgressAchievement):
    __slots__ = ()
    __ACHIEVEMENT_NAME = 'rankedDivisionFighter'
    __ACHIEVEMENT_COUNTER = 'rankedDivisionCounter'
    __DEFAULT_LEVEL = 0

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, self.__ACHIEVEMENT_NAME, _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readValue(self, dossier):
        return self.__getLvlValue(dossier)

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, self.__ACHIEVEMENT_COUNTER)

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        return cls.__getLvlValue(dossier) > cls.__DEFAULT_LEVEL if dossier is not None else False

    def _readProgressValue(self, dossier):
        return self.__getLvlValue(dossier)

    @classmethod
    def __getLvlValue(cls, dossier):
        return dossier.getRecordValue(_AB.TOTAL, cls.__ACHIEVEMENT_NAME)


class ReferralProgramClassAchievement(ClassProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReferralProgramClassAchievement, self).__init__('RP2018sergeant', _AB.TOTAL, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.requiresReferralProgram() or validators.alreadyAchieved(cls, name, block, dossier)

    def getNextLevelInfo(self):
        return ('recruitsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'RP2018sergeant')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'RP2018sergeantCounter')


class SoldierOfFortuneAchievement(Fortification, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, 'soldierOfFortune', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'soldierOfFortune')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFortSortiesStats().getWinsCount()


class StormLordAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(StormLordAchievement, self).__init__('stormLord', _AB.FALLOUT, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FALLOUT, 'stormLord')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFalloutStats().getConsumablesFragsCount()


class StrategicOperationsAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(StrategicOperationsAchievement, self).__init__('strategicOperations', _AB.RATED_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.RATED_7X7, 'strategicOperations')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getTotalStats().getWinsCount()


class WinnerLaurelsAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(WinnerLaurelsAchievement, self).__init__('winnerLaurels', _AB.FALLOUT, dossier, value)

    def getNextLevelInfo(self):
        return ('winPointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FALLOUT, 'winnerLaurels')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFalloutStats().getVictoryPoints()
