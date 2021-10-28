# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/personality.py
import logging
import time
import weakref
from functools import partial
import BigWorld
import SoundGroups
import nations
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from account_helpers.account_validator import ValidationCodes, InventoryVehiclesValidator, InventoryOutfitValidator, InventoryTankmenValidator
from adisp import process, async
from constants import HAS_DEV_RESOURCES
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, g_guiResetters, miniclient
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import requesters
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.wgnc import g_wgncProvider
from helpers import isPlayerAccount, time_utils, dependency
from helpers.blueprint_generator import g_blueprintGenerator
from helpers.statistics import HANGAR_LOADING_STATE
from items import vehicles
from skeletons.account_helpers.settings_core import ISettingsCache, ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gameplay import IGameplayLogic, PlayerEventID
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IGameStateTracker, IBootcampController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace, IRaresCache
from skeletons.gui.sounds import ISoundsController
from skeletons.gui.web import IWebController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.helpers.statistics import IStatisticsCollector
_logger = logging.getLogger(__name__)
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
    webCtrl = dependency.descriptor(IWebController)
    settingsCache = dependency.descriptor(ISettingsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    battleResults = dependency.descriptor(IBattleResultsService)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    eventsController = dependency.descriptor(IEventBoardController)
    gameplay = dependency.descriptor(IGameplayLogic)
    hangarSpace = dependency.descriptor(IHangarSpace)
    rareAchievesCache = dependency.descriptor(IRaresCache)
    appLoader = dependency.descriptor(IAppLoader)
    offersProvider = dependency.descriptor(IOffersDataProvider)
    bootcamp = dependency.descriptor(IBootcampController)
    gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def clear(cls):
        cls.itemsCache.clear()
        cls.goodiesCache.clear()
        cls.gameEventController.clear()
        cls.eventsCache.clear()
        cls.lobbyContext.clear()
        cls.settingsCore.clear()
        cls.settingsCache.clear()

    @classmethod
    def onDisconnected(cls):
        cls.itemsCache.onDisconnected()
        cls.clear()


class NationVehiclesCacher(object):

    def __init__(self, nation):
        self.__nation = nation
        self.__name__ = '%sVehiclesCacher' % nations.NAMES[nation]

    @async
    def __call__(self, ctx, callback=None):
        itemGetter = ServicesLocator.itemsCache.items.getItem
        counter = 0
        for vehTypeID in vehicles.g_list.getList(self.__nation):
            if itemGetter(GUI_ITEM_TYPE.VEHICLE, self.__nation, vehTypeID) is None:
                _logger.error('Vehicle with nation:%s and innationID:%s doesnt exist', self.__nation, vehTypeID)
                callback(False)
                return
            counter += 1

        _logger.info('Vehicles in nation: %s created %s', nations.NAMES[self.__nation], counter)
        callback(True)
        return


def onAccountShowGUI(ctx):
    Waiting.show('enter')
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.SHOW_GUI)
    ServicesLocator.lobbyContext.onAccountShowGUI(ctx)
    chain = [__runItemsCacheSync,
     __validateInventoryVehicles,
     __validateInventoryOutfit,
     __validateInventoryTankmen]
    chain.extend([ NationVehiclesCacher(nationID) for nationID in xrange(len(nations.NAMES)) ])
    chain.extend([__runQuestSync,
     __runSettingsSync,
     __processEULA,
     __notifyOnSyncComplete,
     __requestDossier,
     __initializeHangarSpace,
     __initializeHangar,
     __processWebCtrl,
     __processElen])
    __runChain(chain, ctx)


def onAccountBecomeNonPlayer():
    g_clanCache.clear()
    g_currentVehicle.destroy()
    ServicesLocator.itemsCache.clear()
    ServicesLocator.goodiesCache.clear()
    g_currentPreviewVehicle.destroy()
    ServicesLocator.hangarSpace.destroy()
    g_prbLoader.onAccountBecomeNonPlayer()
    ServicesLocator.gameState.onAccountBecomeNonPlayer()
    ServicesLocator.gameEventController.stop()
    guiModsSendEvent('onAccountBecomeNonPlayer')
    UsersInfoHelper.clear()
    g_blueprintGenerator.fini()


