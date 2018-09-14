# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/__init__.py
import constants
from gui.shared import g_eventBus, events
from gui.game_control.controllers import ControllersCollection
from gui.game_control.gc_constants import CONTROLLER
from gui.game_control.AOGAS import AOGASController as _AOGAS
from gui.game_control.AwardController import AwardController as _Awards
from gui.game_control.BoostersController import BoostersController as _Boosters
from gui.game_control.BrowserController import BrowserController as _Browser
from gui.game_control.ChinaController import ChinaController as _China
from gui.game_control.ExternalLinksHandler import ExternalLinksHandler as _ExternalLinks
from gui.game_control.GameSessionController import GameSessionController as _GameSessions
from gui.game_control.IGR import IGRController as _IGR
from gui.game_control.InternalLinksHandler import InternalLinksHandler as _InternalLinks
from gui.game_control.prmp_controller import EncyclopediaController as _Exncyclopedia
from gui.game_control.screencast_controller import ScreenCastController as _ScreenCast
from gui.game_control.NotifyController import NotifyController as _Notify
from gui.game_control.restore_contoller import RestoreController as _Restore
from gui.game_control.PromoController import PromoController as _Promos
from gui.game_control.RefSystem import RefSystem as _RefSystem
from gui.game_control.RentalsController import RentalsController as _Rentals
from gui.game_control.ServerStats import ServerStats as _ServerStats
from gui.game_control.SoundEventChecker import SoundEventChecker as _Sounds
from gui.game_control.clan_lock_controller import ClanLockController as _ClanLocks
from gui.game_control.events_notifications import EventsNotificationsController as _EventNotifications
from gui.game_control.fallout_controller import FalloutController as _Fallout
from gui.game_control.relogin_controller import ReloginController as _Relogin
from gui.game_control.veh_comparison_basket import VehComparisonBasket as _VehComparison
from gui.game_control.wallet import WalletController as _Wallet

class _GameControllers(ControllersCollection):

    def __init__(self):
        super(_GameControllers, self).__init__({CONTROLLER.RELOGIN: _Relogin,
         CONTROLLER.AOGAS: _AOGAS,
         CONTROLLER.GAME_SESSION: _GameSessions,
         CONTROLLER.RENTALS: _Rentals,
         CONTROLLER.RESTORE: _Restore,
         CONTROLLER.IGR: _IGR,
         CONTROLLER.WALLET: _Wallet,
         CONTROLLER.NOTIFIER: _Notify,
         CONTROLLER.LINKS: _ExternalLinks,
         CONTROLLER.INTERNAL_LINKS: _InternalLinks,
         CONTROLLER.SOUND_CHECKER: _Sounds,
         CONTROLLER.SERVER_STATS: _ServerStats,
         CONTROLLER.REF_SYSTEM: _RefSystem,
         CONTROLLER.BROWSER: _Browser,
         CONTROLLER.PROMO: _Promos,
         CONTROLLER.EVENTS_NOTIFICATION: _EventNotifications,
         CONTROLLER.AWARD: _Awards,
         CONTROLLER.BOOSTERS: _Boosters,
         CONTROLLER.FALLOUT: _Fallout,
         CONTROLLER.SCREENCAST: _ScreenCast,
         CONTROLLER.CLAN_LOCK: _ClanLocks,
         CONTROLLER.VEH_COMPARISON_BASKET: _VehComparison,
         CONTROLLER.ENCYCLOPEDIA: _Exncyclopedia})
        if constants.IS_CHINA:
            self._addController(CONTROLLER.CHINA, _China)
        self.__collectUiStats = True
        self.__logUXEvents = False

    def init(self):
        super(_GameControllers, self).init()
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)

    def fini(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)
        super(_GameControllers, self).fini()

    @property
    def collectUiStats(self):
        return self.__collectUiStats

    @property
    def needLogUXEvents(self):
        return self.__logUXEvents

    def onAccountShowGUI(self, ctx):
        self.onLobbyStarted(ctx)
        self.__collectUiStats = ctx.get('collectUiStats', True)
        self.__logUXEvents = ctx.get('logUXEvents', False)


g_instance = _GameControllers()

def getEventsNotificationCtrl():
    return _getController(CONTROLLER.EVENTS_NOTIFICATION)


def getBrowserCtrl():
    return _getController(CONTROLLER.BROWSER)


def getChinaCtrl():
    assert constants.IS_CHINA, 'China controller only available if IS_CHINA = True'
    return _getController(CONTROLLER.CHINA)


def getIGRCtrl():
    return _getController(CONTROLLER.IGR)


def getRefSysCtrl():
    return _getController(CONTROLLER.REF_SYSTEM)


def getRoamingCtrl():
    return _getController(CONTROLLER.RELOGIN)


def getWalletCtrl():
    return _getController(CONTROLLER.WALLET)


def getFalloutCtrl():
    return _getController(CONTROLLER.FALLOUT)


def getVehicleComparisonBasketCtrl():
    return _getController(CONTROLLER.VEH_COMPARISON_BASKET)


def getEncyclopediaController():
    return _getController(CONTROLLER.ENCYCLOPEDIA)


def getPromoController():
    return _getController(CONTROLLER.PROMO)


def getRestoreController():
    return _getController(CONTROLLER.RESTORE)


def _getController(controller):
    return g_instance.getController(controller)
