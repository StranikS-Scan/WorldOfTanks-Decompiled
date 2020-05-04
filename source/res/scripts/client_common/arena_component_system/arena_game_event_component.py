# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_game_event_component.py
import weakref
from functools import wraps
import logging
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, EVENT_SOULS_CHANGE_REASON
import BigWorld
_logger = logging.getLogger(__name__)

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
        self._activeTimers = ActiveTimers(self)
        self._minimapInfo = MinimapInfo(self)
        self._areaPointMarker = AreaPointMarker(self)
        self._areaVehicleMarker = AreaVehicleMarker(self)
        self._behaviorMarker = BehaviorMarker(self)
        self._highlightMarkers = HighlightMarkers(self)
        self._teammateLifecycle = TeammateLifecycle(self)
        self._scenarioGoals = ScenarioGoals(self)

    def getComponents(self):
        return (self._teammateVehicleHealth,
         self._teammateResurrectEquipment,
         self._scenarioAnimationTriggers,
         self._environmentData,
         self._souls,
         self._soulCollector,
         self._ecpState,
         self._nearbyIndicator,
         self._enemySpottedData,
         self._activeTimers,
         self._areaPointMarker,
         self._areaVehicleMarker,
         self._behaviorMarker,
         self._highlightMarkers,
         self._teammateLifecycle,
         self._scenarioGoals,
         self._minimapInfo)

    def activate(self):
        super(GameEventComponent, self).activate()
        for component in self.getComponents():
            component.activate()

    def deactivate(self):
        for component in self.getComponents():
            component.deactivate()

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

    def getAreaPointMarker(self):
        return self._areaPointMarker

    def getAreaVehicleMarker(self):
        return self._areaVehicleMarker

    def getBehaviorMarker(self):
        return self._behaviorMarker

    def getHighlightMarkers(self):
        return self._highlightMarkers

    @property
    def ecpState(self):
        return self._ecpState

    def getNearbyIndicator(self):
        return self._nearbyIndicator

    def getEnemySpottedData(self):
        return self._enemySpottedData

    @property
    def activeTimers(self):
        return self._activeTimers

    @property
    def minimapInfo(self):
        return self._minimapInfo

    def getTeammateLifecycle(self):
        return self._teammateLifecycle

    def getScenarioGoals(self):
        return self._scenarioGoals


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

    def _onUpdated(self, diff):
        super(EnvironmentEventData, self)._onUpdated(diff)
        envID = diff.get('currentID')
        if envID is not None:
            self.onEnvironmentEventIDUpdate(envID)
        return


class ActiveTimers(GameEventData):

    def __init__(self, gameEventComponent):
        super(ActiveTimers, self).__init__(gameEventComponent, 'activeTimers')
        self.onActiveTimersUpdated = Event.Event(self._eventManager)

    @_hasSyncData(default=None)
    def getTimerData(self, timerId):
        return self.getSyncData().get(timerId, None)

    def _onUpdated(self, diff):
        super(ActiveTimers, self)._onUpdated(diff)
        self.onActiveTimersUpdated(diff)


class AreaPointMarker(GameEventData):

    def __init__(self, gameEventComponent):
        super(AreaPointMarker, self).__init__(gameEventComponent, 'areaPointMarker')

    @_hasSyncData(default={})
    def getParams(self):
        marker = self.getSyncData()
        return marker


class AreaVehicleMarker(GameEventData):

    def __init__(self, gameEventComponent):
        super(AreaVehicleMarker, self).__init__(gameEventComponent, 'areaVehicleMarker')

    @_hasSyncData(default={})
    def getParams(self):
        return self.getSyncData()


class BehaviorMarker(GameEventData):

    def __init__(self, gameEventComponent):
        super(BehaviorMarker, self).__init__(gameEventComponent, 'behaviorMarker')

    @_hasSyncData(default={})
    def getParams(self):
        return self.getSyncData()


class TeammateLifecycle(GameEventData):

    def __init__(self, gameEventComponent):
        super(TeammateLifecycle, self).__init__(gameEventComponent, 'teammateLifecycle')

    @_hasSyncData(default={})
    def getParams(self):
        return self.getSyncData()


class HighlightMarkers(GameEventData):

    def __init__(self, gameEventComponent):
        super(HighlightMarkers, self).__init__(gameEventComponent, 'highlightMarkers')

    @_hasSyncData(default={})
    def getParams(self):
        return self.getSyncData()


class ScenarioGoals(GameEventData):

    def __init__(self, gameEventComponent):
        super(ScenarioGoals, self).__init__(gameEventComponent, 'scenarioGoals')
        self._goals = {}
        self.onScenarioGoalsChanged = Event.Event(self._eventManager)

    def _onUpdated(self, diff):
        super(ScenarioGoals, self)._onUpdated(diff)
        self.onScenarioGoalsChanged()
        _logger.debug('Goal update receive')

    @_hasSyncData(default={})
    def getParams(self):
        return self.getSyncData()

    def getGoalsInfo(self):
        currentGoal = len(self.getParams().get('goals', {}))
        totalGoals = self.getParams().get('maxCount', 0)
        return (currentGoal, totalGoals)

    def getLastGoal(self):
        params = self.getParams().get('goals', {})
        if not params:
            return None
        else:
            lastID = max(map(int, params.keys()))
            return params[str(lastID)]


class MinimapInfo(GameEventData):
    DEFAULT_MINIMAP_ID = 'mmap'

    def __init__(self, gameEventComponent):
        super(MinimapInfo, self).__init__(gameEventComponent, 'minimapInfo')

    @_hasSyncData(default=None)
    def getMinimapId(self):
        return self.getSyncData().get('minimapId', self.DEFAULT_MINIMAP_ID)
