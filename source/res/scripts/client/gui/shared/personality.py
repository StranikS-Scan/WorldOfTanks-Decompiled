# Embedded file name: scripts/client/gui/shared/personality.py
import time
import SoundGroups
import BigWorld
import MusicController
from gui.shared.ClanCache import g_clanCache
from predefined_hosts import g_preDefinedHosts
from account_helpers.settings_core.SettingsCache import g_settingsCache
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.AccountValidator import AccountValidator
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from helpers import isPlayerAccount
from adisp import process
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from PlayerEvents import g_playerEvents
from account_helpers import isPremiumAccount
from CurrentVehicle import g_currentVehicle
from ConnectionManager import connectionManager
from gui import SystemMessages, g_guiResetters, game_control
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_eventBus, g_itemsCache, g_eventsCache, events
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.WindowsManager import g_windowsManager
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils import ParametersCache
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.RareAchievementsCache import g_rareAchievesCache

@process
def onAccountShowGUI(ctx):
    global onCenterIsLongDisconnected
    g_lobbyContext.onAccountShowGUI(ctx)
    yield g_itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
    yield g_eventsCache.update()
    yield g_settingsCache.update()
    if not g_itemsCache.isSynced():
        return
    else:
        code = yield AccountValidator().validate()
        if code > 0:
            from gui import DialogsInterface
            DialogsInterface.showDisconnect('#menu:disconnect/codes/%d' % code)
            return
        g_settingsCore.serverSettings.applySettings()
        game_control.g_instance.onAccountShowGUI(g_lobbyContext.getGuiCtx())
        accDossier = g_itemsCache.items.getAccountDossier()
        g_rareAchievesCache.request(accDossier.getBlock('rareAchievements'))
        eula = EULADispatcher()
        yield eula.processLicense()
        eula.fini()
        eula = None
        MusicController.g_musicController.setAccountAttrs(g_itemsCache.items.stats.attributes)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        premium = isPremiumAccount(g_itemsCache.items.stats.attributes)
        if g_hangarSpace.inited:
            g_hangarSpace.refreshSpace(premium)
        else:
            g_hangarSpace.init(premium)
        g_currentVehicle.init()
        g_windowsManager.onAccountShowGUI(g_lobbyContext.getGuiCtx())
        g_prbLoader.onAccountShowGUI(g_lobbyContext.getGuiCtx())
        g_clanCache.onAccountShowGUI()
        SoundGroups.g_instance.enableLobbySounds(True)
        onCenterIsLongDisconnected(True)
        Waiting.hide('enter')
        return


def onAccountBecomeNonPlayer():
    g_itemsCache.clear()
    g_currentVehicle.destroy()
    g_hangarSpace.destroy()


@process
def onAvatarBecomePlayer():
    yield g_settingsCache.update()
    g_settingsCore.serverSettings.applySettings()
    g_prbLoader.onAvatarBecomePlayer()
    game_control.g_instance.onAvatarBecomePlayer()
    g_clanCache.onAvatarBecomePlayer()
    Waiting.cancelCallback()


def onAccountBecomePlayer():
    game_control.g_instance.onAccountBecomePlayer()


@process
def onClientUpdate(diff):
    yield lambda callback: callback(None)
    if isPlayerAccount():
        yield g_itemsCache.update(CACHE_SYNC_REASON.CLIENT_UPDATE, diff)
        yield g_eventsCache.update(diff)
        yield g_clanCache.update(diff)
    g_clientUpdateManager.update(diff)


def onShopResyncStarted():
    Waiting.show('sinhronize')


@process
def onShopResync():
    yield g_itemsCache.update(CACHE_SYNC_REASON.SHOP_RESYNC)
    if not g_itemsCache.isSynced():
        Waiting.hide('sinhronize')
        return
    yield g_eventsCache.update()
    Waiting.hide('sinhronize')
    now = time.time()
    SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.SHOP_RESYNC, date=BigWorld.wg_getLongDateFormat(now), time=BigWorld.wg_getShortTimeFormat(now), type=SystemMessages.SM_TYPE.Information)


def onCenterIsLongDisconnected(isLongDisconnected):
    isAvailable = not BigWorld.player().isLongDisconnectedFromCenter
    if isAvailable and not isLongDisconnected:
        SystemMessages.g_instance.pushI18nMessage(MENU.CENTERISAVAILABLE, type=SystemMessages.SM_TYPE.Information)
    elif not isAvailable:
        SystemMessages.g_instance.pushI18nMessage(MENU.CENTERISUNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)


