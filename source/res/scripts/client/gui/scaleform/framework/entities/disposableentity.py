# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DisposableEntity.py
from Event import Event
from debug_utils import LOG_DEBUG

class ENTITY_STATE(object):
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
    ENTITY_STATE description.
    Note that disposable object cannot be destroyed during its initialization. If object is
    destroyed when _populate method is performed, destroy call is postponed till  _populate method
    completion.
    """

    def __init__(self):
        super(DisposableEntity, self).__init__()
        self.onModuleDispose = Event()
        self.__lcState = ENTITY_STATE.UNDEFINED
        self.__postponedState = ENTITY_STATE.UNDEFINED

    def create(self):
        """
        Initializes object.
        """
        if self.__lcState in (ENTITY_STATE.UNDEFINED, ENTITY_STATE.DISPOSED):
            self.__changeStateTo(ENTITY_STATE.CREATING)
            self._populate()
            self.__changeStateTo(ENTITY_STATE.CREATED)
            self.__invalidatePostponedState()
        elif self.__lcState == ENTITY_STATE.DISPOSING:
            LOG_DEBUG('Create call is postponed for {} object. Disposing is in progress.'.format(self))
            self.__postponedState = ENTITY_STATE.CREATING
        else:
            LOG_DEBUG('Entity {} is already created! Current state {}.'.format(self, self.__lcState))

    def validate(self):
        """
        Re-initializes object.
        """
        if self.__lcState == ENTITY_STATE.CREATED:
            self.__changeStateTo(ENTITY_STATE.CREATING)
            self._invalidate()
            self.__changeStateTo(ENTITY_STATE.CREATED)
            self.__invalidatePostponedState()
        elif self.__lcState in (ENTITY_STATE.UNDEFINED, ENTITY_STATE.DISPOSING, ENTITY_STATE.DISPOSED):
            LOG_DEBUG('Invalidate call is skipped because object {} is destroyed or has not been created yet. Current state {}.'.format(self, self.__lcState))
        else:
            LOG_DEBUG('Invalidate call is skipped because initialization of object {} is in progress.'.format(self))

    def destroy(self):
        """
        Destroy object.
        """
        if self.__lcState == ENTITY_STATE.CREATED:
            self.__changeStateTo(ENTITY_STATE.DISPOSING)
            self.onModuleDispose(self)
            self.onModuleDispose.clear()
            self._dispose()
            self.__changeStateTo(ENTITY_STATE.DISPOSED)
            self.__invalidatePostponedState()
        elif self.__lcState == ENTITY_STATE.CREATING:
            LOG_DEBUG('Destroy call is postponed for {} object. Initialization is in progress'.format(self))
            self.__postponedState = ENTITY_STATE.DISPOSING
        else:
            LOG_DEBUG('Entity {} is already destroyed or has not been created! Current state {}.'.format(self, self.__lcState))

    def isDisposed(self):
        """
        Returns True if the object is destroyed (or being destroyed), otherwise returns False.
        """
        return self.__lcState in (ENTITY_STATE.DISPOSING, ENTITY_STATE.DISPOSED)

    def isCreated(self):
        """
        Returns True if the object is initialized (or initialization in progress),
        otherwise returns False.
        """
        return self.__lcState in (ENTITY_STATE.CREATING, ENTITY_STATE.CREATED)

    def _populate(self):
        """
        Performs initialization of disposable object. Derived classes can override it to perform
        required initialization.
        """
        pass

    def _invalidate(self):
        """
        Performs re-initialization of disposable object. Derived classes can override it to
        invalidate object state.
        """
        pass

    def _dispose(self):
        """
        Cleans up resources and inner state before disposable object will be destroyed.
        Derived classes can override it to perform required cleanup logic.
        """
        pass

    def __changeStateTo(self, state):
        self.__lcState = state

    def __invalidatePostponedState(self):
        if self.__postponedState in (ENTITY_STATE.DISPOSING, ENTITY_STATE.DISPOSED):
            LOG_DEBUG('Call postponed destroy call for {}'.format(self))
            self.destroy()
        elif self.__postponedState in (ENTITY_STATE.CREATING, ENTITY_STATE.CREATED):
            LOG_DEBUG('Call postponed create call for {}'.format(self))
            self.destroy()
        self.__postponedState = ENTITY_STATE.UNDEFINED
