# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/client_arena_random_event_component.py
import time
import logging
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, MUTATION_SCENARIO_REASON, HALLOWEEN_STATE
_logger = logging.getLogger(__name__)

class RandomEventComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        super(RandomEventComponent, self).__init__(componentSystem)
        self.onScenarioUpdated = Event.Event(self._eventManager)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RANDOM_EVENT, 'scenarios', self._onScenarioUpdated)

    def getScenario(self):
        if not self.hasSyncDataObjectData(ARENA_SYNC_OBJECTS.RANDOM_EVENT, 'scenarios'):
            return None
        else:
            scenarioData = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.RANDOM_EVENT, 'scenarios')
            if scenarioData:
                firstScenarioKey = sorted(scenarioData.keys())[0]
                return Scenario(scenarioData[firstScenarioKey])
            return None

    def destroy(self):
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RANDOM_EVENT, 'scenarios', self._onScenarioUpdated)
        super(RandomEventComponent, self).destroy()

    def _onScenarioUpdated(self, scenarioDiff):
        self.onScenarioUpdated()


class BaseItem(object):

    def __init__(self, data):
        super(BaseItem, self).__init__()
        self._data = data

    def getId(self):
        return self._data['id']

    def getType(self):
        return self._data['type']

    def getSubtype(self):
        return self._data['subtype']

    def getState(self):
        return self._data['state']


class Scenario(BaseItem):

    def __init__(self, data):
        super(Scenario, self).__init__(data)
        if data.get('objectives'):
            self._objectives = [ ObjectiveItem(dict(id=oId, **data)) for oId, data in data['objectives'].iteritems() ]
        else:
            self._objectives = []
        if data.get('buffs'):
            self._buffs = [ BuffItem(dict(id=bId, **data)) for bId, data in data['buffs'].iteritems() ]
        else:
            self._buffs = []
        self._destroyTime = None
        for obj in self._objectives:
            if obj.getDestroyTime():
                self._destroyTime = obj.getDestroyTime()
                break

        return

    def getName(self):
        return self._data['name']

    def getBuffs(self):
        return self._buffs

    def getObjectives(self):
        return self._objectives

    def getTimeLeft(self):
        return max(0, int(self._destroyTime - time.time())) if self._destroyTime else None

    def getReason(self):
        reasons = [ t.getReason() for t in self._buffs if t.getReason() ]
        return reasons[0] if reasons else MUTATION_SCENARIO_REASON.NONE


class ObjectiveItem(BaseItem):

    def getPosition(self):
        return self._data.get('position', None)

    def getAward(self):
        return self._data.get('reward', None)

    def getDestroyTime(self):
        return self._data.get('destroyTime', None)

    def isCompleted(self):
        return self.getState() == HALLOWEEN_STATE.COMPLETED

    def isFailed(self):
        return self.getState() == HALLOWEEN_STATE.FAILED


class BuffItem(BaseItem):

    def getReason(self):
        return self._data.get('reason', None)
