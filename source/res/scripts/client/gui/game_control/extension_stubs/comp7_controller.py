# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/comp7_controller.py
import Event
from skeletons.gui.game_control import IComp7Controller
from gui.periodic_battles.models import PrimeTimeStatus

class Comp7Controller(IComp7Controller):

    def __init__(self):
        super(Comp7Controller, self).__init__()
        self.__eventsManager = em = Event.EventManager()
        self.onStatusUpdated = Event.Event(em)
        self.onStatusTick = Event.Event(em)
        self.onRankUpdated = Event.Event(em)
        self.onComp7ConfigChanged = Event.Event(em)
        self.onComp7RanksConfigChanged = Event.Event(em)
        self.onBanUpdated = Event.Event(em)
        self.onOfflineStatusUpdated = Event.Event(em)
        self.onQualificationBattlesUpdated = Event.Event(em)
        self.onQualificationStateUpdated = Event.Event(em)
        self.onSeasonPointsUpdated = Event.Event(em)
        self.onComp7RewardsConfigChanged = Event.Event(em)
        self.onHighestRankAchieved = Event.Event(em)
        self.onEntitlementsUpdated = Event.Event(em)
        self.onEntitlementsUpdateFailed = Event.Event(em)
        self.onTournamentBannerStateChanged = Event.Event(em)
        self.onGrandTournamentBannerAvailabilityChanged = Event.Event(em)

    @property
    def rating(self):
        pass

    @property
    def isElite(self):
        return False

    @property
    def isBanned(self):
        return False

    @property
    def banDuration(self):
        pass

    @property
    def isOffline(self):
        return False

    @property
    def leaderboard(self):
        return None

    @property
    def activityPoints(self):
        pass

    @property
    def battleModifiers(self):
        pass

    @property
    def qualificationBattlesNumber(self):
        pass

    @property
    def qualificationBattlesStatuses(self):
        return []

    @property
    def qualificationState(self):
        return None

    @property
    def isTournamentBannerEnabled(self):
        return False

    @property
    def isGrandTournamentBannerEnabled(self):
        return False

    @property
    def remainingOfferTokensNotifications(self):
        return []

    def fini(self):
        self.__eventsManager.clear()

    def isAvailable(self):
        return False

    def isBattlesPossible(self):
        return False

    def isInPrimeTime(self):
        return False

    def isFrozen(self):
        return True

    def isNotSet(self, now=None, peripheryID=None):
        return True

    def isWithinSeasonTime(self, seasonID):
        return False

    def hasAnySeason(self):
        return False

    def hasAvailablePrimeTimeServers(self, now=None):
        return False

    def hasConfiguredPrimeTimeServers(self, now=None):
        return False

    def hasPrimeTimesLeftForCurrentCycle(self):
        return False

    def getClosestStateChangeTime(self, now=None):
        pass

    def getCurrentCycleID(self):
        return None

    def getCurrentCycleInfo(self):
        return (None, False)

    def getCurrentOrNextActiveCycleNumber(self, season):
        pass

    def getEventEndTimestamp(self):
        return None

    def getModeSettings(self):
        return None

    def getRanksConfig(self):
        return None

    def getYearlyRewards(self):
        return None

    def getNextSeason(self, now=None):
        return None

    def getPeriodInfo(self, now=None, peripheryID=None):
        return None

    def getPrimeTimes(self):
        return {}

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        return {}

    def getPrimeTimeStatus(self, now=None, peripheryID=None):
        return (PrimeTimeStatus.NOT_SET, 0, False)

    def getPreviousSeason(self, now=None):
        return None

    def getSeason(self, seasonID):
        return None

    def getSeasonsPassed(self, now=None):
        return []

    def getAllSeasons(self):
        return []

    def getTimer(self, now=None, peripheryID=None):
        pass

    def getLeftTimeToPrimeTimesEnd(self, now=None):
        pass

    def isEnabled(self):
        return False

    def isTrainingEnabled(self):
        return False

    def hasActiveSeason(self, includePreannounced=False):
        return False

    def getActualSeasonNumber(self):
        return None

    def getCurrentSeason(self, now=None, includePreannounced=False):
        return None

    def isQualificationActive(self):
        return False

    def isQualificationResultsProcessing(self):
        return False

    def isQualificationCalculationRating(self):
        return False

    def isQualificationSquadAllowed(self):
        return None

    def preannounceSeasonId(self):
        return None

    def isInPreannounceState(self):
        return False

    def getPreannouncedSeason(self):
        return None

    def getRoleEquipment(self, roleName):
        return None

    def getEquipmentStartLevel(self, roleName):
        return None

    def getRoleEquipmentOverrides(self, roleName):
        return None

    def getPoiEquipmentOverrides(self, poiName):
        return None

    def getViewData(self, viewAlias):
        return {}

    def isSuitableVehicle(self, vehicle):
        return False

    def hasSuitableVehicles(self):
        return False

    def vehicleIsAvailableForBuy(self):
        return False

    def vehicleIsAvailableForRestore(self):
        return False

    def hasPlayableVehicle(self):
        return False

    def isComp7PrbActive(self):
        return False

    def isBattleModifiersAvailable(self):
        return False

    def getAlertBlock(self):
        return (False, None, None)

    def getPlatoonRatingRestriction(self):
        return None

    def getPlatoonMaxRankRestriction(self):
        pass

    def getStatsSeasonsKeys(self):
        return []

    def getReceivedSeasonPoints(self):
        return {}

    def getMaxAvailableSeasonPoints(self):
        pass

    def isQualificationPassedInSeason(self, seasonNumber):
        return False

    def getRatingForSeason(self, seasonNumber):
        pass

    def getMaxRankNumberForSeason(self, seasonNumber=None):
        pass

    def isEliteForSeason(self, seasonNumber=None):
        return False

    def getTournamentBannerAvailability(self):
        return False

    def getTournamentBannerData(self):
        return None

    def updateEntitlementsCache(self, force=False, retryTimes=None):
        pass

    def getGrandTournamentBannerData(self):
        return None

    def getPlatoonRankRestriction(self, squadSize=None):
        pass

    def tryToShowSeasonStatistics(self):
        pass
