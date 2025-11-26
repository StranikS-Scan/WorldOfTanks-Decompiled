# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/comp7_light_controller.py
import Event
from skeletons.gui.game_control import IComp7LightController
from gui.periodic_battles.models import PrimeTimeStatus

class Comp7LightController(IComp7LightController):

    def __init__(self):
        super(Comp7LightController, self).__init__()
        self.__eventsManager = em = Event.EventManager()
        self.onStatusUpdated = Event.Event(em)
        self.onStatusTick = Event.Event(em)
        self.onComp7LightConfigChanged = Event.Event(em)

    @property
    def isBanned(self):
        return False

    @property
    def isOffline(self):
        return False

    @property
    def battleModifiers(self):
        pass

    def fini(self):
        self.__eventsManager.clear()
        super(Comp7LightController, self).fini()

    def isBattlesPossible(self):
        return False

    def isInPrimeTime(self):
        return False

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

    def getCurrentSeason(self, now=None, includePreannounced=False):
        return None

    def getCurrentOrNextActiveCycleNumber(self, season):
        pass

    def getEventEndTimestamp(self):
        return None

    def getModeSettings(self):
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

    def getQuestsTimerLeft(self):
        pass

    def isEnabled(self):
        return False

    def isFrozen(self):
        return True

    def isAvailable(self):
        return False

    def isSuitableVehicle(self, vehicle):
        return False

    def hasSuitableVehicles(self):
        return False

    def isModePrbActive(self):
        return False

    def isProgressionActive(self):
        return False

    def vehicleIsAvailableForBuy(self):
        return False

    def vehicleIsAvailableForRestore(self):
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

    def isBattleModifiersAvailable(self):
        return False
