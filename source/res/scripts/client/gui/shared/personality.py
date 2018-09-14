# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/personality.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from account_helpers import isPremiumAccount
from account_helpers.AccountValidator import AccountValidator
from adisp import process
from constants import HAS_DEV_RESOURCES
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, g_guiResetters, miniclient
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.app_loader import g_appLoader
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.RareAchievementsCache import g_rareAchievesCache
from gui.shared.utils import requesters
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.wgnc import g_wgncProvider
from helpers import isPlayerAccount, time_utils, dependency
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.account_helpers.settings_core import ISettingsCache, ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.clans import IClanController
from skeletons.gui.game_control import IGameStateTracker
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.sounds import ISoundsController
from skeletons.helpers.statistics import IStatisticsCollector
try:
    from gui import mods
    guiModsInit = mods.init
    guiModsFini = mods.fini
    guiModsSendEvent = mods.sendEvent
except ImportError:
    LOG_DEBUG('There is not mods package in the scripts')
    guiModsInit = guiModsFini = guiModsSendEvent = lambda *args: None

class ServicesLocator(object):
    itemsCache = dependency.descriptor(IItemsCache)
    gameState = dependency.descriptor(IGameStateTracker)
    loginManager = dependency.descriptor(ILoginManager)
    eventsCache = dependency.descriptor(IEventsCache)
    soundCtrl = dependency.descriptor(ISoundsController)
    clanCtrl = dependency.descriptor(IClanController)
    settingsCache = dependency.descriptor(ISettingsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    battleResults = dependency.descriptor(IBattleResultsService)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    @classmethod
    def clear(cls):
        cls.itemsCache.clear()
        cls.goodiesCache.clear()
        cls.eventsCache.clear()
        cls.lobbyContext.clear()


@process
def onAccountShowGUI(ctx):
    global onCenterIsLongDisconnected
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.SHOW_GUI)
    ServicesLocator.lobbyContext.onAccountShowGUI(ctx)
    yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.QUESTS_SYNC)
    ServicesLocator.eventsCache.start()
    yield ServicesLocator.eventsCache.update()
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.USER_SERVER_SETTINGS_SYNC)
    yield ServicesLocator.settingsCache.update()
    if not ServicesLocator.itemsCache.isSynced():
        g_appLoader.goToLoginByError('#menu:disconnect/codes/0')
        return
    eula = EULADispatcher()
    yield eula.processLicense()
    eula.fini()
    g_playerEvents.onGuiCacheSyncCompleted(ctx)
    code = yield AccountValidator().validate()
    if code > 0:
        g_appLoader.goToLoginByError('#menu:disconnect/codes/%d' % code)
        return
    ServicesLocator.settingsCore.serverSettings.applySettings()
    ServicesLocator.gameState.onAccountShowGUI(ServicesLocator.lobbyContext.getGuiCtx())
    accDossier = ServicesLocator.itemsCache.items.getAccountDossier()
    g_rareAchievesCache.request(accDossier.getBlock('rareAchievements'))
    premium = isPremiumAccount(ServicesLocator.itemsCache.items.stats.attributes)
    if g_hangarSpace.inited:
        g_hangarSpace.refreshSpace(premium)
    else:
        g_hangarSpace.init(premium)
    g_currentVehicle.init()
    g_currentPreviewVehicle.init()
    if not g_prbLoader.isEnabled():
        isLobbyLoaded = g_appLoader
    g_appLoader.showLobby()
    g_prbLoader.onAccountShowGUI(ServicesLocator.lobbyContext.getGuiCtx())
    g_clanCache.onAccountShowGUI()
    ServicesLocator.clanCtrl.start()
    ServicesLocator.soundCtrl.start()
    SoundGroups.g_instance.enableLobbySounds(True)
    onCenterIsLongDisconnected(True)
    guiModsSendEvent('onAccountShowGUI', ctx)
    Waiting.hide('enter')


def onAccountBecomeNonPlayer():
    ServicesLocator.itemsCache.clear()
    ServicesLocator.goodiesCache.clear()
    g_currentVehicle.destroy()
    g_currentPreviewVehicle.destroy()
    g_hangarSpace.destroy()
    g_prbLoader.onAccountBecomeNonPlayer()
    guiModsSendEvent('onAccountBecomeNonPlayer')
    UsersInfoHelper.clear()


@process
def onAvatarBecomePlayer():
    ServicesLocator.battleResults.clear()
    yield ServicesLocator.settingsCache.update()
    ServicesLocator.settingsCore.serverSettings.applySettings()
    ServicesLocator.soundCtrl.stop()
    ServicesLocator.clanCtrl.stop()
    ServicesLocator.eventsCache.stop()
    g_prbLoader.onAvatarBecomePlayer()
    ServicesLocator.gameState.onAvatarBecomePlayer()
    g_clanCache.onAvatarBecomePlayer()
    ServicesLocator.loginManager.writePeripheryLifetime()
    guiModsSendEvent('onAvatarBecomePlayer')
    Waiting.cancelCallback()


def onAccountBecomePlayer():
    ServicesLocator.lobbyContext.onAccountBecomePlayer()
    ServicesLocator.gameState.onAccountBecomePlayer()
    guiModsSendEvent('onAccountBecomePlayer')


@process
def onClientUpdate(diff, updateOnlyLobbyCtx):
    yield lambda callback: callback(None)
    if updateOnlyLobbyCtx:
        ServicesLocator.lobbyContext.update(diff)
    else:
        if isPlayerAccount():
            yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.CLIENT_UPDATE, diff)
            yield ServicesLocator.eventsCache.update(diff)
            yield g_clanCache.update(diff)
        ServicesLocator.lobbyContext.update(diff)
        g_clientUpdateManager.update(diff)


