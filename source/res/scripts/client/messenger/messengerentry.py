# Embedded file name: scripts/client/messenger/MessengerEntry.py
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from messenger import g_settings
from messenger.ext.filters import MessageFiltersChain
from messenger.ext.player_helpers import CurrentPlayerHelper
from messenger.gui.entry_decorator import GUIDecorator
from messenger.m_constants import MESSENGER_SCOPE
from messenger.proto import ProtoPluginsDecorator
from messenger.storage import StorageDecorator

class MessengerEntry(object):

    def __init__(self):
        self.__protoPlugins = ProtoPluginsDecorator()
        self.__storage = StorageDecorator()
        self.__gui = GUIDecorator()
        self.__playerHelper = CurrentPlayerHelper()
        self.__msgFiltersChain = MessageFiltersChain()

    @property
    def protos(self):
        return self.__protoPlugins

    @property
    def storage(self):
        return self.__storage

    @property
    def gui(self):
        return self.__gui

    def init(self):
        g_settings.init()
        self.__gui.init()
        self.__msgFiltersChain.init()
        self.__protoPlugins.setFilters(self.__msgFiltersChain)
        g_playerEvents.onAccountShowGUI += self.__pe_onAccountShowGUI
        g_playerEvents.onGuiCacheSyncCompleted += self.__pe_onGuiCacheSyncCompleted
        g_playerEvents.onAccountBecomePlayer += self.__pe_onAccountBecomePlayer
        g_playerEvents.onAvatarBecomePlayer += self.__pe_onAvatarBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer += self.__pe_onAccountBecomeNonPlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__pe_onAvatarBecomeNonPlayer
        connectionManager.onDisconnected += self.__cm_onDisconnected

    def fini(self):
        self.__msgFiltersChain.fini()
        self.__protoPlugins.clear()
        self.__gui.clear()
        self.__playerHelper.clear()
        self.__storage.clear()
        g_settings.fini()
        g_playerEvents.onAccountShowGUI -= self.__pe_onAccountShowGUI
        g_playerEvents.onGuiCacheSyncCompleted -= self.__pe_onGuiCacheSyncCompleted
        g_playerEvents.onAccountBecomePlayer -= self.__pe_onAccountBecomePlayer
        g_playerEvents.onAvatarBecomePlayer -= self.__pe_onAvatarBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer -= self.__pe_onAccountBecomeNonPlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__pe_onAvatarBecomeNonPlayer
        connectionManager.onDisconnected -= self.__cm_onDisconnected

    def onAccountShowGUI(self):
        self.__playerHelper.initPersonalAccount()
        self.__storage.restoreFromCache()
        self.__protoPlugins.view(MESSENGER_SCOPE.LOBBY)

    def onAvatarInitGUI(self):
        import BattleReplay
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__gui.switch(MESSENGER_SCOPE.BATTLE)
            return
        self.__playerHelper.onAvatarShowGUI()
        self.__storage.restoreFromCache()
        scope = MESSENGER_SCOPE.BATTLE
        self.__protoPlugins.connect(scope)
        self.__gui.switch(scope)

    def onAvatarShowGUI(self):
        import BattleReplay
        if not BattleReplay.g_replayCtrl.isPlaying:
            self.__protoPlugins.view(MESSENGER_SCOPE.BATTLE)

    def __pe_onAccountShowGUI(self, _):
        self.onAccountShowGUI()

    def __pe_onGuiCacheSyncCompleted(self, _):
        self.__playerHelper.initCachedData()

    def __pe_onAccountBecomePlayer(self):
        scope = MESSENGER_SCOPE.LOBBY
        g_settings.update()
        self.__storage.init()
        self.__protoPlugins.setFilters(self.__msgFiltersChain)
        self.__protoPlugins.connect(scope)
        self.__gui.switch(scope)

    def __pe_onAvatarBecomePlayer(self):
        g_settings.update()
        self.__storage.init()
        self.__protoPlugins.setFilters(self.__msgFiltersChain)
        self.__playerHelper.onAvatarBecomePlayer()

    def __pe_onAccountBecomeNonPlayer(self):
        self.__gui.close(MESSENGER_SCOPE.UNKNOWN)

    def __pe_onAvatarBecomeNonPlayer(self):
        self.__gui.close(MESSENGER_SCOPE.UNKNOWN)

    def __cm_onDisconnected(self):
        self.__protoPlugins.disconnect()
        self.__gui.switch(MESSENGER_SCOPE.LOGIN)
        self.__playerHelper.onDisconnected()
        self.__storage.clear()
        g_settings.resetUserPreferences()


g_instance = MessengerEntry()
