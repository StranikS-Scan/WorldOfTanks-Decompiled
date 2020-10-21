# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_game_event_component.py
import weakref
from functools import wraps
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, EVENT_SOULS_CHANGE_REASON
import BigWorld

class GameEventComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        super(GameEventComponent, self).__init__(componentSystem)
        self._teammateVehicleHealth = TeammateVehicleHealth(self)
        self._teammateResurrectEquipment = TeammateResurrectEquipment(self)
        self._scenarioAnimationTriggers = ScenarioAnimationTriggers(self)
        self._environmentData = EnvironmentEventData(self)
        self._souls = Souls(self)
        self._soulCollector = SoulCollector(self)
        self._ecpState = ECPState(self)
        self._nearbyIndicator = NearbyIndicatorData(self)
        self._enemySpottedData = EnemySpottedData(self)

    def activate(self):
        super(GameEventComponent, self).activate()
        self._teammateVehicleHealth.activate()
        self._teammateResurrectEquipment.activate()
        self._scenarioAnimationTriggers.activate()
        self._environmentData.activate()
        self._souls.activate()
        self._soulCollector.activate()
        self._nearbyIndicator.activate()
        self._ecpState.activate()
        self._enemySpottedData.activate()

    def deactivate(self):
        self._scenarioAnimationTriggers.deactivate()
        self._teammateVehicleHealth.deactivate()
        self._teammateResurrectEquipment.deactivate()
        self._environmentData.deactivate()
        self._souls.deactivate()
        self._soulCollector.deactivate()
        self._nearbyIndicator.deactivate()
        self._ecpState.deactivate()
        self._enemySpottedData.deactivate()
        super(GameEventComponent, self).deactivate()

    def getTeammateVehicleHealth(self):
        return self._teammateVehicleHealth

    def getTeammateResurrectEquipment(self):
        return self._teammateResurrectEquipment

    def scenarioAnimationTriggers(self):
        return self._scenarioAnimationTriggers

    def getEnvironmentData(self):
        return self._environmentData

    def getSouls(self):
        return self._souls

    def getSoulCollector(self):
        return self._soulCollector

    @property
    def ecpState(self):
        return self._ecpState

    def getNearbyIndicator(self):
        return self._nearbyIndicator

    def getEnemySpottedData(self):
        return self._enemySpottedData


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


class EnemySpottedData(GameEventData):

    def __init__(self, gameEventComponent):
        super(EnemySpottedData, self).__init__(gameEventComponent, 'enemySpottedData')
        self.onEnemySpottedDataUpdate = Event.Event(self._eventManager)

    def checkBossVehicleSpotted(self):
        return False if not self.hasSyncData() else self.getSyncData().get('bossVehicleSpotted', False)

    def checkBomberVehicleSpotted(self):
        return False if not self.hasSyncData() else self.getSyncData().get('bomberVehicleSpotted', 0)

    def _onUpdated(self, diff):
        super(EnemySpottedData, self)._onUpdated(diff)
        self.onEnemySpottedDataUpdate(diff)


class NearbyIndicatorData(GameEventData):

    def __init__(self, gameEventComponent):
        super(NearbyIndicatorData, self).__init__(gameEventComponent, 'nearbyVehicleIndicator')
        self.onNearByIndicatorChanged = Event.Event(self._eventManager)

    def getIndicatorValue(self, avatarID):
        return 0 if not self.hasSyncData() else int(self.getSyncData().get(avatarID, 0))


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


class TeammateResurrectEquipment(GameEventData):

    def __init__(self, gameEventComponent):
        super(TeammateResurrectEquipment, self).__init__(gameEventComponent, 'teammateResurrectEquipment')
        self.onTeammateResurrectUpdate = Event.Event(self._eventManager)

    @_hasSyncData(default=False)
    def getTeammateResurrect(self, vehID):
        return self.getSyncData().get(vehID, False)

    def _onUpdated(self, diff):
        super(TeammateResurrectEquipment, self)._onUpdated(diff)
        self.onTeammateResurrectUpdate(diff)


class ScenarioAnimationTriggers(GameEventData):

    def __init__(self, gameEventComponent):
        super(ScenarioAnimationTriggers, self).__init__(gameEventComponent, 'scenarioAnimationTriggers')
        self.onScenarioAnimationTriggersUpdate = Event.Event(self._eventManager)

    @_hasSyncData(default=set())
    def getTriggers(self):
        return {trigger for trigger, enabled in self.getSyncData().iteritems() if enabled}

    def _onUpdated(self, diff):
        super(ScenarioAnimationTriggers, self)._onUpdated(diff)
        for trigger, enabled in diff.iteritems():
            if enabled:
                BigWorld.wg_setTrigger(trigger)

        self.onScenarioAnimationTriggersUpdate(diff)


class Souls(GameEventData):

    def __init__(self, gameEventComponent):
        super(Souls, self).__init__(gameEventComponent, 'souls')
        self.onSoulsChanged = Event.Event(self._eventManager)

    def getSouls(self, vehID):
        return self._getSoulData(vehID)[0]

    def getLastSoulsModifiedReason(self, vehID):
        return self._getSoulData(vehID)[1]

    @_hasSyncData(default=(0, EVENT_SOULS_CHANGE_REASON.NONE))
    def _getSoulData(self, vehID):
        return self.getSyncData().get(vehID, (0, EVENT_SOULS_CHANGE_REASON.NONE))

    def _onUpdated(self, diff):
        super(Souls, self)._onUpdated(diff)
        self.onSoulsChanged(diff)


class SoulCollector(GameEventData):

    def __init__(self, gameEventComponent):
        super(SoulCollector, self).__init__(gameEventComponent, 'ecpSouls')
        self.onSoulsChanged = Event.Event(self._eventManager)

    @_hasSyncData(default=(0, EVENT_SOULS_CHANGE_REASON.NONE))
    def getSoulCollectorData(self):
        return self.getSyncData()

    def _onUpdated(self, diff):
        super(SoulCollector, self)._onUpdated(diff)
        self.onSoulsChanged(diff)


class ECPState(GameEventData):

    def __init__(self, gameEventComponent):
        super(ECPState, self).__init__(gameEventComponent, 'ecpState')

    def getStateByID(self, ecpID):
        return 0 if not self.hasSyncData() else self.getSyncData().get(ecpID, None)

    def getStates(self):
        return {} if not self.hasSyncData() else self.getSyncData()


class EnvironmentEventData(GameEventData):

    def __init__(self, gameEventComponent):
        super(EnvironmentEventData, self).__init__(gameEventComponent, 'environment')
        self.onEnvironmentEventIDUpdate = Event.Event(self._eventManager)

    def getCurrentEnvironmentID(self):
        return 0 if not self.hasSyncData() else int(self.getSyncData().get('currentID', 0))

    def getMaxEnvironmentID(self):
        return 0 if not self.hasSyncData() else int(self.getSyncData().get('maxID', 0))

    def _onUpdated(self, diff):
        super(EnvironmentEventData, self)._onUpdated(diff)
        envID = diff.get('currentID')
        if envID is not None:
            self.onEnvironmentEventIDUpdate(envID)
        return
