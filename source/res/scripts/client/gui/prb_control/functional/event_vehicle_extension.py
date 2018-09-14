# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/functional/event_vehicle_extension.py
import weakref
from functools import partial
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.prb_getters import isInEventBattlesQueue
from gui.server_events import g_eventsCache
_SUPPORTED_FUNCTIONALS = ('RandomQueueFunctional',)
_PATCHED_METHODS = ('init', 'fini')
_SWITCHED_METHODS = ('isInQueue', '_doQueue', '_doDequeue', '_makeQueueCtxByAction')

class EventVehicleMeta(type):
    """
    Meta class the main goal of which is applying vehicle event extension to functional if it is
    in _SUPPORTED_FUNCTIONALS list. The meta class should be present in class declaration if
    expected to extend it or its children with the event vehicle extension. Also names of all
    extended classes should be listed in _SUPPORTED_FUNCTIONALS tuple.
    """

    def __call__(self, *more):
        """
        Called when a new instance of a marked class is instantiated. Apply the extension
        to all supported functional.
        
        :param *more: Arguments list
        :return: A new instance of functional extended with the event vehicle extension, if the
                class name is in SUPPORTED_FUNCTIONALS list. Otherwise returns original functional
                instance.
        """
        o = super(EventVehicleMeta, self).__call__(*more)
        if o.__class__.__name__ in _SUPPORTED_FUNCTIONALS:
            extension = _EventVehicleFunctionalExtension()
            extension.bound(o)
        return o