def onIGRTypeChanged(roomType, xpFactor):
    g_lobbyContext.updateGuiCtx({'igrData': {'roomType': roomType,
                 'igrXPFactor': xpFactor}})


@process
def onAppStarted(args):
    yield lambda callback: callback(None)
    if not connectionManager.isConnected():
        return


def init(loadingScreenGUI = None):
    global onIGRTypeChanged
    global onShopResyncStarted
    global onAvatarBecomePlayer
    global onAccountBecomePlayer
    global onAccountBecomeNonPlayer
    global onAccountShowGUI
    global onShopResync
    g_playerEvents.onAccountShowGUI += onAccountShowGUI
    g_playerEvents.onAccountBecomeNonPlayer += onAccountBecomeNonPlayer
    g_playerEvents.onAccountBecomePlayer += onAccountBecomePlayer
    g_playerEvents.onAvatarBecomePlayer += onAvatarBecomePlayer
    g_playerEvents.onClientUpdated += onClientUpdate
    g_playerEvents.onShopResyncStarted += onShopResyncStarted
    g_playerEvents.onShopResync += onShopResync
    g_playerEvents.onCenterIsLongDisconnected += onCenterIsLongDisconnected
    g_playerEvents.onIGRTypeChanged += onIGRTypeChanged
    game_control.g_instance.init()
    from gui.Scaleform import SystemMessagesInterface
    SystemMessages.g_instance = SystemMessagesInterface.SystemMessagesInterface()
    SystemMessages.g_instance.init()
    ParametersCache.g_instance.init()
    if loadingScreenGUI and loadingScreenGUI.script:
        loadingScreenGUI.script.active(False)
    g_prbLoader.init()
    LogitechMonitor.init()
    g_itemsCache.init()
    g_settingsCache.init()
    g_settingsCore.init()
    g_eventsCache.init()
    g_clanCache.init()
    from constants import IS_DEVELOPMENT
    if IS_DEVELOPMENT:
        try:
            from gui.development import init
        except ImportError:
            LOG_ERROR('Development features not found.')
            init = lambda : None

        init()


def start():
    g_eventBus.addListener(events.GUICommonEvent.APP_STARTED, onAppStarted)
    g_windowsManager.start()


def fini():
    Waiting.close()
    g_eventBus.removeListener(events.GUICommonEvent.APP_STARTED, onAppStarted)
    game_control.g_instance.fini()
    g_settingsCore.fini()
    g_settingsCache.fini()
    g_eventsCache.fini()
    g_itemsCache.fini()
    LogitechMonitor.destroy()
    g_windowsManager.destroy()
    SystemMessages.g_instance.destroy()
    g_eventBus.clear()
    g_prbLoader.fini()
    g_clanCache.fini()
    g_playerEvents.onIGRTypeChanged -= onIGRTypeChanged
    g_playerEvents.onAccountShowGUI -= onAccountShowGUI
    g_playerEvents.onAccountBecomeNonPlayer -= onAccountBecomeNonPlayer
    g_playerEvents.onAvatarBecomePlayer -= onAvatarBecomePlayer
    g_playerEvents.onAccountBecomePlayer -= onAccountBecomePlayer
    g_playerEvents.onClientUpdated -= onClientUpdate
    g_playerEvents.onShopResyncStarted -= onShopResyncStarted
    g_playerEvents.onShopResync -= onShopResync
    g_playerEvents.onCenterIsLongDisconnected -= onCenterIsLongDisconnected
    from constants import IS_DEVELOPMENT
    if IS_DEVELOPMENT:
        try:
            from gui.development import fini
        except ImportError:
            LOG_ERROR('Development features not found.')
            fini = lambda : None

        fini()


def onConnected():
    pass


def onDisconnected():
    if game_control.g_instance.roaming.isInRoaming():
        g_preDefinedHosts.savePeripheryTL(connectionManager.peripheryID)
    g_prbLoader.onDisconnected()
    g_clanCache.onDisconnected()
    game_control.g_instance.onDisconnected()
    g_itemsCache.clear()
    g_lobbyContext.clear()
    Waiting.rollback()
    Waiting.cancelCallback()


def onRecreateDevice():
    for c in g_guiResetters:
        try:
            c()
        except Exception:
            LOG_CURRENT_EXCEPTION()
