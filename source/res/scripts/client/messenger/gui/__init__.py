# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/__init__.py
# Compiled at: 2010-12-03 15:38:00
from ConnectionManager import connectionManager
from debug_utils import LOG_ERROR
import exceptions
from messenger.gui import MessengerDispatcher
from PlayerEvents import g_playerEvents

def init():
    try:
        from messenger.gui.Scalefrom.MessengerLobbyInterface import MessengerLobbyInterface
        from messenger.gui.Scalefrom.MessengerBattleInterface import MessengerBattleInterface
        MessengerDispatcher.g_instance = MessengerDispatcher.MessengerDispatcher(MessengerLobbyInterface, MessengerBattleInterface)
    except exceptions.ImportError:
        LOG_ERROR('Package messenger.gui.Scaleform not defined')
        raise


def start():
    messenger = MessengerDispatcher.g_instance
    if messenger is not None:
        g_playerEvents.onAccountBecomePlayer += messenger.onLobbyConnect
        connectionManager.onDisconnected += messenger.onDisconnect
    return


def fini():
    messenger = MessengerDispatcher.g_instance
    if messenger is not None:
        g_playerEvents.onAccountBecomePlayer -= messenger.onLobbyConnect
        connectionManager.onDisconnected -= messenger.onDisconnect
        messenger.onDisconnect()
    return