def onShopResyncStarted():
    Waiting.show('sinhronize')


@process
def onShopResync():
    yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.SHOP_RESYNC)
    if not ServicesLocator.itemsCache.isSynced():
        Waiting.hide('sinhronize')
        return
    yield ServicesLocator.eventsCache.update()
    Waiting.hide('sinhronize')
    now = time_utils.getCurrentTimestamp()
    SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.SHOP_RESYNC, date=BigWorld.wg_getLongDateFormat(now), time=BigWorld.wg_getShortTimeFormat(now), type=SystemMessages.SM_TYPE.Information)


def onCenterIsLongDisconnected(isLongDisconnected):
    isAvailable = not BigWorld.player().isLongDisconnectedFromCenter
    if isAvailable and not isLongDisconnected:
        SystemMessages.pushI18nMessage(MENU.CENTERISAVAILABLE, type=SystemMessages.SM_TYPE.Information)
    elif not isAvailable:
        SystemMessages.pushI18nMessage(MENU.CENTERISUNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)


def onIGRTypeChanged(roomType, xpFactor):
    ServicesLocator.lobbyContext.updateGuiCtx({'igrData': {'roomType': roomType,
                 'igrXPFactor': xpFactor}})


def init(loadingScreenGUI=None):
    global onShopResyncStarted
    global onAccountShowGUI
    global onScreenShotMade
    global onIGRTypeChanged
    global onAccountBecomeNonPlayer
    global onAvatarBecomePlayer
    global onAccountBecomePlayer
    global onKickedFromServer
    global onShopResync
    miniclient.configure_state()
    ServicesLocator.connectionMgr.onKickedFromServer += onKickedFromServer
    g_playerEvents.onAccountShowGUI += onAccountShowGUI
    g_playerEvents.onAccountBecomeNonPlayer += onAccountBecomeNonPlayer
    g_playerEvents.onAccountBecomePlayer += onAccountBecomePlayer
    g_playerEvents.onAvatarBecomePlayer += onAvatarBecomePlayer
    g_playerEvents.onClientUpdated += onClientUpdate
    g_playerEvents.onShopResyncStarted += onShopResyncStarted
    g_playerEvents.onShopResync += onShopResync
    g_playerEvents.onCenterIsLongDisconnected += onCenterIsLongDisconnected
    g_playerEvents.onIGRTypeChanged += onIGRTypeChanged
    from gui.Scaleform.app_factory import createAppFactory
    g_appLoader.init(createAppFactory())
    g_paramsCache.init()
    if loadingScreenGUI and loadingScreenGUI.script:
        loadingScreenGUI.script.active(False)
    g_prbLoader.init()
    g_clanCache.init()
    BigWorld.wg_setScreenshotNotifyCallback(onScreenShotMade)
    if HAS_DEV_RESOURCES:
        try:
            from gui.development import init
        except ImportError:
            LOG_ERROR('Development features not found.')

            def init():
                pass

        init()
    guiModsInit()


def start():
    g_appLoader.startLobby()


def fini():
    guiModsFini()
    Waiting.close()
    g_appLoader.fini()
    g_eventBus.clear()
    g_prbLoader.fini()
    g_clanCache.fini()
    requesters.fini()
    UsersInfoHelper.fini()
    ServicesLocator.connectionMgr.onKickedFromServer -= onKickedFromServer
    g_playerEvents.onIGRTypeChanged -= onIGRTypeChanged
    g_playerEvents.onAccountShowGUI -= onAccountShowGUI
    g_playerEvents.onAccountBecomeNonPlayer -= onAccountBecomeNonPlayer
    g_playerEvents.onAvatarBecomePlayer -= onAvatarBecomePlayer
    g_playerEvents.onAccountBecomePlayer -= onAccountBecomePlayer
    g_playerEvents.onClientUpdated -= onClientUpdate
    g_playerEvents.onShopResyncStarted -= onShopResyncStarted
    g_playerEvents.onShopResync -= onShopResync
    g_playerEvents.onCenterIsLongDisconnected -= onCenterIsLongDisconnected
    BigWorld.wg_setScreenshotNotifyCallback(None)
    if HAS_DEV_RESOURCES:
        try:
            from gui.development import fini
        except ImportError:
            LOG_ERROR('Development features not found.')

            def fini():
                pass

        fini()
    return


def onConnected():
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.CONNECTED)
    guiModsSendEvent('onConnected')
    ServicesLocator.gameState.onConnected()


def onDisconnected():
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.DISCONNECTED)
    guiModsSendEvent('onDisconnected')
    g_appLoader.goToLoginByEvent()
    ServicesLocator.battleResults.clear()
    g_prbLoader.onDisconnected()
    g_clanCache.onDisconnected()
    ServicesLocator.soundCtrl.stop(isDisconnected=True)
    ServicesLocator.gameState.onDisconnected()
    ServicesLocator.clanCtrl.stop()
    g_wgncProvider.clear()
    ServicesLocator.clear()
    UsersInfoHelper.clear()
    Waiting.rollback()
    Waiting.cancelCallback()


def onKickedFromServer(reason, isBan, expiryTime):
    g_appLoader.goToLoginByKick(reason, isBan, expiryTime)


def onScreenShotMade(path):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.SCREEN_SHOT_MADE, {'path': path}), scope=EVENT_BUS_SCOPE.GLOBAL)


def onRecreateDevice():
    for c in g_guiResetters:
        try:
            c()
        except Exception:
            LOG_CURRENT_EXCEPTION()
