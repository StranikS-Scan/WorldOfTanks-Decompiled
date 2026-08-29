# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/storage/__init__.py
from .ChannelsStorage import ChannelsStorage
from .descriptor import MessengerStorageDescriptor, StorageDecorator
from .local_cache import StorageLocalCache
from .PlayerCtxStorage import PlayerCtxStorage
from .shown_messages_storage import ShownMessagesStorage
from .UsersStorage import UsersStorage
__all__ = ('ChannelsStorage', 'MessengerStorageDescriptor', 'PlayerCtxStorage', 'ShownMessagesStorage', 'StorageDecorator', 'StorageLocalCache', 'UsersStorage')
