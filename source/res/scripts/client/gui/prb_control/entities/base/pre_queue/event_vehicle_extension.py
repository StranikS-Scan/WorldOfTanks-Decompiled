# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/event_vehicle_extension.py
"""
The main goal of Event Vehicle Extension package - provide to developers an easy way to extend
capabilities of standard entities by event specific logic. As a rule all events are based on
the special event vehicles that are enqueued to Event Queue on the server. The extension allows
to patch a entity such so all event vehicles are processed by event rules and standard
vehicles are processed by original rules of the patched entity. The extension logic based
on AOP concept. For details please see descriptions of classes.

To use extension you should follow to a few recommendations:
- update _SUPPORTED_ENTITIES list with entities (class names) that should be patched by
the extension. Take into account that the extension is applied only to entities from this list.
- update _SWITCHED_METHODS list if it don't correspond your needs (if you want to override one
more method from the extended entity). Also don't forget to provide implementation of new
methods. Follow to the existing rules of naming.
- if you need to fully replace method of the patched entity, update _PATCHED_METHODS list.

For more details please see classes descriptions.
"""
import weakref
from functools import partial
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.prb_control.prb_getters import isInEventBattlesQueue
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
_SUPPORTED_ENTITIES = ()
_PATCHED_METHODS = ('init', 'fini')
_SWITCHED_METHODS = ('isInQueue', '_doQueue', '_doDequeue', '_makeQueueCtxByAction')

class EventVehicleMeta(type):
    """
    Meta class the main goal of which is applying vehicle event extension to entity if it is
    in _SUPPORTED_ENTITIES list. The meta class should be present in class declaration if
    expected to extend it or its children with the event vehicle extension. Also names of all
    extended classes should be listed in _SUPPORTED_ENTITIES tuple.
    """

    def __call__(self, *more):
        """
        Called when a new instance of a marked class is instantiated. Apply the extension
        to all supported entities.
        
        :param *more: Arguments list
        :return: A new instance of entity extended with the event vehicle extension, if the
                class name is in _SUPPORTED_ENTITIES list. Otherwise returns original entity
                instance.
        """
        o = super(EventVehicleMeta, self).__call__(*more)
        if o.__class__.__name__ in _SUPPORTED_ENTITIES:
            extension = _EventVehicleEntityExtension()
            extension.bound(o)
        return o


