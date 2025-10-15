# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/skeletons/portal_event_controller.py
import typing
from skeletons.gui.game_control import IGameController, ISeasonProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from Event import Event

class IPortalEventController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onPortalBattleConfigChanged = None
    onVehicleUpgradesMasksChanged = None
    onVehicleExperienceChanged = None
    onComplexityLevelChanged = None
    onMaxAvailableComplexityLevelChanged = None
    onPortalSquadStateChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    @property
    def battleLevel(self):
        raise NotImplementedError

    @battleLevel.setter
    def battleLevel(self, battleLevel):
        raise NotImplementedError

    @property
    def maxComplexityLevel(self):
        raise NotImplementedError

    def setMaxAvailableComplexityLevel(self, maxAvailableComplexityLevel):
        raise NotImplementedError

    def onSquadBattleLevelChanged(self, battleLevel):
        raise NotImplementedError

    def selectRandomBattle(self):
        raise NotImplementedError

    def selectPortal(self):
        raise NotImplementedError

    def getQuestRewards(self, questID):
        raise NotImplementedError

    def getCurrentStampsCount(self):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getDeserializedUpgradeTreeLevel(self, vehicle, level):
        raise NotImplementedError

    def getUpgradeLevel(self, vehicle):
        raise NotImplementedError

    def getCurrentVehicleLevel(self, vehicle):
        raise NotImplementedError

    def getMaxUnlockedLevel(self, vehicle):
        raise NotImplementedError

    def canUpgradeVehicle(self, vehicle):
        raise NotImplementedError

    def getVehicleUpgradeTree(self, vehicle):
        raise NotImplementedError

    def getVehicleUpgradeNodes(self, vehicle):
        raise NotImplementedError

    def getVehicleExperience(self, vehicle):
        raise NotImplementedError

    def getComplexityLevelStatus(self, level):
        raise NotImplementedError

    def isComplexityLevelLocked(self, level):
        raise NotImplementedError

    def getComplexityRecommendedVehicleLvl(self, level):
        raise NotImplementedError

    def getVehicleAbilities(self, vehicle, includeLocked=False):
        raise NotImplementedError

    def getVehicleModifiers(self, vehicle):
        raise NotImplementedError

    def getStampsCountPerLevel(self):
        raise NotImplementedError

    def getSeasonStartEndDate(self):
        raise NotImplementedError

    def getBadges(self):
        raise NotImplementedError

    def getMedals(self):
        raise NotImplementedError

    def getAbilityDuration(self, abilityName):
        raise NotImplementedError

    def getAbilityCooldown(self, abilityName):
        raise NotImplementedError

    def getTotalLevelsCount(self):
        raise NotImplementedError

    def getProgression(self):
        return NotImplementedError

    def onLobbyInited(self, event):
        pass

    def onPrbEnter(self):
        pass

    def onPrbLeave(self):
        pass

    def getOrderedPortalVehicles(self):
        raise NotImplementedError

    def setCurrentSelectedVehicle(self, vehicleID):
        raise NotImplementedError

    def selectNextPortalVehicle(self):
        raise NotImplementedError

    def selectPrevPortalVehicle(self):
        raise NotImplementedError

    def getPortalVehicleByInvID(self, invID):
        raise NotImplementedError

    def getCurrentSelectedVehicle(self):
        raise NotImplementedError

    def getFinishedLevelsCount(self):
        raise NotImplementedError

    def getCurrentStampsAtLevel(self, level):
        raise NotImplementedError

    def upgradeCurrentVehicle(self, upgradeNodeNumber):
        raise NotImplementedError

    def resetCurrentVehicleUpgrades(self):
        raise NotImplementedError

    def showOutroVideo(self):
        raise NotImplementedError

    def showIntroVideo(self):
        raise NotImplementedError
