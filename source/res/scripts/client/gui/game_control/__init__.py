# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/__init__.py
import constants
from skeletons.festivity_factory import IFestivityFactory
from shared_utils import CONST_CONTAINER

class CalendarInvokeOrigin(CONST_CONTAINER):
    ACTION = 'action'
    HANGAR = 'hangar'
    SPLASH = 'first'
    BANNER = 'banner'


def getGameControllersConfig(manager):
    from gui.game_control.AOGAS import AOGASController as _AOGAS
    from gui.game_control.AwardController import AwardController as _Awards
    from gui.game_control.anonymizer_controller import AnonymizerController as _Anonymizer
    from gui.game_control.BoostersController import BoostersController as _Boosters
    from gui.game_control.BrowserController import BrowserController as _Browser
    from gui.game_control.ChinaController import ChinaController as _China
    from gui.game_control.ChinaController import NoChinaController as _NoChina
    from gui.game_control.links_handlers import ExternalLinksHandler as _ExternalLinks
    from gui.game_control.GameSessionController import GameSessionController as _GameSessions
    from gui.game_control.IGR import IGRController as _IGR
    from gui.game_control.links_handlers import InternalLinksHandler as _InternalLinks
    from gui.game_control.NotifyController import NotifyController as _Notify
    from gui.game_control.PromoController import PromoController as _Promos
    from gui.game_control.RentalsController import RentalsController as _Rentals
    from gui.game_control.seasons_controller import SeasonsController as _Seasons
    from gui.game_control.ServerStats import ServerStats as _ServerStats
    from gui.game_control.SoundEventChecker import SoundEventChecker as _Sounds
    from gui.game_control.clan_lock_controller import ClanLockController as _ClanLocks
    from gui.game_control.events_notifications import EventsNotificationsController as _EventNotifications
    from gui.game_control.relogin_controller import ReloginController as _Relogin
    from gui.game_control.restore_contoller import RestoreController as _Restore
    from gui.game_control.screencast_controller import ScreenCastController as _ScreenCast
    from gui.game_control.state_tracker import GameStateTracker
    from gui.game_control.veh_comparison_basket import VehComparisonBasket as _VehComparison
    from gui.game_control.wallet import WalletController as _Wallet
    from gui.game_control.trade_in import TradeInController as _TradeIn
    from gui.game_control.personal_trade_in import PersonalTradeInController as _PersonalTradeIn
    from gui.game_control.quests_controller import QuestsController as _Quests
    from gui.game_control.ranked_battles_controller import RankedBattlesController as _Ranked
    from gui.game_control.hangar_loading_controller import HangarLoadingController as _HangarLoading
    from gui.game_control.battle_royale_controller import BattleRoyaleController as _BattleRoyale
    from gui.game_control.battle_royale_tournament_controller import BattleRoyaleTournamentController as _BRTournament
    from gui.game_control.epic_mode_controller import EpicModeController as _Epic
    from gui.game_control.bootcamp_controller import BootcampController as _Bootcamp
    from gui.game_control.hero_tank_controller import HeroTankController as _HeroTankController
    from gui.game_control.platoon_controller import PlatoonController as _PlatoonController
    from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController as _EpicMeta
    from gui.game_control.manual_controller import ManualController as _ManualController
    from gui.game_control.calendar_controller import CalendarController as _Calendar
    from gui.marathon.marathon_event_controller import MarathonEventsController as _MarathonEventsController
    from skeletons.gui import game_control as _interface
    from gui.game_control.referral_program_controller import ReferralProgramController as _ReferralController
    from gui.game_control.badges_controller import BadgesController as _Badges
    from gui.game_control.special_sound_ctrl import SpecialSoundCtrl as _SpecialSoundCtrl
    from gui.game_control.battle_pass_controller import BattlePassController
    from gui.game_control.clan_notification_controller import ClanNotificationController as _ClanNotification
    from gui.game_control.craftmachine_controller import CraftmachineController
    from gui.game_control.reactive_comm import ReactiveCommunicationService
    from gui.game_control.maps_training_controller import MapsTrainingController as _MapsTrainingController
    from gui.ui_spam.ui_spam_controller import UISpamController
    from gui.game_control.blueprints_convert_sale_controller import BlueprintsConvertSaleController
    from gui.game_control.mapbox_controller import MapboxController
    from gui.game_control.overlay import OverlayController as _OverlayController
    from gui.game_control.account_completion import SteamCompletionController as _SteamCompletionController, DemoAccCompletionController as _DemoAccCompletionController
    from gui.game_control.veh_post_progression_controller import VehiclePostProgressionController
    from gui.game_control.seniority_awards_controller import SeniorityAwardsController as _SeniorityAwardsController
    from gui.game_control.wot_plus_controller import WotPlusNotificationController
    from gui.game_control.telecom_rentals_controller import TelecomRentalsNotificationController
    from gui.game_control.event_battles_controller import EventBattlesController
    from gui.game_control.gift_system_controller import GiftSystemController
    from gui.game_control.wo_controller import WOController as _WOController
    from skeletons import new_year as _NYInterface
    from new_year.ny_jukebox_controller import JukeboxController as _JukeboxController
    from new_year.celebrity.celebrity_scene_ctrl import CelebritySceneController as _CelebritySceneController
    from new_year.craft_machine_controller import NewYearCraftMachineController as _NewYearCraftMachineController
    tracker = GameStateTracker()
    tracker.init()
    manager.addInstance(_interface.IGameStateTracker, tracker, finalizer='fini')

    def _config(interface, controller):
        tracker.addController(controller)
        controller.init()
        manager.addInstance(interface, controller, finalizer='fini')

    _config(_interface.IFestivityController, manager.getService(IFestivityFactory).getController())
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
    _config(_interface.IBrowserController, _Browser())
    _config(_interface.IEventsNotificationsController, _EventNotifications())
    _config(_interface.IPromoController, _Promos())
    _config(_interface.IAwardController, _Awards())
    _config(_interface.IBoostersController, _Boosters())
    _config(_interface.IScreenCastController, _ScreenCast())
    _config(_interface.IClanLockController, _ClanLocks())
    _config(_interface.IVehicleComparisonBasket, _VehComparison())
    _config(_interface.ITradeInController, _TradeIn())
    _config(_interface.IPersonalTradeInController, _PersonalTradeIn())
    _config(_interface.IQuestsController, _Quests())
    _config(_interface.IBootcampController, _Bootcamp())
    _config(_interface.IRankedBattlesController, _Ranked())
    _config(_interface.IEpicModeController, _Epic())
    _config(_interface.IHeroTankController, _HeroTankController())
    _config(_interface.IPlatoonController, _PlatoonController())
    _config(_interface.IMarathonEventsController, _MarathonEventsController())
    _config(_interface.ICalendarController, _Calendar())
    _config(_interface.IWOController, _WOController())
    _config(_interface.IEpicBattleMetaGameController, _EpicMeta())
    _config(_interface.IBattleRoyaleController, _BattleRoyale())
    _config(_interface.IBattleRoyaleTournamentController, _BRTournament())
    _config(_interface.IManualController, _ManualController())
    _config(_interface.IReferralProgramController, _ReferralController())
    _config(_interface.ISpecialSoundCtrl, _SpecialSoundCtrl())
    _config(_interface.IBattlePassController, BattlePassController())
    _config(_interface.IHangarLoadingController, _HangarLoading())
    if constants.IS_CHINA:
        _config(_interface.IChinaController, _China())
    else:
        _config(_interface.IChinaController, _NoChina())
    _config(_interface.IMapboxController, MapboxController())
    _config(_interface.IEventBattlesController, EventBattlesController())
    _config(_interface.ISeasonsController, _Seasons())
    _config(_interface.IBadgesController, _Badges())
    _config(_interface.IAnonymizerController, _Anonymizer())
    _config(_interface.ICraftmachineController, CraftmachineController())
    _config(_interface.IClanNotificationController, _ClanNotification())
    _config(_interface.IReactiveCommunicationService, ReactiveCommunicationService())
    _config(_interface.IMapsTrainingController, _MapsTrainingController())
    _config(_interface.IUISpamController, UISpamController())
    _config(_interface.IBlueprintsConvertSaleController, BlueprintsConvertSaleController())
    _config(_interface.IOverlayController, _OverlayController())
    _config(_interface.ISteamCompletionController, _SteamCompletionController())
    _config(_interface.IDemoAccCompletionController, _DemoAccCompletionController())
    _config(_interface.IVehiclePostProgressionController, VehiclePostProgressionController())
    _config(_interface.ISeniorityAwardsController, _SeniorityAwardsController())
    _config(_interface.IWotPlusNotificationController, WotPlusNotificationController())
    _config(_interface.ITelecomRentalsNotificationController, TelecomRentalsNotificationController())
    _config(_interface.IGiftSystemController, GiftSystemController())
    _config(_NYInterface.IJukeboxController, _JukeboxController())
    _config(_NYInterface.ICelebritySceneController, _CelebritySceneController())
    _config(_NYInterface.INewYearCraftMachineController, _NewYearCraftMachineController())
