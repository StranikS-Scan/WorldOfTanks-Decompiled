# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/event_vehicle_extension.py
import weakref
from functools import partial
import BigWorld
from constants import QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.prb_control.prb_getters import isInEventBattlesQueue
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
_SUPPORTED_ENTITIES = ('RandomEntity',)
_PATCHED_METHODS = ('init', 'fini')
_SWITCHED_METHODS = ('isInQueue', '_doQueue', '_doDequeue', '_makeQueueCtxByAction')

class EventVehicleMeta(type):

    def __call__(cls, *more):
        o = super(EventVehicleMeta, cls).__call__(*more)
        if o.__class__.__name__ in _SUPPORTED_ENTITIES:
            extension = _EventVehicleEntityExtension()
            extension.bound(o)
        return o


class _EventVehicleEntityExtension(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(_EventVehicleEntityExtension, self).__init__()
        self.__entity = None
        self.__patchedMethods = {}
        self.__originalSubscriber = None
        self.__isActivated = False
        self.__isEventsEnabled = False
        return

    def __del__(self):
        LOG_DEBUG('Extension has been deleted')

    def bound(self, entity):
        LOG_DEBUG('Bound event extension')
        self.__entity = weakref.proxy(entity)
        self.__originalSubscriber = self.__getSubscriber()
        entity._extension = self
        for name in _PATCHED_METHODS:
            self._patchMethod(name)

    def unbound(self):
        LOG_DEBUG('Unbound event extension')
        for k, m in self.__patchedMethods.iteritems():
            setattr(self.__entity, k, m)

        delattr(self.__entity, '_extension')
        self.__patchedMethods.clear()
        self.__entity = None
        return

    def init(self, *args, **kwargs):
        LOG_DEBUG('Init event extension')
        self.__isEventsEnabled = self.eventsCache.isEventEnabled()
        self._invalidate(resetSubscription=False)
        rv = self._callOriginalMethod('init', *args, **kwargs)
        self.eventsCache.onSyncCompleted += self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged += self._onCurrentVehicleChanged
        return rv

    def fini(self, *args, **kwargs):
        LOG_DEBUG('Fini event extension')
        self.eventsCache.onSyncCompleted -= self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
        self.__isEventsEnabled = False
        self._invalidate(resetSubscription=True)
        rv = self._callOriginalMethod('fini', *args, **kwargs)
        self.unbound()
        return rv

    def isInQueue(self):
        return isInEventBattlesQueue()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryIDs())
        self.__entity.setQueueType(QUEUE_TYPE.EVENT_BATTLES)
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        self.__entity.setQueueType(QUEUE_TYPE.RANDOMS)
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _makeQueueCtxByAction(self, action=None):
        from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
        return EventBattleQueueCtx(vehInvIDs=[g_currentVehicle.item.invID], waitingID='prebattle/join')

    def _onEventsCacheResync(self):
        if self.__isEventsEnabled != self.eventsCache.isEventEnabled():
            if self.eventsCache.isEventEnabled():
                g_currentVehicle.onChanged += self._onCurrentVehicleChanged
            else:
                g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
            self.__isEventsEnabled = self.eventsCache.isEventEnabled()
            self._invalidate(resetSubscription=True)

    def _onCurrentVehicleChanged(self):
        self._invalidate(resetSubscription=True)

    def _invalidate(self, resetSubscription=False):
        from gui.prb_control.entities.event.pre_queue.entity import EventBattleSubscriber
        activate = self.__isEventsEnabled and g_currentVehicle.isEvent()
        if self.__isActivated != activate:
            prevSubscriber = self.__getSubscriber()
            if activate:
                method = self._patchMethod
                newSubscriber = EventBattleSubscriber()
            else:
                method = self._unpatchMethod
                newSubscriber = self.__originalSubscriber
            for name in _SWITCHED_METHODS:
                method(name)

            if resetSubscription:
                prevSubscriber.unsubscribe(self.__entity)
                newSubscriber.subscribe(self.__entity)
            self.__setSubscriber(newSubscriber)
            self.__isActivated = activate
        LOG_DEBUG('Event Vehicle Entity is {} to entity {}'.format('set' if self.__isActivated else 'unset', self.__entity))

    def _patchMethod(self, name, method=None):
        if method is None:
            method = getattr(self, name)
        if name not in self.__patchedMethods:
            self.__patchedMethods[name] = self.__getEntityMethodWeakRef(name)
            setattr(self.__entity, name, method)
        return

    def _unpatchMethod(self, name):
        if name in self.__patchedMethods:
            setattr(self.__entity, name, self.__patchedMethods[name])
            del self.__patchedMethods[name]

    def _callOriginalMethod(self, name, *args, **kwargs):
        m = self.__patchedMethods[name]
        return m(*args, **kwargs)

    def __getEntityMethodWeakRef(self, name):
        method = getattr(self.__entity, name)
        if not isinstance(method, partial):
            method = partial(getattr(self.__entity.__class__, name), self.__entity)
        return method

    def __getSubscriber(self):
        return getattr(self.__entity, '_subscriber')

    def __setSubscriber(self, subscriber):
        setattr(self.__entity, '_subscriber', subscriber)
