# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/training_room_external_handlers.py
from gui.shared.system_factory import collectTrainingRoomExternalHandlers

class TrainingRoomBaseHandler(object):

    def getArenaFilter(self):
        return None

    def getArenaData(self):
        return None

    def getAdditionalInfo(self):
        return None

    def getIcon(self):
        return None

    def getMaxPlayersInTeam(self):
        return None

    def getObserverValidator(self):
        return None

    def getPlayerReadyHandler(self):
        return None

    def getPrebattleLimits(self):
        return None

    def getPrebattlePropertyChecker(self):
        return None

    def getVehicleWatcherType(self):
        return None

    def getClientMessageData(self, errorType=None):
        return None

    def isEnabledForGuiTypeName(self, guiTypeName=None):
        return False


def getTrainingRoomHandler(guiType=None):
    handler = collectTrainingRoomExternalHandlers().get(guiType)
    return handler() if handler is not None else TrainingRoomBaseHandler()


def getAllTrainingRoomHandlers():
    handlers = collectTrainingRoomExternalHandlers()
    return [ handler() for handler in handlers.values() ]