class _EventVehicleFunctionalExtension(object):
    """
    The class that encapsulates functional logic required for queuing the current vehicle in the
    event queue on the server. The extension can be applied to all functionals derived
    from the AccountQueueFunctional (AccountQueueFunctional is marked with the appropriate meta
    class). All functionals which is supposed to be extended through the event vehicle extension
    should correspond to the following conditions:
    - functional should be marked with EventVehicleMeta meta class (directly or through inheritance)
    - functional interface should include all methods listed in _PATCHED_METHODS and
    _SWITCHED_METHODS methods.
    
    Extension logic is based on the aspect-oriented programming (AOP). The extension tracks change
    of selected vehicle. If the current selected vehicle is the event vehicle the extension
    substitutes _SWITCHED_METHODS methods of the functional with its own methods. Then if the
    current vehicle is changed, the extension rolls mapping back to the original functional
    methods.
    """

    def __init__(self):
        """
        Constructor.
        :return: A new instance of _EventVehicleFunctionalExtension class.
        """
        super(_EventVehicleFunctionalExtension, self).__init__()
        self.__functional = None
        self.__patchedMethods = {}
        self.__originalSubscriber = None
        self.__isActivated = False
        self.__isEventsEnabled = False
        return

    def bound(self, functional):
        """
        Bounds the given functional implementing _PATCHED_METHODS and _SWITCHED_METHODS methods
        with the extension.
        
        :param functional: A functional corresponding to criteria listed above.
        """
        self.__functional = weakref.proxy(functional)
        self.__originalSubscriber = self.__getSubscriber()
        functional._extension = self
        for name in _PATCHED_METHODS:
            self._patchMethod(name)

    def unbound(self):
        """
        Returns the controlled functional to its original state: restores interface and
        removes temp attributes.
        """
        for k, m in self.__patchedMethods.iteritems():
            setattr(self.__functional, k, m)

        delattr(self.__functional, '_extension')
        self.__patchedMethods.clear()
        self.__functional = None
        return

    def init(self, *args, **kwargs):
        """
        The init method that will replace the original functional method. Initializes the
        inner extension state.
        
        :param args: Arguments that are passed to the original method
        :param kwargs: Arguments that are passed to the original method
        :return: Result of the original method call.
        """
        self.__isEventsEnabled = g_eventsCache.isEventEnabled()
        self._invalidate(resetSubscription=False)
        rv = self._callOriginalMethod('init', *args, **kwargs)
        g_eventsCache.onSyncCompleted += self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged += self._onCurrentVehicleChanged
        return rv

    def fini(self, *args, **kwargs):
        """
        The fini method that will replace the original functional method. Clear inner state and
        resources and restore the functional to its original state.
        
        :param args: Arguments that are passed to the original method
        :param kwargs: Arguments that are passed to the original method
        :return: Result of the original method call.
        """
        g_eventsCache.onSyncCompleted -= self._onEventsCacheResync
        if self.__isEventsEnabled:
            g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
        self.__isEventsEnabled = False
        self._invalidate(resetSubscription=True)
        rv = self._callOriginalMethod('fini', *args, **kwargs)
        return rv

    def isInQueue(self):
        """
        Checks if the current vehicle is in the event battle queue. Will replace the original
        functional method for the event vehicle.
        
        :return: True if the vehicle is queued, otherwise False.
        """
        return isInEventBattlesQueue()

    def _doQueue(self, ctx):
        """
        Puts the vehicle to the event battle queue on the server. Will replace the original
        functional method for an event vehicle.
        
        :param ctx: An instance of EventVehicleQueueCtx class.
        """
        BigWorld.player().enqueueEventBattles([ctx.getVehicleInventoryID()])
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        """
        Remove the vehicle from the event battle queue on the server. Will replace the original
        functional method for the event vehicle.
        
        :param ctx: Unused.
        """
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _makeQueueCtxByAction(self, action=None):
        """
        Makes a context encapsulating data required to queueing vehicle. Will replace the original
        functional method for an event vehicle.
        
        :param action: Unused.
        :return: Instance of EventVehicleQueueCtx class.
        """
        return pre_queue_ctx.EventVehicleQueueCtx(vehInvID=g_currentVehicle.item.invID, waitingID='prebattle/join')

    def _onEventsCacheResync(self):
        """
        Callback to be invoked when the event cache is re-synced.
        """
        if self.__isEventsEnabled != g_eventsCache.isEventEnabled():
            if g_eventsCache.isEventEnabled():
                g_currentVehicle.onChanged += self._onCurrentVehicleChanged
            else:
                g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
            self.__isEventsEnabled = g_eventsCache.isEventEnabled()
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
        functional method to the extension methods. For all other vehicles, restore original
        methods.
        """
        activate = self.__isEventsEnabled and g_currentVehicle.isPresent() and g_currentVehicle.isEvent()
        if self.__isActivated != activate:
            prevSubscriber = self.__getSubscriber()
            if activate:
                method = self._patchMethod
                from gui.prb_control.functional.event_battles import EventBattlesEventsSubscriber
                newSubscriber = EventBattlesEventsSubscriber()
            else:
                method = self._unpatchMethod
                newSubscriber = self.__originalSubscriber
            for name in _SWITCHED_METHODS:
                method(name)

            if resetSubscription:
                prevSubscriber.unsubscribe(self.__functional)
                newSubscriber.subscribe(self.__functional)
            self.__setSubscriber(newSubscriber)
            self.__isActivated = activate
        LOG_DEBUG('Event Vehicle Functional is {} to functional {}'.format('set' if self.__isActivated else 'unset', self.__functional))

    def _patchMethod(self, name, method=None):
        """
        Updates functional method with the given method. If the given method is None, updates
        functional method with the appropriate extension method.
        
        :param name: Name of functional method to be patched.
        :param method: A callable. Note that signature should match to the original one.
        """
        if method is None:
            method = getattr(self, name)
        if name not in self.__patchedMethods:
            self.__patchedMethods[name] = self.__getFunctionalMethodWeakRef(name)
            setattr(self.__functional, name, method)
        return

    def _unpatchMethod(self, name):
        """
        Restores functional method with the given name to the original state.
        
        :param name: Name of functional method to be restored.
        """
        if name in self.__patchedMethods:
            setattr(self.__functional, name, self.__patchedMethods[name])
            del self.__patchedMethods[name]

    def _callOriginalMethod(self, name, *args, **kwargs):
        """
        Calls the original functional method.
        
        :param name: Name of functional method to be called.
        :param args: Arguments to be passed to the original method.
        :param kwargs: Arguments to be passed to the original method.
        :return: Result of the original method call.
        """
        m = self.__patchedMethods[name]
        return m(*args, **kwargs)

    def __getFunctionalMethodWeakRef(self, name):
        """
        Creates a weak ref to functional's method to avoid memory leaks.
        :param name: method name
        :return: partial weak ref to functional's method with the given name
        """
        method = getattr(self.__functional, name)
        if not isinstance(method, partial):
            method = partial(getattr(self.__functional.__class__, name), self.__functional)
        return method

    def __getSubscriber(self):
        return getattr(self.__functional, '_subscriber')

    def __setSubscriber(self, subscriber):
        setattr(self.__functional, '_subscriber', subscriber)
