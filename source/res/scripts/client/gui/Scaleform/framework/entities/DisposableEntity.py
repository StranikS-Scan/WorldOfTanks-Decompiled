# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DisposableEntity.py
from Event import Event, EventManager
from debug_utils import LOG_DEBUG

class EntityState(object):
    """
    Enumeration of possible DisposableEntity states.
    """
    UNDEFINED = 0
    CREATING = 1
    CREATED = 2
    DISPOSING = 3
    DISPOSED = 4


class DisposableEntity(object):
    """
    The class provides implementation of disposable object concept. All derived classes should
    override protected _populate (to initialize object) and _dispose (to clean up resources)
    methods.
    Disposable object goes through several states during its lifetime. For details please see
    EntityState description.
    Note that disposable object cannot be destroyed during its initialization. If object is
    destroyed when _populate method is performed, destroy call is postponed till  _populate method
    completion.
    """

    def __init__(self):
        super(DisposableEntity, self).__init__()
        self.__eManager = EventManager()
        self.onCreate = Event(self.__eManager)
        self.onCreated = Event(self.__eManager)
        self.onDispose = Event(self.__eManager)
        self.onDisposed = Event(self.__eManager)
        self.__lcState = EntityState.UNDEFINED
        self.__postponedState = EntityState.UNDEFINED

    def getState(self):
        return self.__lcState

    def create(self):
        """
        Initializes object.
        """
        if self.__lcState in (EntityState.UNDEFINED, EntityState.DISPOSED):
            self.__changeStateTo(EntityState.CREATING)
            self.onCreate(self)
            self._populate()
            self.__changeStateTo(EntityState.CREATED)
            self.onCreated(self)
            self.__invalidatePostponedState()
        elif self.__lcState == EntityState.DISPOSING:
            LOG_DEBUG('Create call is postponed for {} object. Disposing is in progress.'.format(self))
            self.__postponedState = EntityState.CREATING
        else:
            LOG_DEBUG('Entity {} is already created! Current state {}.'.format(self, self.__lcState))

    def validate(self, *args, **kwargs):
        """
        Re-initializes object. If method is called without args and kwargs, it means that it is just required to
        invalidate the inner state.
        """
        if self.__lcState == EntityState.CREATED:
            self.__changeStateTo(EntityState.CREATING)
            self._invalidate(*args, **kwargs)
            self.__changeStateTo(EntityState.CREATED)
            self.__invalidatePostponedState()
        elif self.__lcState in (EntityState.UNDEFINED, EntityState.DISPOSING, EntityState.DISPOSED):
            LOG_DEBUG('Invalidate call is skipped because object {} is destroyed or has not been created yet. Current state {}.'.format(self, self.__lcState))
        else:
            LOG_DEBUG('Invalidate call is skipped because initialization of object {} is in progress.'.format(self))

    def destroy(self):
        """
        Destroy object.
        """
        if self.__lcState in (EntityState.UNDEFINED, EntityState.CREATED):
            needToBeDisposed = self.__lcState == EntityState.CREATED
            self.__changeStateTo(EntityState.DISPOSING)
            self.onDispose(self)
            if needToBeDisposed:
                self._dispose()
            self._destroy()
            self.__changeStateTo(EntityState.DISPOSED)
            self.onDisposed(self)
            self.__eManager.clear()
            self.__invalidatePostponedState()
        elif self.__lcState == EntityState.CREATING:
            LOG_DEBUG('Destroy call is postponed for {} object. Initialization is in progress'.format(self))
            self.__postponedState = EntityState.DISPOSING
        else:
            LOG_DEBUG('Entity {} is already destroyed! Current state {}.'.format(self, self.__lcState))

    def isDisposed(self):
        """
        Returns True if the object is destroyed (or being destroyed), otherwise returns False.
        """
        return self.__lcState in (EntityState.DISPOSING, EntityState.DISPOSED)

    def isCreated(self):
        """
        Returns True if the object is initialized (or initialization in progress),
        otherwise returns False.
        """
        return self.__lcState in (EntityState.CREATING, EntityState.CREATED)

    def _populate(self):
        """
        Performs initialization of disposable object. Derived classes can override it to perform
        required initialization.
        """
        pass

    def _invalidate(self, *args, **kwargs):
        """
        Performs re-initialization of disposable object. Derived classes can override it to
        invalidate object state.
        """
        pass

    def _dispose(self):
        """
        Cleans up resources that been allocated in the _populate method before disposable object is destroyed.
        Be aware that it is called only if _populate method has been called. Derived classes can override it to
        perform required cleanup logic.
        """
        pass

    def _destroy(self):
        """
        Perform finalization after object has been disposed. Be aware that _destroy method is always called even if
        _populate method has not been called (_dispose is called only if _populate has been called). Derived classes
        can override it to perform required cleanup logic.
        """
        pass

    def __changeStateTo(self, state):
        self.__lcState = state

    def __invalidatePostponedState(self):
        if self.__postponedState in (EntityState.DISPOSING, EntityState.DISPOSED):
            LOG_DEBUG('Call postponed destroy call for {}'.format(self))
            self.destroy()
        elif self.__postponedState in (EntityState.CREATING, EntityState.CREATED):
            LOG_DEBUG('Call postponed create call for {}'.format(self))
            self.create()
        self.__postponedState = EntityState.UNDEFINED
