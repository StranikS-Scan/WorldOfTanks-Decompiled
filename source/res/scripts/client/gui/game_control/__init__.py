# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/__init__.py
import constants

def getGameControllersConfig(manager):
    """ Configures services for package game_control.
    :param manager: instance of dependency manager.
    """
    from gui.game_control.AOGAS import AOGASController as _AOGAS
    from gui.game_control.AwardController import AwardController as _Awards
    from gui.game_control.BoostersController import BoostersController as _Boosters
    from gui.game_control.BrowserController import BrowserController as _Browser
    from gui.game_control.ChinaController import ChinaController as _China
    from gui.game_control.ChinaController import NoChinaController as _NoChina
    from gui.game_control.ExternalLinksHandler import ExternalLinksHandler as _ExternalLinks
    from gui.game_control.GameSessionController import GameSessionController as _GameSessions
    from gui.game_control.IGR import IGRController as _IGR
    from gui.game_control.InternalLinksHandler import InternalLinksHandler as _InternalLinks
    from gui.game_control.NotifyController import NotifyController as _Notify
    from gui.game_control.PromoController import PromoController as _Promos
    from gui.game_control.RefSystem import RefSystem as _RefSystem
    from gui.game_control.RentalsController import RentalsController as _Rentals
    from gui.game_control.ServerStats import ServerStats as _ServerStats
    from gui.game_control.SoundEventChecker import SoundEventChecker as _Sounds
    from gui.game_control.clan_lock_controller import ClanLockController as _ClanLocks
    from gui.game_control.events_notifications import EventsNotificationsController as _EventNotifications
    from gui.game_control.fallout_controller import FalloutController as _Fallout
    from gui.game_control.prmp_controller import EncyclopediaController as _Exncyclopedia
    from gui.game_control.relogin_controller import ReloginController as _Relogin
    from gui.game_control.restore_contoller import RestoreController as _Restore
    from gui.game_control.screencast_controller import ScreenCastController as _ScreenCast
    from gui.game_control.state_tracker import GameStateTracker
    from gui.game_control.veh_comparison_basket import VehComparisonBasket as _VehComparison
    from gui.game_control.wallet import WalletController as _Wallet
    from gui.game_control.trade_in import TradeInController as _TradeIn
    from gui.game_control.quests_controller import QuestsController as _Quests
    from gui.game_control.ranked_battles_controller import RankedBattlesController as _Ranked
    from gui.game_control.bootcamp_controller import BootcampController as _Bootcamp
    from skeletons.gui import game_control as _interface
    tracker = GameStateTracker()
    tracker.init()
    manager.addInstance(_interface.IGameStateTracker, tracker, finalizer='fini')

    def _config(interface, controller):
        tracker.addController(controller)
        controller.init()
        manager.addInstance(interface, controller, finalizer='fini')

    _config(_interface.IReloginController, _Relogin())
    _config(_interface.IAOGASController, _AOGAS())
    _config(_interface.IGameSessionController, _GameSessions())
    _config(_interface.IRentalsController, _Rentals())
    _config(_interface.IRestoreController, _Restore())
    _config(_interface.IIGRController, _IGR())
    _config(_interface.IWalletController, _Wallet())
    _config(_interface.INotifyController, _Notify())
    _config(_interface.IExternalLinksController, _ExternalLinks())
    _config(_interface.IInternalLinksController, _InternalLinks())
    _config(_interface.ISoundEventChecker, _Sounds())
    _config(_interface.IServerStatsController, _ServerStats())
    _config(_interface.IRefSystemController, _RefSystem())
    _config(_interface.IBrowserController, _Browser())
    _config(_interface.IEventsNotificationsController, _EventNotifications())
    _config(_interface.IPromoController, _Promos())
    _config(_interface.IAwardController, _Awards())
    _config(_interface.IBoostersController, _Boosters())
    _config(_interface.IFalloutController, _Fallout())
    _config(_interface.IScreenCastController, _ScreenCast())
    _config(_interface.IClanLockController, _ClanLocks())
    _config(_interface.IVehicleComparisonBasket, _VehComparison())
    _config(_interface.IEncyclopediaController, _Exncyclopedia())
    _config(_interface.ITradeInController, _TradeIn())
    _config(_interface.IQuestsController, _Quests())
    _config(_interface.IBootcampController, _Bootcamp())
    _config(_interface.IRankedBattlesController, _Ranked())
    if constants.IS_CHINA:
        _config(_interface.IChinaController, _China())
    else:
        _config(_interface.IChinaController, _NoChina())
