# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_game_event_component.py
import weakref
from functools import wraps
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS

class GameEventComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        super(GameEventComponent, self).__init__(componentSystem)
        self._generalsInBattle = GeneralsInBattle(self)
        self._checkpoints = Checkpoints(self)
        self._lineOfFront = LineOfFront(self)
        self._respawnLives = RespawnLives(self)
        self._teammateVehicleHealth = TeammateVehicleHealth(self)

    def activate(self):
        super(GameEventComponent, self).activate()
        self._generalsInBattle.activate()
        self._checkpoints.activate()
        self._lineOfFront.activate()
        self._respawnLives.activate()
        self._teammateVehicleHealth.activate()

    def deactivate(self):
        self._generalsInBattle.deactivate()
        self._checkpoints.deactivate()
        self._lineOfFront.deactivate()
        self._respawnLives.deactivate()
        self._teammateVehicleHealth.deactivate()
        super(GameEventComponent, self).deactivate()

    def getGeneralsInBattle(self):
        return self._generalsInBattle

    def getCheckpoints(self):
        return self._checkpoints

    def getLineOfFront(self):
        return self._lineOfFront

    def getRespawnLives(self):
        return self._respawnLives

    def getTeammateVehicleHealth(self):
        return self._teammateVehicleHealth


class GameEventData(object):

    def __init__(self, gameEventComponent, dataDictName):
        super(GameEventData, self).__init__()
        self._gameEventComponent = weakref.proxy(gameEventComponent)
        self._dataDictName = dataDictName
        self._eventManager = Event.EventManager()
        self.onUpdated = Event.Event(self._eventManager)

    def activate(self):
        self._gameEventComponent.addSyncDataCallback(ARENA_SYNC_OBJECTS.GAME_EVENT, self._dataDictName, self._onUpdated)

    def deactivate(self):
        self._gameEventComponent.removeSyncDataCallback(ARENA_SYNC_OBJECTS.GAME_EVENT, self._dataDictName, self._onUpdated)
        self._eventManager.clear()

    def hasSyncData(self):
        return self._gameEventComponent.hasSyncDataObjectData(ARENA_SYNC_OBJECTS.GAME_EVENT, self._dataDictName)

    def getSyncData(self):
        return self._gameEventComponent.getSyncDataObjectData(ARENA_SYNC_OBJECTS.GAME_EVENT, self._dataDictName)

    def _onUpdated(self, _):
        self.onUpdated()


def _hasSyncData(default=None):

    def wrapper(func):

        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return default if not self.hasSyncData() else func(self, *args, **kwargs)

        return wrapped

    return wrapper


class Checkpoints(GameEventData):

    def __init__(self, gameEventComponent):
        super(Checkpoints, self).__init__(gameEventComponent, 'checkpoints')

    @_hasSyncData(default=0)
    def getCurrentProgress(self):
        checkpointsData = self.getSyncData()
        return checkpointsData.get('current', 0)

    @_hasSyncData(default=0)
    def getGoalValue(self):
        checkpointsData = self.getSyncData()
        return checkpointsData.get('goal', 0)


class LineOfFront(GameEventData):

    def __init__(self, gameEventComponent):
        super(LineOfFront, self).__init__(gameEventComponent, 'lineOfFront')

    @_hasSyncData(default=0)
    def getHealth(self):
        lineOfFrontData = self.getSyncData()
        return lineOfFrontData.get('health', 0)

    @_hasSyncData(default=0)
    def getMaxHealth(self):
        lineOfFrontData = self.getSyncData()
        return lineOfFrontData.get('maxHealth', 0)


class GeneralsInBattle(GameEventData):

    def __init__(self, gameEventComponent):
        super(GeneralsInBattle, self).__init__(gameEventComponent, 'generals')

    def getGeneralsInfo(self):
        if not self.hasSyncData():
            return {}
        generalsData = self.getSyncData()
        return {avatarID:GeneralInBattle(generalData) for avatarID, generalData in generalsData.iteritems()}

    @_hasSyncData(default=None)
    def getGeneralInfo(self, avatarID):
        generalsData = self.getSyncData()
        rawData = generalsData.get(avatarID, None)
        return None if rawData is None else GeneralInBattle(rawData)


class RespawnLives(GameEventData):

    def __init__(self, gameEventComponent):
        super(RespawnLives, self).__init__(gameEventComponent, 'teammateLives')
        self.onTeammateLivesUpdate = Event.Event(self._eventManager)

    @_hasSyncData(default={})
    def getTeammateLives(self):
        return self.getSyncData()

    def _onUpdated(self, diff):
        super(RespawnLives, self)._onUpdated(diff)
        self.onTeammateLivesUpdate(diff)


class TeammateVehicleHealth(GameEventData):

    def __init__(self, gameEventComponent):
        super(TeammateVehicleHealth, self).__init__(gameEventComponent, 'teammateVehicleHealth')
        self.onTeammateVehicleHealthUpdate = Event.Event(self._eventManager)

    @_hasSyncData(default=0)
    def getTeammateHealth(self, vehID):
        return self.getSyncData().get(vehID, 0)

    def _onUpdated(self, diff):
        super(TeammateVehicleHealth, self)._onUpdated(diff)
        self.onTeammateVehicleHealthUpdate(diff)


class GeneralInBattle(object):

    def __init__(self, data):
        self._data = data

    def getID(self):
        return self._data['generalID']

    def getVehicles(self):
        return self._data['vehicles']

    def getVehicleID(self):
        return self._data['vehicleID']

    def getLevel(self):
        return self._data['generalLevel']
