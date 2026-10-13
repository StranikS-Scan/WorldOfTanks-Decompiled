# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/entity_events.py
from __future__ import absolute_import
import typing
import weakref
from events_handler import EventsHandler
from events_container import EventsContainer
from debug_utils import LOG_ERROR
from constants import IS_DEVELOPMENT
if typing.TYPE_CHECKING:
    import BigWorld
    from Event import SafeEvent

class EntityEventsCoreIntegration(EventsHandler):

    def __init__(self, entity):
        super(EntityEventsCoreIntegration, self).__init__()
        self.spaceID = entity.spaceID
        self.entityID = entity.id
        self.entityGO = entity.entityGameObject


class EntityEvents(EventsContainer):
    __slots__ = ('onDynComponentGroupAdded', 'onDynComponentGroupRemoved', '_entityRef')

    def __init__(self, entity=None):
        super(EntityEvents, self).__init__()
        self._entityRef = weakref.ref(entity) if entity else None
        self.onDynComponentGroupAdded = self._createEvent()
        self.onDynComponentGroupRemoved = self._createEvent()
        return

    def createEvent(self):
        return self._createEvent()

    def _createCoreIntegration(self):
        entity = self._entityRef() if self._entityRef else None
        if entity is None or entity.entityGameObject is None or not entity.entityGameObject.valid:
            LOG_ERROR('[EntityEvents] Could not create core integration. Entity is not ready or already destroyed.')
            return
        else:
            integration = self._createIntegrationInstance(entity)
            if integration is None:
                LOG_ERROR('[EntityEvents] Could not create core integration. Core integration object not provided.')
                return
            integration.subscribeTo(self, raiseException=IS_DEVELOPMENT)
            return integration

    def _createIntegrationInstance(self, entity):
        return None
