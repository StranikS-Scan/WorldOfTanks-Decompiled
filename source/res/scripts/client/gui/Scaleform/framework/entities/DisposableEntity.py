# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DisposableEntity.py
import logging
from Event import EventManager, SafeEvent
_logger = logging.getLogger(__name__)

class EntityState(object):
    UNDEFINED = 0
    CREATING = 1
    CREATED = 2
    DISPOSING = 3
    DISPOSED = 4


class DisposableEntity(object):

    def __init__(self):
        super(DisposableEntity, self).__init__()
        self.__eManager = EventManager()
        self.onCreate = SafeEvent(self.__eManager)
        self.onCreated = SafeEvent(self.__eManager)
        self.onDispose = SafeEvent(self.__eManager)
        self.onDisposed = SafeEvent(self.__eManager)
        self.__lcState = EntityState.UNDEFINED
        self.__postponedState = EntityState.UNDEFINED

    def getState(self):
        return self.__lcState

    def create(self):
        if self.__lcState in (EntityState.UNDEFINED, EntityState.DISPOSED):
            self.__changeStateTo(EntityState.CREATING)
            self.onCreate(self)
            try:
                self._populate()
            except Exception as ex:
                _logger.exception(ex)

            self.__changeStateTo(EntityState.CREATED)
            self.onCreated(self)
            self.__invalidatePostponedState()
        elif self.__lcState == EntityState.DISPOSING:
            _logger.debug('Create call is postponed for %r object. Disposing is in progress.', self)
            self.__postponedState = EntityState.CREATING
        else:
            _logger.debug('Entity %r is already created! Current state %r.', self, self.__lcState)

    def validate(self, *args, **kwargs):
        if self.__lcState == EntityState.CREATED:
            self.__changeStateTo(EntityState.CREATING)
            try:
                self._invalidate(*args, **kwargs)
            except Exception as ex:
                _logger.exception(ex)

            self.__changeStateTo(EntityState.CREATED)
            self.__invalidatePostponedState()
        elif self.__lcState in (EntityState.UNDEFINED, EntityState.DISPOSING, EntityState.DISPOSED):
            _logger.debug('Invalidate call is skipped because object %r is destroyed or has not been created yet. Current state %r.', self, self.__lcState)
        else:
            _logger.debug('Invalidate call is skipped because initialization of object %r is in progress.', self)

    def _needToBeDisposed(self):
        return self.__lcState == EntityState.CREATED

    def destroy(self):
        if self.__lcState in (EntityState.UNDEFINED, EntityState.CREATED):
            needToBeDisposed = self._needToBeDisposed()
            self.__changeStateTo(EntityState.DISPOSING)
            self.onDispose(self)
            if needToBeDisposed:
                try:
                    self._dispose()
                except Exception as ex:
                    _logger.exception(ex)

            try:
                self._destroy()
            except Exception as ex:
                _logger.exception(ex)

            self.__changeStateTo(EntityState.DISPOSED)
            self.onDisposed(self)
            self.__eManager.clear()
            self.__invalidatePostponedState()
        elif self.__lcState == EntityState.CREATING:
            _logger.debug('Destroy call is postponed for %r object. Initialization is in progress', self)
            self.__postponedState = EntityState.DISPOSING
        else:
            _logger.debug('Entity %r is already destroyed! Current state %r.', self, self.__lcState)

    def isDisposed(self):
        return self.__lcState in (EntityState.DISPOSING, EntityState.DISPOSED)

    def isCreated(self):
        return self.__lcState in (EntityState.CREATING, EntityState.CREATED)

    def _populate(self):
        pass

    def _invalidate(self, *args, **kwargs):
        pass

    def _dispose(self):
        pass

    def _destroy(self):
        pass

    def __changeStateTo(self, state):
        self.__lcState = state

    def __invalidatePostponedState(self):
        if self.__postponedState in (EntityState.DISPOSING, EntityState.DISPOSED):
            _logger.debug('Call postponed destroy call for %r', self)
            self.destroy()
        elif self.__postponedState in (EntityState.CREATING, EntityState.CREATED):
            _logger.debug('Call postponed create call for %r', self)
            self.create()
        self.__postponedState = EntityState.UNDEFINED
