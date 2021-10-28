# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_event_controller.py


class IGameEventController(object):
    onSelectedDifficultyLevelChanged = None
    onSquadDifficultyLevelChanged = None
    onRewardBoxUpdated = None
    onRewardBoxKeyUpdated = None
    onIngameEventsUpdated = None
    onQuestsUpdated = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def getEnergy(self):
        raise NotImplementedError

    def getVehiclesForRent(self):
        raise NotImplementedError

    def getVehiclesController(self):
        raise NotImplementedError

    def getDifficultyController(self):
        raise NotImplementedError

    def getMissionsController(self):
        raise NotImplementedError

    def getEventRewardController(self):
        raise NotImplementedError

    def getShop(self):
        raise NotImplementedError

    def getVehicleSettings(self):
        return NotImplementedError

    def needEventCrew(self, intCD):
        return NotImplementedError

    def getEventCrew(self, vehicle):
        return NotImplementedError

    def getDifficultyLevels(self):
        raise NotImplementedError

    def setSelectedDifficultyLevel(self, difficultyLevel):
        raise NotImplementedError

    def getSelectedDifficultyLevel(self):
        raise NotImplementedError

    def hasDifficultyLevelToken(self, difficultyID):
        raise NotImplementedError

    def getBattlesCountToAnimateNextLevel(self):
        raise NotImplementedError

    def getSquadDifficultyLevel(self):
        raise NotImplementedError

    def setSquadDifficultyLevel(self, level):
        raise NotImplementedError

    def getMaxUnlockedDifficultyLevel(self):
        raise NotImplementedError

    def getBattlesCountByDifficultyLevel(self, level):
        raise NotImplementedError

    def isEventCurrentDateActive(self):
        raise NotImplementedError

    def isEventActiveAndEnable(self):
        raise NotImplementedError
