# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampContext.py
from TriggersManager import TRIGGER_TYPE

class IHasID(object):

    def getID(self):
        raise NotImplementedError

    def setID(self, entityID):
        raise NotImplementedError

    def clear(self):
        pass


class IHasTargetID(object):

    def getTargetID(self):
        raise NotImplementedError

    def setTargetID(self, targetID):
        raise NotImplementedError


class HasID(IHasID):

    def __init__(self, entityID=None, entityType=0, **kwargs):
        super(HasID, self).__init__(**kwargs)
        self._id = entityID
        self._type = entityType

    def getID(self):
        return self._id

    def getType(self):
        return self._type

    def setID(self, entityID):
        self._id = entityID


class HasTargetID(IHasTargetID):

    def __init__(self, targetID, **kwargs):
        super(IHasTargetID, self).__init__(**kwargs)
        self._targetID = targetID

    def getTargetID(self):
        return self._targetID

    def setTargetID(self, targetID):
        self._targetID = targetID


class HasIDAndTarget(HasID, HasTargetID):

    def __init__(self, entityID=None, targetID=None, entityType=0):
        super(HasIDAndTarget, self).__init__(entityID=entityID, targetID=targetID, entityType=entityType)
        self._targetID = targetID


class GLOBAL_VAR(object):
    LAST_HISTORY_ID = '_BootcampLastHistoryID'
    SERVICE_MESSAGES_IDS = '_BootcampServiceMessagesIDs'
    PLAYER_VEHICLE_NAME = '_BootcampPlayerVehicleName'
    ALL = (LAST_HISTORY_ID, SERVICE_MESSAGES_IDS, PLAYER_VEHICLE_NAME)


class GLOBAL_FLAG(object):
    IS_FLAGS_RESET = '_BootcampIsFlagsReset'
    SHOW_HISTORY = '_BootcampShowHistory'
    HISTORY_NOT_AVAILABLE = '_BootcampHistoryNotAvailable'
    IN_QUEUE = '_InBootcampQueue'
    ALL_BONUSES_RECEIVED = '_AllBonusesReceived'
    ALL = (IS_FLAGS_RESET,
     SHOW_HISTORY,
     HISTORY_NOT_AVAILABLE,
     IN_QUEUE,
     ALL_BONUSES_RECEIVED)


class EntityMarker(HasID):

    def __init__(self, entityID, createInd=True):
        super(EntityMarker, self).__init__(entityID=entityID)
        self.__createInd = createInd

    def getTypeID(self):
        raise NotImplementedError('EntityMarker.getTypeID not implemented')

    def isIndicatorCreate(self):
        return self.__createInd


class AimMarker(EntityMarker):

    def __init__(self, entityID, modelData, worldData, createInd=True):
        super(AimMarker, self).__init__(entityID, createInd=createInd)
        self.__modelData = modelData
        self.__worldData = worldData

    def getTypeID(self):
        return TRIGGER_TYPE.AIM

    def getModelData(self):
        return self.__modelData

    def getWorldData(self):
        return self.__worldData


class AreaMarker(AimMarker):

    def __init__(self, entityID, modelData, groundData, worldData, createInd=True):
        super(AreaMarker, self).__init__(entityID, modelData, worldData, createInd=createInd)
        self.__groundData = groundData

    def getTypeID(self):
        return TRIGGER_TYPE.AREA

    def getGroundData(self):
        return self.__groundData


class Chapter:

    def __init__(self, filePath):
        self.__entities = {}
        self.__filePath = filePath
        from BootcampParser import BootcampParser as parser
        parser.parse(self)

    def destroy(self):
        self.clear()

    def clear(self):
        self.__entities = {}

    def addEntity(self, entity):
        if entity is not None:
            self.__entities[entity.getID()] = entity
        return

    def getEntity(self, entityID):
        return self.__entities.get(entityID)

    def getFilePath(self):
        return self.__filePath
