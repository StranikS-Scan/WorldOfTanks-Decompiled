# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/storage/descriptor.py
import typing
from future.utils import viewitems, viewvalues
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from messenger import error
from py2to3.patched_typing import Generic
from .ChannelsStorage import ChannelsStorage
from .local_cache import StorageLocalCache
from .PlayerCtxStorage import PlayerCtxStorage
from .shown_messages_storage import ShownMessagesStorage
from .UsersStorage import UsersStorage
_STORAGE = {ChannelsStorage: ChannelsStorage(),
 PlayerCtxStorage: PlayerCtxStorage(),
 ShownMessagesStorage: ShownMessagesStorage(),
 UsersStorage: UsersStorage()}
_StorageType = typing.TypeVar('_StorageType', bound=typing.Union[ChannelsStorage, UsersStorage, PlayerCtxStorage, ShownMessagesStorage])

class MessengerStorageDescriptor(Generic[_StorageType]):

    def __init__(self, class_):
        super(MessengerStorageDescriptor, self).__init__()
        if class_ not in _STORAGE:
            msg = 'Storage "{:>s}" not found'.format(class_)
            raise error(msg)
        self.__class = class_

    def __get__(self, obj, objType):
        return _STORAGE[self.__class]

    def get(self):
        return _STORAGE[self.__class]


class StorageDecorator(object):

    def __repr__(self):
        return 'StorageDecorator(id=0x{:08X}, ro={!r:s})'.format(id(self), _STORAGE.keys())

    def __init__(self):
        self.__storageCache = None
        return

    def restoreFromCache(self):
        if self.__storageCache:
            return
        self.__storageCache = StorageLocalCache((getPlayerDatabaseID(), getPlayerName(), 'storage'))
        self.__storageCache.onRead += self.__onRead
        self.__storageCache.read()

    def init(self):
        for storage in viewvalues(_STORAGE):
            storage.init()

    def switch(self, scope):
        for storage in viewvalues(_STORAGE):
            storage.switch(scope)

    def clear(self):
        if self.__storageCache:
            for name, storage in viewitems(_STORAGE):
                record = storage.makeRecordInCache()
                if record:
                    self.__storageCache.addRecord(name, record)

            self.__storageCache.write()
            self.__storageCache.clear()
            self.__storageCache.onRead -= self.__onRead
            self.__storageCache = None
        for storage in viewvalues(_STORAGE):
            storage.clear()

        return

    def __onRead(self):
        if not self.__storageCache:
            return
        self.__storageCache.onRead -= self.__onRead
        for name, storage in viewitems(_STORAGE):
            storage.restoreFromCache(self.__storageCache.popRecord(name))
