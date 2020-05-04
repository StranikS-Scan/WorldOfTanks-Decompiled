# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_event_controller.py
import typing
if typing.TYPE_CHECKING:
    from Event import Event

class IGameEventController(object):
    onProgressChanged = None
    onSelectedCommanderChanged = None

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

    def getCommanders(self):
        raise NotImplementedError

    def getCommander(self, commanderId):
        raise NotImplementedError

    def getFront(self, frontId):
        raise NotImplementedError

    def getSelectedCommanderID(self):
        raise NotImplementedError

    def setSelectedCommanderID(self, commanderID):
        raise NotImplementedError

    def getSelectedCommander(self):
        raise NotImplementedError

    def getFronts(self):
        raise NotImplementedError

    def getCurrentFront(self):
        raise NotImplementedError

    def getAvailableCommanderIDs(self):
        raise NotImplementedError

    def getMissionsController(self):
        raise NotImplementedError

    def getShop(self):
        raise NotImplementedError

    def getVehicleSettings(self):
        raise NotImplementedError

    def getHeroTank(self):
        raise NotImplementedError

    def getEventFinishTime(self):
        raise NotImplementedError

    def getEventFinishTimeLeft(self):
        raise NotImplementedError

    def isBerlinStarted(self):
        raise NotImplementedError

    def getLongWaitTime(self):
        raise NotImplementedError

    def getBerlinStartTimeLeft(self):
        raise NotImplementedError

    def getCommanderByEnergy(self, energyID):
        raise NotImplementedError

    @property
    def wasBannerAnimationShown(self):
        raise NotImplementedError

    def setBannerAnimationAsShown(self):
        raise NotImplementedError

    def getCompletedMessages(self, completedQuestIDs, popUps):
        raise NotImplementedError

    def getCompletedMessagesForProgress(self, progress, completedQuestIDs, popUps):
        raise NotImplementedError