@process
def onAvatarBecomePlayer():
    ServicesLocator.battleResults.clear()
    yield ServicesLocator.settingsCache.update()
    ServicesLocator.settingsCore.serverSettings.applySettings()
    ServicesLocator.soundCtrl.stop()
    ServicesLocator.webCtrl.stop(logout=False)
    ServicesLocator.gameEventController.stop()
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
            yield crewBooksViewedCache().onCrewBooksUpdated(diff)
            yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.CLIENT_UPDATE, diff)
            yield ServicesLocator.eventsCache.update(diff)
            yield g_clanCache.update(diff)
        ServicesLocator.lobbyContext.update(diff)
        _logger.info('onClientUpdate: diff = %r', diff)
        g_clientUpdateManager.update(diff)
    ServicesLocator.offersProvider.update(diff)


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
    SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.SHOP_RESYNC, date=backport.getLongDateFormat(now), time=backport.getShortTimeFormat(now), type=SystemMessages.SM_TYPE.Information)


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
    global onCenterIsLongDisconnected
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
    ServicesLocator.appLoader.init(createAppFactory())
    g_paramsCache.init()
    if loadingScreenGUI and loadingScreenGUI.script:
        loadingScreenGUI.script.active(False)
    g_prbLoader.init()
    g_clanCache.init()
    BigWorld.wg_setScreenshotNotifyCallback(onScreenShotMade)
    if HAS_DEV_RESOURCES:
        try:
            from gui.development import init as dev_init
        except ImportError:
            LOG_ERROR('Development features not found.')

            def dev_init():
                pass

        dev_init()
    guiModsInit()


def fini():
    guiModsFini()
    Waiting.close()
    ServicesLocator.appLoader.fini()
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
            from gui.development import fini as dev_fini
        except ImportError:
            LOG_ERROR('Development features not found.')

            def dev_fini():
                pass

        dev_fini()
    return


def onConnected():
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.CONNECTED)
    guiModsSendEvent('onConnected')
    ServicesLocator.gameState.onConnected()


def onDisconnected():
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.DISCONNECTED)
    guiModsSendEvent('onDisconnected')
    ServicesLocator.gameplay.goToLoginByEvent()
    ServicesLocator.battleResults.clear()
    g_prbLoader.onDisconnected()
    g_clanCache.onDisconnected()
    ServicesLocator.soundCtrl.stop(isDisconnected=True)
    ServicesLocator.gameState.onDisconnected()
    ServicesLocator.webCtrl.stop()
    ServicesLocator.eventsCache.getPersonalMissions().stop()
    g_wgncProvider.clear()
    ServicesLocator.onDisconnected()
    UsersInfoHelper.clear()
    Waiting.rollback()
    Waiting.cancelCallback()
    if ServicesLocator.lobbyContext.getServerSettings().isElenEnabled():
        ServicesLocator.eventsController.cleanEventsData()
    BigWorld.purgeUrlRequestCache()


def onKickedFromServer(reason, kickReasonType, expiryTime):
    ServicesLocator.gameplay.goToLoginByKick(reason, kickReasonType, expiryTime)


def onScreenShotMade(path):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.SCREEN_SHOT_MADE, {'path': path}), scope=EVENT_BUS_SCOPE.GLOBAL)


def disableLobbyGUI():
    ServicesLocator.appLoader.fini()
    from gui.Scaleform.app_factory import createAppFactory
    ServicesLocator.appLoader.init(createAppFactory(True))


def onRecreateDevice():
    for c in g_guiResetters:
        try:
            c()
        except Exception:
            LOG_CURRENT_EXCEPTION()


@process
def __runChain(chain, ctx, currentIdx=0):
    if currentIdx < len(chain):
        ts = time.time()
        result = yield chain[currentIdx](ctx)
        te = time.time()
        rt = te - ts
        _logger.info('%s elapsed time: %s sec', chain[currentIdx].__name__, rt)
        if result:
            currentIdx += 1
            BigWorld.callback(0.0, partial(__runChain, chain, ctx, currentIdx))
        else:
            del chain[:]
    else:
        del chain[:]