class _EventVehicleEntityExtension(object):
    """
    The class that encapsulates entity logic required for queuing the current vehicle in the
    event queue on the server. The extension can be applied to all entities derived
    from the QueueEntity (QueueEntity is marked with the appropriate meta
    class). All entities which are supposed to be extended through the event vehicle extension
    should correspond to the following conditions:
    - entity should be marked with EventVehicleMeta meta (directly or through inheritance)
    - entity interface should include all methods listed in _PATCHED_METHODS and
    _SWITCHED_METHODS methods.
    
    Extension logic is based on the aspect-oriented programming (AOP). The extension tracks change
    of selected vehicle. If the current selected vehicle is the event vehicle the extension
    substitutes _SWITCHED_METHODS methods of the entity with its own methods. Then if the
    current vehicle is changed, the extension rolls mapping back to the original entity
    methods.
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        """
        Constructor.
        :return: A new instance of _EventVehicleEntityExtension class.
        """
        super(_EventVehicleEntityExtension, self).__init__()
        self.__entity = None
        self.__patchedMethods = {}
        self.__originalSubscriber = None
        self.__isActivated = False
        self.__isEventsEnabled = False
        return

    def bound(self, entity):
        """
        Bounds the given entity implementing _PATCHED_METHODS and _SWITCHED_METHODS methods
        with the extension.
        
        :param entity: A entity corresponding to criteria listed above.
        """
        self.__entity = weakref.proxy(entity)
        self.__originalSubscriber = self.__getSubscriber()
        entity._extension = self
        for name in _PATCHED_METHODS:
            self._patchMethod(name)

    def unbound(self):
        """
        Returns the controlled entity to its original state: restores interface and
        removes temp attributes.
        """
        for k, m in self.__patchedMethods.iteritems():
            setattr(self.__entity, k, m)

        delattr(self.__entity, '_extension')
        self.__patchedMethods.clear()
        self.__entity = None
        return

    def init(self, *args, **kwargs):
        """
        The init method that will replace the original entity method. Initializes the
        inner extension state.
        
        :param args: Arguments that are passed to the original method
        :param kwargs: Arguments that are passed to the original method
        :return: Result of the original method call.
        """
        self.__isEventsEnabled = self.eventsCache.isEventEnabled()
        self._invalidate(resetSubscription=False)
        rv = self._callOriginalMethod('init', *args, **kwargs)
        self.eventsCache.onSyncCompleted += self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged += self._onCurrentVehicleChanged
        return rv

    def fini(self, *args, **kwargs):
        """
        The fini method that will replace the original entity method. Clear inner state and
        resources and restore the entity to its original state.
        
        :param args: Arguments that are passed to the original method
        :param kwargs: Arguments that are passed to the original method
        :return: Result of the original method call.
        """
        self.eventsCache.onSyncCompleted -= self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
        self.__isEventsEnabled = False
        self._invalidate(resetSubscription=True)
        rv = self._callOriginalMethod('fini', *args, **kwargs)
        return rv

    def isInQueue(self):
        """
        Checks if the current vehicle is in the event battle queue. Will replace the original
        entity's method for the event vehicle.
        
        :return: True if the vehicle is queued, otherwise False.
        """
        return isInEventBattlesQueue()

    def _doQueue(self, ctx):
        """
        Puts the vehicle to the event battle queue on the server. Will replace the original
        entity's method for an event vehicle.
        
        :param ctx: An instance of EventVehicleQueueCtx class.
        """
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryIDs())
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        """
        Remove the vehicle from the event battle queue on the server. Will replace the original
        entity's method for the event vehicle.
        
        :param ctx: Unused.
        """
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _makeQueueCtxByAction(self, action=None):
        """
        Makes a context encapsulating data required to queueing vehicle. Will replace the original
        entity's method for an event vehicle.
        
        :param action: Unused.
        :return: Instance of EventVehicleQueueCtx class.
        """
        from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
        return EventBattleQueueCtx(vehInvIDs=[g_currentVehicle.item.invID], waitingID='prebattle/join')

    def _onEventsCacheResync(self):
        """
        Callback to be invoked when the event cache is re-synced.
        """
        if self.__isEventsEnabled != self.eventsCache.isEventEnabled():
            if self.eventsCache.isEventEnabled():
                g_currentVehicle.onChanged += self._onCurrentVehicleChanged
            else:
                g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
            self.__isEventsEnabled = self.eventsCache.isEventEnabled()
            self._invalidate(resetSubscription=True)

    def _onCurrentVehicleChanged(self):
        """
        Callback to be invoked when the current selected vehicle is changed.
        Initiates _SWITCHED_METHODS mapping validation.
        """
        self._invalidate(resetSubscription=True)

    def _invalidate(self, resetSubscription=False):
        """
        Invalidates _SWITCHED_METHODS mapping: for the event vehicle switch the appropriate
        entity's method to the extension methods. For all other vehicles, restore original
        methods.
        """
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
        """
        Updates entity's method with the given method. If the given method is None, updates
        entity's method with the appropriate extension method.
        
        :param name: Name of entity's method to be patched.
        :param method: A callable. Note that signature should match to the original one.
        """
        if method is None:
            method = getattr(self, name)
        if name not in self.__patchedMethods:
            self.__patchedMethods[name] = self.__getEntityMethodWeakRef(name)
            setattr(self.__entity, name, method)
        return

    def _unpatchMethod(self, name):
        """
        Restores entity's method with the given name to the original state.
        
        :param name: Name of entity's method to be restored.
        """
        if name in self.__patchedMethods:
            setattr(self.__entity, name, self.__patchedMethods[name])
            del self.__patchedMethods[name]

    def _callOriginalMethod(self, name, *args, **kwargs):
        """
        Calls the original entity's method.
        
        :param name: Name of entity's method to be called.
        :param args: Arguments to be passed to the original method.
        :param kwargs: Arguments to be passed to the original method.
        :return: Result of the original method call.
        """
        m = self.__patchedMethods[name]
        return m(*args, **kwargs)

    def __getEntityMethodWeakRef(self, name):
        """
        Creates a weak ref to entity's method to avoid memory leaks.
        :param name: method name
        :return: partial weak ref to entity's method with the given name
        """
        method = getattr(self.__entity, name)
        if not isinstance(method, partial):
            method = partial(getattr(self.__entity.__class__, name), self.__entity)
        return method

    def __getSubscriber(self):
        return getattr(self.__entity, '_subscriber')

    def __setSubscriber(self, subscriber):
        setattr(self.__entity, '_subscriber', subscriber)
