# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/client_arena_event_points_component.py
import logging
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS
_logger = logging.getLogger(__name__)

class EventPointsComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        super(EventPointsComponent, self).__init__(componentSystem)
        self.__currentEventPoints = {}
        self.__totalEventPoints = {}
        _logger.debug('EventPointsComponent instance created.')
        self.onCurrentEventPointsUpdated = Event.Event(self._eventManager)
        self.onTotalEventPointsUpdated = Event.Event(self._eventManager)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.EVENT_POINTS, 'currentEventPoints', self._onCurrentEventPointsUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.EVENT_POINTS, 'totalEventPoints', self._onTotalEventPointsUpdated)

    @property
    def currentEventPoints(self):
        return self.__currentEventPoints

    @property
    def totalEventPoints(self):
        return self.__totalEventPoints

    def destroy(self):
        ClientArenaComponent.destroy(self)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.EVENT_POINTS, 'currentEventPoints', self._onCurrentEventPointsUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.EVENT_POINTS, 'totalEventPoints', self._onTotalEventPointsUpdated)

    def getVehicleEventPoints(self, vehicleID):
        for vehicles in self.__currentEventPoints.itervalues():
            if vehicleID in vehicles:
                return vehicles[vehicleID]

        return None

    def _onCurrentEventPointsUpdated(self, eventPointsDiff):
        _logger.debug('onCurrentEventPointsUpdated. Diff is: %s', eventPointsDiff)
        if eventPointsDiff:
            for key, value in eventPointsDiff.iteritems():
                self.__currentEventPoints.setdefault(key, {}).update(value)

            self.onCurrentEventPointsUpdated(self.__currentEventPoints)

    def _onTotalEventPointsUpdated(self, totalEventPoints):
        _logger.debug('onTotalEventPointsUpdated. New value: %s', totalEventPoints)
        if totalEventPoints:
            self.__totalEventPoints.update(totalEventPoints)
            self.onTotalEventPointsUpdated(self.__totalEventPoints)