@async
@process
def __runItemsCacheSync(_, callback=None):
    playerRef = weakref.ref(BigWorld.player())
    yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI, notify=False)
    if not ServicesLocator.itemsCache.isSynced():
        ServicesLocator.gameplay.goToLoginByError('#menu:disconnect/codes/0')
        callback(False)
        return
    if not playerRef():
        _logger.warn('onAccountShowGUI(): the item cache update callback has been called for an already deleted PlayerAccount object.')
        callback(False)
        return
    callback(True)


@async
@process
def __runQuestSync(_, callback=None):
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.QUESTS_SYNC)
    ServicesLocator.eventsCache.start()
    yield ServicesLocator.eventsCache.update()
    callback(True)


@async
@process
def __runSettingsSync(_, callback=None):
    ServicesLocator.gameEventController.start()
    ServicesLocator.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.USER_SERVER_SETTINGS_SYNC)
    yield ServicesLocator.settingsCache.update()
    ServicesLocator.settingsCore.serverSettings.applySettings()
    callback(True)


@async
@process
def __processEULA(_, callback=None):
    eula = EULADispatcher()
    yield eula.processLicense()
    eula.fini()
    callback(True)


def __processValidator(validator, callback):
    code = validator.validate()
    if code != ValidationCodes.OK:
        ServicesLocator.gameplay.goToLoginByError('#menu:disconnect/codes/{}'.format(code))
        callback(False)
        return
    callback(True)


@async
def __validateInventoryVehicles(_, callback=None):
    __processValidator(InventoryVehiclesValidator(), callback)


@async
def __validateInventoryOutfit(_, callback=None):
    __processValidator(InventoryOutfitValidator(), callback)


@async
def __validateInventoryTankmen(_, callback=None):
    __processValidator(InventoryTankmenValidator(), callback)


@async
def __notifyOnSyncComplete(ctx, callback=None):
    playerRef = weakref.ref(BigWorld.player())
    g_playerEvents.onGuiCacheSyncCompleted(ctx)
    ServicesLocator.itemsCache.onSyncCompleted(CACHE_SYNC_REASON.SHOW_GUI, {})
    if not playerRef():
        _logger.warn('onSyncCompleted(): the item cache update callback has been called for an already deleted PlayerAccount object.')
        callback(False)
        return
    ServicesLocator.gameState.onAccountShowGUI(ServicesLocator.lobbyContext.getGuiCtx())
    callback(True)


@async
def __requestDossier(_, callback=None):
    accDossier = ServicesLocator.itemsCache.items.getAccountDossier()
    ServicesLocator.rareAchievesCache.request(accDossier.getBlock('rareAchievements'))
    callback(True)


@async
def __initializeHangarSpace(_, callback=None):
    premium = ServicesLocator.itemsCache.items.stats.isPremium
    if ServicesLocator.hangarSpace.inited:
        ServicesLocator.hangarSpace.refreshSpace(premium)
    else:
        ServicesLocator.hangarSpace.init(premium)
    g_currentVehicle.init()
    g_currentPreviewVehicle.init()
    callback(True)


@async
def __initializeHangar(ctx=None, callback=None):
    ServicesLocator.soundCtrl.start()
    SoundGroups.g_instance.enableLobbySounds(True)
    ServicesLocator.gameplay.postStateEvent(PlayerEventID.ACCOUNT_SHOW_GUI)
    g_prbLoader.onAccountShowGUI(ServicesLocator.lobbyContext.getGuiCtx())
    g_clanCache.onAccountShowGUI()
    g_blueprintGenerator.init()
    onCenterIsLongDisconnected(True)
    ServicesLocator.offersProvider.start()
    guiModsSendEvent('onAccountShowGUI', ctx)
    callback(True)


@async
@process
def __processWebCtrl(_, callback=None):
    serverSettings = ServicesLocator.lobbyContext.getServerSettings()
    ServicesLocator.webCtrl.start()
    if serverSettings.wgcg.getLoginOnStart() and not ServicesLocator.bootcamp.isInBootcamp():
        yield ServicesLocator.webCtrl.login()
    callback(True)


@async
@process
def __processElen(_, callback=None):
    serverSettings = ServicesLocator.lobbyContext.getServerSettings()
    if serverSettings.isElenEnabled():
        yield ServicesLocator.eventsController.getEvents(onlySettings=True, onLogin=True, prefetchKeyArtBig=False)
        yield ServicesLocator.eventsController.getHangarFlag(onLogin=True)
    callback(True)
