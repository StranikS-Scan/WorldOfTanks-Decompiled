# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountSettings.py
import base64
import cPickle as pickle
import copy
import logging
from copy import deepcopy
import typing
import BigWorld
import CommandMapping
import Event
import Settings
import WWISE
import constants
import nations
from account_helpers import gameplay_ctx
from account_helpers.settings_core.settings_constants import AIM, BATTLE_EVENTS, BattleCommStorageKeys, CONTOUR, GAME, GuiSettingsBehavior, SOUND, SPGAim, ScorePanelStorageKeys
from aih_constants import CTRL_MODE_NAME
from constants import MAX_VEHICLE_LEVEL, VEHICLE_CLASSES
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.genConsts.MISSIONS_CONSTANTS import MISSIONS_CONSTANTS
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.collection.collections_constants import COLLECTIONS_UPDATED_ENTRY_SEEN, COLLECTION_RENEW_SEEN, COLLECTION_START_SEEN
from gui.integrated_auction.constants import AUCTION_FINISH_STAGE_SEEN, AUCTION_STAGE_START_SEEN
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from helpers import dependency, getClientVersion
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.account_helpers.settings_core import ISettingsCore
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from typing import List, Optional, Iterable
_logger = logging.getLogger(__name__)
KEY_FILTERS = 'filters'
KEY_SESSION_SETTINGS = 'session_settings'
KEY_SETTINGS = 'settings'
KEY_FAVORITES = 'favorites'
KEY_COUNTERS = 'counters'
KEY_NOTIFICATIONS = 'notifications'
KEY_UI_FLAGS = 'ui_flags'
KEY_MANUAL = 'manual'
KEY_BATTLE_HINTS = 'battle_hints'
KEY_NEWBIE_HINTS = 'newbie_hints'
CAROUSEL_FILTER_1 = 'CAROUSEL_FILTER_1'
CAROUSEL_FILTER_2 = 'CAROUSEL_FILTER_2'
CAROUSEL_FILTER_CLIENT_1 = 'CAROUSEL_FILTER_CLIENT_1'
MISSION_SELECTOR_FILTER = 'MISSION_SELECTOR_FILTER'
PM_SELECTOR_FILTER = 'PM_SELECTOR_FILTER'
RANKED_CAROUSEL_FILTER_1 = 'RANKED_CAROUSEL_FILTER_1'
RANKED_CAROUSEL_FILTER_2 = 'RANKED_CAROUSEL_FILTER_2'
RANKED_CAROUSEL_FILTER_CLIENT_1 = 'RANKED_CAROUSEL_FILTER_CLIENT_1'
EPICBATTLE_CAROUSEL_FILTER_1 = 'EPICBATTLE_CAROUSEL_FILTER_1'
EPICBATTLE_CAROUSEL_FILTER_2 = 'EPICBATTLE_CAROUSEL_FILTER_2'
EPICBATTLE_CAROUSEL_FILTER_CLIENT_1 = 'EPICBATTLE_CAROUSEL_FILTER_CLIENT_1'
EPICBATTLE_CAROUSEL_FILTER_CLIENT_2 = 'EPICBATTLE_CAROUSEL_FILTER_CLIENT_2'
STORAGE_VEHICLES_CAROUSEL_FILTER_1 = 'STORAGE_CAROUSEL_FILTER_1'
STORAGE_BLUEPRINTS_CAROUSEL_FILTER = 'STORAGE_BLUEPRINTS_CAROUSEL_FILTER'
BATTLEPASS_CAROUSEL_FILTER_1 = 'BATTLEPASS_CAROUSEL_FILTER_1'
BATTLEPASS_CAROUSEL_FILTER_CLIENT_1 = 'BATTLEPASS_CAROUSEL_FILTER_CLIENT_1'
ROYALE_CAROUSEL_FILTER_1 = 'ROYALE_CAROUSEL_FILTER_1'
ROYALE_CAROUSEL_FILTER_2 = 'ROYALE_CAROUSEL_FILTER_2'
ROYALE_CAROUSEL_FILTER_CLIENT_1 = 'ROYALE_CAROUSEL_FILTER_CLIENT_1'
ROYALE_INTRO_VIDEO_SHOWN = 'ROYALE_INTRO_VIDEO_SHOWN'
ROYALE_SQUAD_TIP_SHOWN_FOR_SEASON = 'ROYALE_SQUAD_TIP_SHOWN_FOR_SEASON'
MAPBOX_CAROUSEL_FILTER_1 = 'MAPBOX_CAROUSEL_FILTER_1'
MAPBOX_CAROUSEL_FILTER_2 = 'MAPBOX_CAROUSEL_FILTER_2'
MAPBOX_CAROUSEL_FILTER_CLIENT_1 = 'MAPBOX_CAROUSEL_FILTER_CLIENT_1'
FUN_RANDOM_CAROUSEL_FILTER_1 = 'FUN_RANDOM_CAROUSEL_FILTER_1'
FUN_RANDOM_CAROUSEL_FILTER_2 = 'FUN_RANDOM_CAROUSEL_FILTER_2'
FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1 = 'FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1'
COMP7_CAROUSEL_FILTER_1 = 'COMP7_CAROUSEL_FILTER_1'
COMP7_CAROUSEL_FILTER_2 = 'COMP7_CAROUSEL_FILTER_2'
COMP7_CAROUSEL_FILTER_CLIENT_1 = 'COMP7_CAROUSEL_FILTER_CLIENT_1'
COMP7_PREBATTLE_CAROUSEL_ROW_VALUE = 'comp7PrebattleCarouselRowValue'
COMP7_IS_VOIP_IN_BATTLE_ACTIVATED = 'comp7IsVoipInBattleActivated'
COMP7_ENTITLEMENTS = 'comp7Entitlements'
COMP7_ENTITLEMENTS_TIMESTAMP = 'timestamp'
COMP7_ENTITLEMENTS_BALANCE = 'balance'
ORDERS_FILTER = 'ORDERS_FILTER'
CURRENT_VEHICLE = 'current'
ROYALE_VEHICLE = 'ROYALE_VEHICLE'
LOBBY_MENU_MANUAL_TRIGGER_SHOWN = 'lobby_menu_manual_trigger_shown'
MANUAL_NEW_CONTENT = 'manual_new_content'
GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
EULA_VERSION = 'EULA_VERSION'
FORT_MEMBER_TUTORIAL = 'FORT_MEMBER_TUTORIAL'
IGR_PROMO = 'IGR_PROMO'
PROMO = 'PROMO'
CONTACTS = 'CONTACTS'
FALLOUT_VEHICLES = 'FALLOUT_VEHICLES'
GOLD_FISH_LAST_SHOW_TIME = 'goldFishWindowShowCooldown'
BOOSTERS_FILTER = 'boostersFilter'
LAST_PROMO_PATCH_VERSION = 'lastPromoPatchVersion'
LAST_CALENDAR_SHOW_TIMESTAMP = 'lastCalendarShowTimestamp'
LAST_STORAGE_VISITED_TIMESTAMP = 'lastStorageVisitedTimestamp'
LAST_RESTORE_NOTIFICATION = 'lastRestoreNotification'
PREVIEW_INFO_PANEL_IDX = 'previewInfoPanelIdx'
NEW_SETTINGS_COUNTER = 'newSettingsCounter'
NEW_HOF_COUNTER = 'newHofCounter'
NEW_LOBBY_TAB_COUNTER = 'newLobbyTabCounter'
REFERRAL_COUNTER = 'referralButtonCounter'
CLAN_NOTIFICATION_COUNTERS = 'ClanButtonNewsCounters'
PROGRESSIVE_REWARD_VISITED = 'progressiveRewardVisited'
RANKED_AWARDS_COUNTER = 'rankedAwardsCounter'
RANKED_INFO_COUNTER = 'rankedInfoCounter'
RANKED_YEAR_RATING_COUNTER = 'rankedYearRatingCounter'
RANKED_SHOP_COUNTER = 'rankedShopCounter'
BOOSTERS_FOR_CREDITS_SLOT_COUNTER = 'boostersForCreditsSlotCounter'
SENIORITY_AWARDS_COUNTER = 'seniorityAwardsCounter'
SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP = 'saReminderShown'
DEMOUNT_KIT_SEEN = 'demountKitSeen'
RECERTIFICATION_FORM_SEEN = 'recertificationFormSeen'
VIEWED_OFFERS = 'viewedOffers'
OFFERS_DISABLED_MSG_SEEN = 'offersDisabledMsgSeen'
PROFILE_TECHNIQUE = 'profileTechnique'
PROFILE_TECHNIQUE_MEMBER = 'profileTechniqueMember'
SHOW_CRYSTAL_HEADER_BAND = 'showCrystalHeaderBand'
ELEN_NOTIFICATIONS = 'elenNotifications'
RECRUIT_NOTIFICATIONS = 'recruitNotifications'
SPEAKERS_DEVICE = 'speakersDevice'
SESSION_STATS_PREV_BATTLE_COUNT = 'sessionStatsPrevBattleCnt'
UNIT_FILTER = 'UNIT_FILTER'
BLUEPRINTS_CONVERT_SALE_STARTED_SEEN = 'bcsStartedSeen'
IS_SHOP_VISITED = 'isShopVisited'
LAST_SHOP_ACTION_COUNTER_MODIFICATION = 'lastShopActionCounterModification'
OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES = 'overridenHeaderCounterActionAliases'
STORE_TAB = 'store_tab'
STATS_REGULAR_SORTING = 'statsSorting'
STATS_SORTIE_SORTING = 'statsSortingSortie'
STATS_COMP7_SORTING = 'statsSortingComp7'
MISSIONS_PAGE = 'missions_page'
DEFAULT_VEHICLE_TYPES_FILTER = [False] * len(VEHICLE_CLASSES)
DEFAULT_LEVELS_FILTERS = [False] * MAX_VEHICLE_LEVEL
SHOW_OPT_DEVICE_HINT = 'showOptDeviceHint'
SHOW_OPT_DEVICE_HINT_TROPHY = 'showOptDeviceHintTrophy'
SHOW_OPT_MODERNIZED_DEVICE_HINT = 'showOptModernizedDeviceHint'
LAST_BADGES_VISIT = 'lastBadgesVisit'
LAST_SELECTED_SUFFIX_BADGE_ID = 'lastSelectedSuffixBadgeID'
ENABLE_RANKED_ANIMATIONS = 'enableRankedAnimations'
COLOR_SETTINGS_TAB_IDX = 'colorSettingsTabIdx'
COLOR_SETTINGS_SHOWS_COUNT = 'colorSettingsShowsCount'
APPLIED_COLOR_SETTINGS = 'appliedColorSettings'
SELECTED_QUEST_IN_REPLAY = 'SELECTED_QUEST_IN_REPLAY'
LAST_SELECTED_PM_BRANCH = 'lastSelectedPMBranch'
WHEELED_DEATH_DELAY_COUNT = 'wheeledDeathCounter'
FREE_CAM_USES_COUNT = 'killCamBattlesCount'
LAST_BATTLE_PASS_POINTS_SEEN = 'lastBattlePassPointsSeen'
BR_PROGRESSION_POINTS_SEEN = 'brProgressionPointsSeen'
IS_BATTLE_PASS_EXTRA_STARTED = 'isBattlePassExtraStarted'
IS_BATTLE_PASS_COLLECTION_SEEN = 'isCollectionSeen'
CRYSTALS_INFO_SHOWN = 'crystalsInfoShown'
IS_CUSTOMIZATION_INTRO_VIEWED = 'isCustomizationIntroViewed'
CUSTOMIZATION_STYLE_ITEMS_VISITED = 'CustomizationStyleItemsVisited'
OPT_DEVICE_TAB_VISITED = 'optDeviceTabVisited'
ANONYMIZER = GAME.ANONYMIZER
CUSTOMIZATION_SECTION = 'customization'
CAROUSEL_ARROWS_HINT_SHOWN_FIELD = 'isCarouselsArrowsHintShown'
PROJECTION_DECAL_HINT_SHOWN_FIELD = 'isProjectionDecalHintShown'
SESSION_STATS_SECTION = 'sessionStats'
BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD = 'battleEfficiencySectionExpanded'
SIEGE_HINT_SECTION = 'siegeModeHint'
WHEELED_MODE_HINT_SECTION = 'wheeledModeScreenHint'
TRAJECTORY_VIEW_HINT_SECTION = 'trajectoryViewHint'
TURBO_SHAFT_ENGINE_MODE_HINT_SECTION = 'turboShaftEngineModeHint'
ROCKET_ACCELERATION_MODE_HINT_SECTION = 'rocketAccelerationModeHint'
DYN_SQUAD_HINT_SECTION = 'dynSquadHint'
RADAR_HINT_SECTION = 'radarHint'
PRE_BATTLE_HINT_SECTION = 'preBattleHintSection'
PRE_BATTLE_ROLE_HINT_SECTION = 'preBattleRoleHintSection'
FUN_RANDOM_HINT_SECTION = 'funRandomHintSection'
MAPBOX_HINT_SECTION = 'mapboxHintSection'
QUEST_PROGRESS_HINT_SECTION = 'questProgressHint'
HELP_SCREEN_HINT_SECTION = 'helpScreenHint'
IBC_HINT_SECTION = 'battleCommunicationHint'
RESERVES_HINT_SECTION = 'reservesHintSection'
COMMANDER_CAM_HINT_SECTION = 'commanderCamHintSection'
MINIMAP_IBC_HINT_SECTION = 'minimapHintSection'
DEV_MAPS_HINT_SECTION = 'devMapsHintSection'
WATCHED_PRE_BATTLE_TIPS_SECTION = 'watchedPreBattleTipsSection'
LAST_DISPLAY_DAY = 'lastDisplayDay'
HINTS_LEFT = 'hintsLeft'
NUM_BATTLES = 'numBattles'
SELECTED_INTRO_VEHICLES_FIELD = 'selectedIntroVehicles'
NATION_CHANGE_VIEWED = 'nation_change_viewed'
CREW_SKINS_VIEWED = 'crew_skins_viewed'
CREW_BOOKS_VIEWED = 'crew_books_viewed'
CREW_SKINS_HISTORICAL_VISIBLE = 'crew_skins_historical_visible'
VEHICLES_WITH_BLUEPRINT_CONFIRM = 'showedBlueprintConfirm'
IS_FIRST_ENTRY_BY_DIVISION_ID = 'isFirstEntryByDivisionId'
RANKED_STYLED_VEHICLES_POOL = 'rankedStyledVehiclesPool'
STYLE_PREVIEW_VEHICLES_POOL = 'stylePreviewVehiclesPool'
RANKED_WEB_INFO = 'rankedWebLeague'
RANKED_WEB_INFO_UPDATE = 'rankedWebLeagueUpdate'
RANKED_AWARDS_BUBBLE_YEAR_REACHED = 'rankedAwardsBubbleYearReached'
RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED = 'rankedCurrentAwardsBubbleYearReached'
RANKED_ENTITLEMENT_EVENTS_AMOUNT = 'rankedEntitlementEventsAmount'
RANKED_YEAR_POSITION = 'rankedYearPosition'
MARATHON_REWARD_WAS_SHOWN_PREFIX = 'marathonRewardScreenWasShown'
MARATHON_VIDEO_WAS_SHOWN_PREFIX = 'marathonRewardVideoWasShown'
SUBTITLES = 'subtitles'
MODULES_ANIMATION_SHOWN = 'collectibleVehiclesAnimWasShown'
NEW_SHOP_TABS = 'newShopTabs'
IS_COLLECTIBLE_VEHICLES_VISITED = 'isCollectibleVehiclesVisited'
LAST_SHOP_TAB_COUNTER = 'lastShopTabCounter'
QUESTS = 'quests'
QUEST_DELTAS = 'questDeltas'
QUEST_DELTAS_COMPLETION = 'questCompletion'
QUEST_DELTAS_PROGRESS = 'questProgress'
QUEST_DELTAS_TOKENS_PROGRESS = 'tokensProgress'
TOP_OF_TREE_CONFIG = 'topOfTree'
DOG_TAGS = 'dogTags'
WOT_PLUS = 'wotPlus'
TELECOM_RENTALS = 'telecomRentals'
PERSONAL_RESERVES = 'personalReserves'
LAST_ARTY_CTRL_MODE = 'lastArtyCtrlMode'
ACTIVE_TEST_PARTICIPATION_CONFIRMED = 'activeTestParticipateConfirmed'
MAPBOX_PROGRESSION = 'mapbox_progression'
UNLOCK_VEHICLES_IN_BATTLE_HINTS = 'unlockVehiclesInBattleHints'
BECOME_ELITE_VEHICLES_WATCHED = 'becomeEliteWatched'
VPP_ENTRY_POINT_LAST_SEEN_STEP = 'vehiclePostProgressionLastSeenStep'
CLAN_PREBATTLE_SORTING_KEY = 'ClanPrebattleSortingKey'
SHOW_DEMO_ACC_REGISTRATION = 'showDemoAccRegistration'
RESOURCE_WELL_START_SHOWN = 'resourceWellStartShown'
RESOURCE_WELL_END_SHOWN = 'resourceWellEndShown'
RESOURCE_WELL_NOTIFICATIONS = 'resourceWellNotifications'
MAPBOX_SURVEYS = 'mapbox_surveys'
CLAN_NEWS_SEEN = 'clanNewsSeen'
INTEGRATED_AUCTION_NOTIFICATIONS = 'integratedAuctionNotifications'
SHOWN_WOT_PLUS_INTRO = 'shownWotPlusIntro'
MINIMAP_SIZE = 'minimapSize'
COMP7_UI_SECTION = 'comp7'
COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT = 'comp7WeeklyQuestsPageTokensCount'
COMP7_SHOP_SEEN_PRODUCTS = 'comp7ShopSeenProducts'
FUN_RANDOM_NOTIFICATIONS = 'funRandomNotifications'
FUN_RANDOM_NOTIFICATIONS_FROZEN = 'funRandomNotificationsFrozen'
FUN_RANDOM_NOTIFICATIONS_PROGRESSIONS = 'funRandomNotificationsProgressions'
FUN_RANDOM_NOTIFICATIONS_SUB_MODES = 'funRandomNotificationsSubModes'
LOOT_BOXES = 'lootBoxes'
EVENT_LOOT_BOXES = 'eventLootBoxes'
LOOT_BOXES_WAS_STARTED = 'lootBoxesWasStarted'
LOOT_BOXES_WAS_FINISHED = 'lootBoxesWasFinished'
LOOT_BOXES_OPEN_ANIMATION_ENABLED = 'lootBoxesOpenAnimationEnabled'
LOOT_BOXES_VIEWED_COUNT = 'lootBoxesViewedCount'
LOOT_BOXES_EVENT_UNIQUE_ID = 'lootBoxesEventUniqueID'
COLLECTIONS_SECTION = 'collections'
COLLECTIONS_INTRO_SHOWN = 'collectionsIntroShown'
COLLECTION_SHOWN_NEW_REWARDS = 'collectionsNewRewards'
COLLECTION_SHOWN_NEW_ITEMS = 'collectionNewItems'
COLLECTION_SHOWN_NEW_ITEMS_COUNT = 'collectionNewItemsCount'
COLLECTION_TUTORIAL_COMPLETED = 'collectionTutorialCompleted'
COLLECTION_WAS_ENABLED = 'collectionsWasEnabled'
COLLECTIONS_TAB_SHOWN_IDS = 'collectionsTabShownIds'
COLLECTIONS_TAB_SHOWN_NEW_ITEMS = 'collectionsTabShownNewItems'
SHOWN_COMPLETED_COLLECTIONS = 'shownCompletedCollections'
LAST_SHOWN_NEW_COLLECTION = 'lastShownNewColLection'
LAST_SHOWN_COLLECTION_BALANCE = 'lastShownCollectionBalance'
COLLECTIONS_NOTIFICATIONS = 'collectionsNotifications'
ACHIEVEMENTS_INFO = 'achievements20_info'
ACHIEVEMENTS_INITIAL_BATTLE_COUNT = 'achievements20InitialBattleCount'
ACHIEVEMENTS_MAX_WTR_POINTS = 'achievements20MaxWtrPoints'
ACHIEVEMENTS_WTR_RANKS = 'achievementsWtrRanks'
ACHIEVEMENTS_WTR_PREV_POINTS_NOTIFICATION = 'achievementWtrPointsNotification'
ACHIEVEMENTS_WTR_INFO = 'achievementWtr'
ACHIEVEMENTS_WTR_PREV_POINTS = 'achievementWtrPoints'
ACHIEVEMENTS_WTR_PREV_RANK = 'achievementWtrPrevRank'
ACHIEVEMENTS_WTR_PREV_SUB_RANK = 'achievementWtrPrevSubRank'
PREV_ACHIEVEMENTS_NAME_LIST = 'prevAchievementNameList'
ACHIEVEMENTS_VISITED = 'achievementsVisited'
ACHIEVEMENTS_FIRST_ENTRY_STATUS = 'achievementsFirstEntryStatus'
ACHIEVEMENTS_RATING_CALCULATED_STATUS = 'achievementsRatingCalculatedStatus'
ACHIEVEMENTS_EDITING_ENABLED_STATUS = 'achievementsEditingEnabledStatus'
ACHIEVEMENTS_MEDAL_ADDED_STATUS = 'achievementsMedalAddedStatus'
ACHIEVEMENTS_RATING_CHANGED_STATUS = 'achievementsRatingChangedStatus'
ACHIEVEMENTS_MEDAL_COUNT_INFO = 'achievementsMedalCountInfo'
VIEWED_MODULES_SECTION = 'mua'
LIMITED_UI_VERSIONED_RULES = 'luiVersioned'

class BattleMatters(object):
    BATTLE_MATTERS_SETTINGS = 'battleMattersSettings'
    BATTLES_COUNT_WITHOUT_PROGRESS = 'battlesCountWithoutProgress'
    QUEST_IDX_FOR_LAST_UPDATED_PROGRESS = 'progressForQuest'
    LAST_QUEST_PROGRESS = 'lastQuestProgress'
    REMINDER_LAST_DISPLAY_TIME = 'reminderLastDisplayTime'


class Winback(object):
    WINBACK_SETTINGS = 'winbackSettings'
    COMPLETED_STARTING_QUEST_COUNT = 'completedStartingQuestCount'
    INTRO_SHOWN = 'introShown'
    BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN = 'battleSelectorSettingsBulletShown'


KNOWN_SELECTOR_BATTLES = 'knownSelectorBattles'
MODE_SELECTOR_BATTLE_PASS_SHOWN = 'modeSelectorBattlePassShown'
RANKED_LAST_CYCLE_ID = 'rankedLastCycleID'
EPIC_LAST_CYCLE_ID = 'epicLastCycleID'
FUN_RANDOM_LAST_PRESET = 'funRandomLastPreset'
DEFAULT_VALUES = {KEY_FILTERS: {STORE_TAB: 0,
               'shop_current': (-1, STORE_CONSTANTS.VEHICLE, False),
               'scroll_to_item': None,
               'shop_restoreVehicle': {'obtainingType': STORE_CONSTANTS.RESTORE_VEHICLE,
                                       'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                       'selectedLevels': DEFAULT_LEVELS_FILTERS},
               'shop_tradeInVehicle': {'obtainingType': STORE_CONSTANTS.TRADE_IN_VEHICLE,
                                       'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                       'selectedLevels': DEFAULT_LEVELS_FILTERS},
               'shop_module': {'fitsType': STORE_CONSTANTS.MY_VEHICLES_ARTEFACT_FIT,
                               'vehicleCD': -1,
                               'extra': [STORE_CONSTANTS.LOCKED_EXTRA_NAME, STORE_CONSTANTS.IN_HANGAR_EXTRA_NAME],
                               'itemTypes': [STORE_CONSTANTS.GUN_MODULE_NAME,
                                             STORE_CONSTANTS.TURRET_MODULE_NAME,
                                             STORE_CONSTANTS.ENGINE_MODULE_NAME,
                                             STORE_CONSTANTS.CHASSIS_MODULE_NAME,
                                             STORE_CONSTANTS.RADIO_MODULE_NAME]},
               'shop_shell': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_SHELL_FIT,
                              'vehicleCD': -1,
                              'itemTypes': [STORE_CONSTANTS.ARMOR_PIERCING_SHELL,
                                            STORE_CONSTANTS.ARMOR_PIERCING_CR_SHELL,
                                            STORE_CONSTANTS.HOLLOW_CHARGE_SHELL,
                                            STORE_CONSTANTS.HIGH_EXPLOSIVE_SHELL]},
               'shop_battleBooster': {'targetType': STORE_CONSTANTS.ALL_KIND_FIT},
               'inventory_current': (-1, STORE_CONSTANTS.VEHICLE, False),
               'inventory_vehicle': {'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                     'selectedLevels': DEFAULT_LEVELS_FILTERS,
                                     'extra': [STORE_CONSTANTS.BROCKEN_EXTRA_NAME, STORE_CONSTANTS.LOCKED_EXTRA_NAME]},
               'inventory_module': {'fitsType': STORE_CONSTANTS.MY_VEHICLES_ARTEFACT_FIT,
                                    'vehicleCD': -1,
                                    'extra': [],
                                    'itemTypes': [STORE_CONSTANTS.GUN_MODULE_NAME,
                                                  STORE_CONSTANTS.TURRET_MODULE_NAME,
                                                  STORE_CONSTANTS.ENGINE_MODULE_NAME,
                                                  STORE_CONSTANTS.CHASSIS_MODULE_NAME,
                                                  STORE_CONSTANTS.RADIO_MODULE_NAME]},
               'inventory_shell': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_SHELL_FIT,
                                   'vehicleCD': -1,
                                   'itemTypes': [STORE_CONSTANTS.ARMOR_PIERCING_SHELL,
                                                 STORE_CONSTANTS.ARMOR_PIERCING_CR_SHELL,
                                                 STORE_CONSTANTS.HOLLOW_CHARGE_SHELL,
                                                 STORE_CONSTANTS.HIGH_EXPLOSIVE_SHELL]},
               'inventory_optionalDevice': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                            'vehicleCD': -1,
                                            'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'inventory_equipment': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                       'vehicleCD': -1,
                                       'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'inventory_battleBooster': {'targetType': STORE_CONSTANTS.ALL_KIND_FIT},
               'inventory_crewBooks': {'targetType': STORE_CONSTANTS.ALL_KIND_FIT},
               MISSIONS_PAGE: {'hideDone': False,
                               'hideUnavailable': False},
               CAROUSEL_FILTER_1: {'ussr': False,
                                   'germany': False,
                                   'usa': False,
                                   'china': False,
                                   'france': False,
                                   'uk': False,
                                   'japan': False,
                                   'czech': False,
                                   'sweden': False,
                                   'poland': False,
                                   'italy': False,
                                   'lightTank': False,
                                   'mediumTank': False,
                                   'heavyTank': False,
                                   'SPG': False,
                                   'AT-SPG': False,
                                   'level_1': False,
                                   'level_2': False,
                                   'level_3': False,
                                   'level_4': False,
                                   'level_5': False,
                                   'level_6': False,
                                   'level_7': False,
                                   'level_8': False,
                                   'level_9': False,
                                   'level_10': False},
               CAROUSEL_FILTER_2: {'premium': False,
                                   'elite': False,
                                   'igr': False,
                                   'rented': True,
                                   'event': True,
                                   'favorite': False,
                                   'bonus': False,
                                   'crystals': False,
                                   'role_HT_assault': False,
                                   'role_HT_break': False,
                                   'role_HT_support': False,
                                   'role_HT_universal': False,
                                   'role_MT_universal': False,
                                   'role_MT_sniper': False,
                                   'role_MT_assault': False,
                                   'role_MT_support': False,
                                   'role_ATSPG_assault': False,
                                   'role_ATSPG_universal': False,
                                   'role_ATSPG_sniper': False,
                                   'role_ATSPG_support': False,
                                   'role_LT_universal': False,
                                   'role_LT_wheeled': False,
                                   'role_SPG': False},
               CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                          'clanRented': False},
               BATTLEPASS_CAROUSEL_FILTER_CLIENT_1: {'battlePassSeason': 0},
               RANKED_CAROUSEL_FILTER_1: {'ussr': False,
                                          'germany': False,
                                          'usa': False,
                                          'china': False,
                                          'france': False,
                                          'uk': False,
                                          'japan': False,
                                          'czech': False,
                                          'sweden': False,
                                          'poland': False,
                                          'italy': False,
                                          'lightTank': False,
                                          'mediumTank': False,
                                          'heavyTank': False,
                                          'SPG': False,
                                          'AT-SPG': False,
                                          'level_1': False,
                                          'level_2': False,
                                          'level_3': False,
                                          'level_4': False,
                                          'level_5': False,
                                          'level_6': False,
                                          'level_7': False,
                                          'level_8': False,
                                          'level_9': False,
                                          'level_10': False},
               RANKED_CAROUSEL_FILTER_2: {'premium': False,
                                          'elite': False,
                                          'igr': False,
                                          'rented': True,
                                          'event': True,
                                          'gameMode': False,
                                          'favorite': False,
                                          'bonus': False,
                                          'crystals': False,
                                          'ranked': True,
                                          'role_HT_assault': False,
                                          'role_HT_break': False,
                                          'role_HT_universal': False,
                                          'role_HT_support': False,
                                          'role_MT_assault': False,
                                          'role_MT_universal': False,
                                          'role_MT_sniper': False,
                                          'role_MT_support': False,
                                          'role_ATSPG_assault': False,
                                          'role_ATSPG_universal': False,
                                          'role_ATSPG_sniper': False,
                                          'role_ATSPG_support': False,
                                          'role_LT_universal': False,
                                          'role_LT_wheeled': False,
                                          'role_SPG': False},
               RANKED_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                                 'clanRented': False},
               ROYALE_CAROUSEL_FILTER_1: {'ussr': False,
                                          'germany': False,
                                          'usa': False,
                                          'china': False,
                                          'france': False,
                                          'uk': False,
                                          'japan': False,
                                          'czech': False,
                                          'sweden': False,
                                          'poland': False,
                                          'italy': False,
                                          'lightTank': True,
                                          'mediumTank': True,
                                          'heavyTank': True,
                                          'SPG': False,
                                          'AT-SPG': False,
                                          'level_1': False,
                                          'level_2': False,
                                          'level_3': False,
                                          'level_4': False,
                                          'level_5': False,
                                          'level_6': False,
                                          'level_7': False,
                                          'level_8': False,
                                          'level_9': False,
                                          'level_10': False},
               ROYALE_CAROUSEL_FILTER_2: {'premium': False,
                                          'elite': False,
                                          'igr': False,
                                          'rented': True,
                                          'event': True,
                                          'gameMode': False,
                                          'favorite': False,
                                          'bonus': False,
                                          'crystals': False,
                                          'battleRoyale': True},
               ROYALE_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                                 'clanRented': False},
               EPICBATTLE_CAROUSEL_FILTER_1: {'ussr': False,
                                              'germany': False,
                                              'usa': False,
                                              'china': False,
                                              'france': False,
                                              'uk': False,
                                              'japan': False,
                                              'czech': False,
                                              'sweden': False,
                                              'poland': False,
                                              'italy': False,
                                              'lightTank': False,
                                              'mediumTank': False,
                                              'heavyTank': False,
                                              'SPG': False,
                                              'AT-SPG': False,
                                              'level_1': False,
                                              'level_2': False,
                                              'level_3': False,
                                              'level_4': False,
                                              'level_5': False,
                                              'level_6': False,
                                              'level_7': False,
                                              'level_8': True,
                                              'level_9': True,
                                              'level_10': False},
               EPICBATTLE_CAROUSEL_FILTER_2: {'premium': False,
                                              'elite': False,
                                              'igr': False,
                                              'rented': True,
                                              'event': True,
                                              'gameMode': False,
                                              'favorite': False,
                                              'bonus': False,
                                              'crystals': False,
                                              'role_HT_assault': False,
                                              'role_HT_break': False,
                                              'role_HT_support': False,
                                              'role_HT_universal': False,
                                              'role_MT_universal': False,
                                              'role_MT_sniper': False,
                                              'role_MT_assault': False,
                                              'role_MT_support': False,
                                              'role_ATSPG_assault': False,
                                              'role_ATSPG_universal': False,
                                              'role_ATSPG_sniper': False,
                                              'role_ATSPG_support': False,
                                              'role_LT_universal': False,
                                              'role_LT_wheeled': False,
                                              'role_SPG': False},
               EPICBATTLE_CAROUSEL_FILTER_CLIENT_1: {'epicBattleSeason': 0,
                                                     'level_8': True,
                                                     'level_9': True,
                                                     'searchNameVehicle': '',
                                                     'clanRented': False},
               EPICBATTLE_CAROUSEL_FILTER_CLIENT_2: {'epicBattleSeason': 0,
                                                     'level_8': True,
                                                     'level_9': False,
                                                     'searchNameVehicle': '',
                                                     'clanRented': False},
               BATTLEPASS_CAROUSEL_FILTER_1: {'isCommonProgression': False},
               MAPBOX_CAROUSEL_FILTER_1: {'ussr': False,
                                          'germany': False,
                                          'usa': False,
                                          'china': False,
                                          'france': False,
                                          'uk': False,
                                          'japan': False,
                                          'czech': False,
                                          'sweden': False,
                                          'poland': False,
                                          'italy': False,
                                          'lightTank': False,
                                          'mediumTank': False,
                                          'heavyTank': False,
                                          'SPG': False,
                                          'AT-SPG': False,
                                          'level_1': False,
                                          'level_2': False,
                                          'level_3': False,
                                          'level_4': False,
                                          'level_5': False,
                                          'level_6': False,
                                          'level_7': False,
                                          'level_8': True,
                                          'level_9': True,
                                          'level_10': True},
               MAPBOX_CAROUSEL_FILTER_2: {'premium': False,
                                          'elite': False,
                                          'igr': False,
                                          'rented': True,
                                          'event': True,
                                          'gameMode': False,
                                          'favorite': False,
                                          'bonus': False,
                                          'crystals': False,
                                          'role_HT_assault': False,
                                          'role_HT_break': False,
                                          'role_HT_support': False,
                                          'role_HT_universal': False,
                                          'role_MT_universal': False,
                                          'role_MT_sniper': False,
                                          'role_MT_assault': False,
                                          'role_MT_support': False,
                                          'role_ATSPG_assault': False,
                                          'role_ATSPG_universal': False,
                                          'role_ATSPG_sniper': False,
                                          'role_ATSPG_support': False,
                                          'role_LT_universal': False,
                                          'role_LT_wheeled': False,
                                          'role_SPG': False},
               MAPBOX_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                                 'clanRented': False},
               FUN_RANDOM_CAROUSEL_FILTER_1: {'ussr': False,
                                              'germany': False,
                                              'usa': False,
                                              'china': False,
                                              'france': False,
                                              'uk': False,
                                              'japan': False,
                                              'czech': False,
                                              'sweden': False,
                                              'poland': False,
                                              'italy': False,
                                              'lightTank': False,
                                              'mediumTank': False,
                                              'heavyTank': False,
                                              'SPG': False,
                                              'AT-SPG': False,
                                              'level_1': False,
                                              'level_2': False,
                                              'level_3': False,
                                              'level_4': False,
                                              'level_5': False,
                                              'level_6': False,
                                              'level_7': False,
                                              'level_8': False,
                                              'level_9': False,
                                              'level_10': False},
               FUN_RANDOM_CAROUSEL_FILTER_2: {'premium': False,
                                              'elite': False,
                                              'igr': False,
                                              'rented': True,
                                              'event': False,
                                              'gameMode': False,
                                              'favorite': False,
                                              'bonus': False,
                                              'crystals': False,
                                              'funRandom': True,
                                              'role_HT_assault': False,
                                              'role_HT_break': False,
                                              'role_HT_support': False,
                                              'role_HT_universal': False,
                                              'role_MT_universal': False,
                                              'role_MT_sniper': False,
                                              'role_MT_assault': False,
                                              'role_MT_support': False,
                                              'role_ATSPG_assault': False,
                                              'role_ATSPG_universal': False,
                                              'role_ATSPG_sniper': False,
                                              'role_ATSPG_support': False,
                                              'role_LT_universal': False,
                                              'role_LT_wheeled': False,
                                              'role_SPG': False},
               FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                                     'clanRented': False},
               COMP7_CAROUSEL_FILTER_1: {'ussr': False,
                                         'germany': False,
                                         'usa': False,
                                         'china': False,
                                         'france': False,
                                         'uk': False,
                                         'japan': False,
                                         'czech': False,
                                         'sweden': False,
                                         'poland': False,
                                         'italy': False,
                                         'lightTank': False,
                                         'mediumTank': False,
                                         'heavyTank': False,
                                         'SPG': False,
                                         'AT-SPG': False,
                                         'level_1': False,
                                         'level_2': False,
                                         'level_3': False,
                                         'level_4': False,
                                         'level_5': False,
                                         'level_6': False,
                                         'level_7': False,
                                         'level_8': False,
                                         'level_9': False,
                                         'level_10': False},
               COMP7_CAROUSEL_FILTER_2: {'premium': False,
                                         'elite': False,
                                         'igr': False,
                                         'rented': True,
                                         'event': True,
                                         'gameMode': False,
                                         'favorite': False,
                                         'bonus': False,
                                         'crystals': False,
                                         'comp7': True,
                                         'role_HT_assault': False,
                                         'role_HT_break': False,
                                         'role_HT_support': False,
                                         'role_HT_universal': False,
                                         'role_MT_universal': False,
                                         'role_MT_sniper': False,
                                         'role_MT_assault': False,
                                         'role_MT_support': False,
                                         'role_ATSPG_assault': False,
                                         'role_ATSPG_universal': False,
                                         'role_ATSPG_sniper': False,
                                         'role_ATSPG_support': False,
                                         'role_LT_universal': False,
                                         'role_LT_wheeled': False,
                                         'role_SPG': False},
               COMP7_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': '',
                                                'clanRented': False},
               MISSION_SELECTOR_FILTER: {'inventory': False},
               PM_SELECTOR_FILTER: {'inventory': False},
               ORDERS_FILTER: {'isSelected': False},
               GUI_START_BEHAVIOR: {'isFreeXPInfoDialogShowed': False,
                                    'isRankedWelcomeViewShowed': False,
                                    'isRankedWelcomeViewStarted': False,
                                    'isEpicRandomCheckboxClicked': False,
                                    'isDisplayPlatoonMembersClicked': False,
                                    GuiSettingsBehavior.VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW: True,
                                    GuiSettingsBehavior.RESOURCE_WELL_INTRO_SHOWN: False,
                                    GuiSettingsBehavior.IS_PRESTIGE_ONBOARDING_VIEWED: False,
                                    GuiSettingsBehavior.PRESTIGE_FIRST_ENTRY_NOTIFICATION_SHOWN: False,
                                    'birthdayCalendarIntroShowed': False,
                                    GuiSettingsBehavior.COMP7_INTRO_SHOWN: False,
                                    GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN: False,
                                    GuiSettingsBehavior.CLAN_SUPPLY_INTRO_SHOWN: False},
               EULA_VERSION: {'version': 0},
               FORT_MEMBER_TUTORIAL: {'wasShown': False},
               IGR_PROMO: {'wasShown': False},
               CONTACTS: {'showOfflineUsers': True,
                          'showOthersCategory': True},
               GOLD_FISH_LAST_SHOW_TIME: 0,
               BOOSTERS_FILTER: 0,
               'cs_intro_view_vehicle': {'nation': -1,
                                         'vehicleType': 'none',
                                         'isMain': False,
                                         'level': -1,
                                         'compatibleOnly': True},
               'cs_list_view_vehicle': {'nation': -1,
                                        'vehicleType': 'none',
                                        'isMain': False,
                                        'level': -1,
                                        'compatibleOnly': True},
               'cs_unit_view_vehicle': {'nation': -1,
                                        'vehicleType': 'none',
                                        'isMain': False,
                                        'level': -1,
                                        'compatibleOnly': True},
               'cs_unit_view_settings': {'nation': -1,
                                         'vehicleType': 'none',
                                         'isMain': False,
                                         'level': -1,
                                         'compatibleOnly': True},
               'epic_rent_view_vehicle': {'nation': -1,
                                          'vehicleType': 'none',
                                          'isMain': False,
                                          'level': -1,
                                          'compatibleOnly': True},
               PROMO: {},
               PROFILE_TECHNIQUE: {'selectedColumn': 4,
                                   'selectedColumnSorting': 'descending',
                                   'isInHangarSelected': False},
               PROFILE_TECHNIQUE_MEMBER: {'selectedColumn': 4,
                                          'selectedColumnSorting': 'descending'},
               SPEAKERS_DEVICE: 0,
               UNIT_FILTER: {GAME.UNIT_FILTER: 2047}},
 KEY_FAVORITES: {CURRENT_VEHICLE: 0,
                 ROYALE_VEHICLE: 0,
                 FALLOUT_VEHICLES: {}},
 KEY_MANUAL: {LOBBY_MENU_MANUAL_TRIGGER_SHOWN: False,
              MANUAL_NEW_CONTENT: {}},
 KEY_SETTINGS: {'unitWindow': {SELECTED_INTRO_VEHICLES_FIELD: []},
                'vehicleSellDialog': {'isOpened': False},
                KNOWN_SELECTOR_BATTLES: set(),
                'tankmanDropSkillIdx': 0,
                'cursor': False,
                'arcade': {'mixing': {'alpha': 100,
                                      'type': 3},
                           'gunTag': {'alpha': 100,
                                      'type': 9},
                           'centralTag': {'alpha': 100,
                                          'type': 8},
                           'net': {'alpha': 100,
                                   'type': 0},
                           'reloader': {'alpha': 100,
                                        'type': 0},
                           'condition': {'alpha': 100,
                                         'type': 0},
                           'cassette': {'alpha': 100,
                                        'type': 0},
                           'reloaderTimer': {'alpha': 100,
                                             'type': 0},
                           'zoomIndicator': {'alpha': 100,
                                             'type': 0}},
                'sniper': {'mixing': {'alpha': 90,
                                      'type': 0},
                           'gunTag': {'alpha': 90,
                                      'type': 0},
                           'centralTag': {'alpha': 90,
                                          'type': 0},
                           'net': {'alpha': 90,
                                   'type': 0},
                           'reloader': {'alpha': 90,
                                        'type': 0},
                           'condition': {'alpha': 90,
                                         'type': 0},
                           'cassette': {'alpha': 90,
                                        'type': 0},
                           'reloaderTimer': {'alpha': 100,
                                             'type': 0},
                           'zoomIndicator': {'alpha': 100,
                                             'type': 0}},
                'spgAim': {SPGAim.SHOTS_RESULT_INDICATOR: True,
                           SPGAim.SPG_SCALE_WIDGET: True,
                           SPGAim.AUTO_CHANGE_AIM_MODE: True,
                           SPGAim.AIM_ENTRANCE_MODE: 0},
                'contour': {CONTOUR.ENHANCED_CONTOUR: False,
                            CONTOUR.CONTOUR_PENETRABLE_ZONE: 0,
                            CONTOUR.CONTOUR_IMPENETRABLE_ZONE: 0},
                LAST_ARTY_CTRL_MODE: CTRL_MODE_NAME.STRATEGIC,
                'markers': {'ally': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': True,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 2,
                                     'markerBaseVehicleName': True,
                                     'markerBasePlayerName': False,
                                     'markerBaseAimMarker2D': False,
                                     'markerAltIcon': False,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': False,
                                     'markerAltPlayerName': True,
                                     'markerAltAimMarker2D': False},
                            'enemy': {'markerBaseIcon': False,
                                      'markerBaseLevel': False,
                                      'markerBaseHpIndicator': True,
                                      'markerBaseDamage': True,
                                      'markerBaseHp': 2,
                                      'markerBaseVehicleName': True,
                                      'markerBasePlayerName': False,
                                      'markerBaseAimMarker2D': True,
                                      'markerAltIcon': False,
                                      'markerAltLevel': True,
                                      'markerAltHpIndicator': True,
                                      'markerAltDamage': True,
                                      'markerAltHp': 1,
                                      'markerAltVehicleName': False,
                                      'markerAltPlayerName': True,
                                      'markerAltAimMarker2D': True},
                            'dead': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': False,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 3,
                                     'markerBaseVehicleName': True,
                                     'markerBasePlayerName': False,
                                     'markerBaseAimMarker2D': False,
                                     'markerAltIcon': False,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': False,
                                     'markerAltPlayerName': True,
                                     'markerAltAimMarker2D': False}},
                COMP7_PREBATTLE_CAROUSEL_ROW_VALUE: -1,
                GAME.COMP7_MINIMAP_SIZE: -1,
                COMP7_IS_VOIP_IN_BATTLE_ACTIVATED: False,
                COMP7_ENTITLEMENTS: {COMP7_ENTITLEMENTS_TIMESTAMP: 0,
                                     COMP7_ENTITLEMENTS_BALANCE: {}},
                'showVehicleIcon': False,
                'showVehicleLevel': False,
                'showExInf4Destroyed': False,
                'ingameHelpVersion': -1,
                'isColorBlind': False,
                'useServerAim': False,
                'showDamageIcon': True,
                'showVehiclesCounter': True,
                'minimapAlpha': 0,
                GAME.MINIMAP_SIZE: None,
                GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL: 1,
                GAME.SHOW_VEHICLE_HP_IN_MINIMAP: 1,
                'minimapRespawnSize': 0,
                'minimapViewRange': True,
                'minimapMaxViewRange': True,
                'minimapDrawRange': True,
                'minimapAlphaEnabled': False,
                'epicMinimapZoom': 1.5,
                GAME.TRAINING_MINIMAP_SIZE: None,
                'increasedZoom': True,
                'sniperModeByShift': True,
                'nationalVoices': False,
                'enableVoIP': True,
                'replayEnabled': 1,
                'sniperZoom': 0,
                GAME.SWITCH_SETUPS_IN_LOADING: None,
                GAME.HULLLOCK_ENABLED: True,
                GAME.PRE_COMMANDER_CAM: True,
                GAME.COMMANDER_CAM: True,
                GAME.SCROLL_SMOOTHING: True,
                'hangarCamPeriod': 1,
                'hangarCamParallaxEnabled': True,
                'players_panel': {'state': None,
                                  'showLevels': True,
                                  'showTypes': True},
                'epic_random_players_panel': {'state': 5},
                'gameplayMask': gameplay_ctx.getDefaultMask(),
                'statsSorting': {'iconType': 'tank',
                                 'sortDirection': 'descending'},
                'statsSortingSortie': {'iconType': 'tank',
                                       'sortDirection': 'descending'},
                'statsSortingComp7': {'iconType': 'prestigePoints',
                                      'sortDirection': 'descending'},
                'backDraftInvert': False,
                QUESTS: {'lastVisitTime': -1,
                         'visited': [],
                         'naVisited': [],
                         'personalMissions': {'introShown': False,
                                              'operationsVisited': set(),
                                              'headerAlert': False},
                         'dailyQuests': {'lastVisitedDQTabIdx': None,
                                         'seenCompleted': False,
                                         'visitedBonus': False,
                                         'premMissionsTabDiscovered': False},
                         QUEST_DELTAS: {QUEST_DELTAS_COMPLETION: dict(),
                                        QUEST_DELTAS_PROGRESS: dict(),
                                        QUEST_DELTAS_TOKENS_PROGRESS: dict()}},
                'checkBoxConfirmator': {'questsConfirmDialogShow': True,
                                        'questsConfirmDialogShowPM2': True},
                DOG_TAGS: {'lastVisitedDogTagsTabIdx': None,
                           'onboardingEnabled': True,
                           'seenComps': set()},
                WOT_PLUS: {'isFirstTime': True,
                           'isWotPlusEnabled': False,
                           'isGoldReserveEnabled': False,
                           'isPassiveXpEnabled': False,
                           'isFreeDemountingEnabled': False,
                           'isExcludedMapEnabled': False,
                           'isDailyAttendancesEnabled': False,
                           'amountOfDailyAttendance': 0,
                           'isBattleBonusesEnabled': False,
                           'isOnboardingShown': False,
                           'isBadgesEnabled': False,
                           'isAdditionalXPEnabled': False},
                TELECOM_RENTALS: {'isTelecomRentalsEnabled': True,
                                  'isTelecomRentalsBlocked': True},
                PERSONAL_RESERVES: {'isFirstTimeNotificationShown': False,
                                    'isIntroPageShown': False,
                                    'boosterCardHintsSeen': set()},
                CUSTOMIZATION_SECTION: {CAROUSEL_ARROWS_HINT_SHOWN_FIELD: False,
                                        PROJECTION_DECAL_HINT_SHOWN_FIELD: False},
                SESSION_STATS_SECTION: {BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD: False},
                'showVehModelsOnMap': 0,
                'battleLoadingInfo': 1,
                'battleLoadingRankedInfo': 1,
                'relativePower': False,
                'relativeArmor': False,
                'relativeMobility': False,
                'relativeVisibility': False,
                'relativeCamouflage': False,
                'interfaceScale': 0,
                'medKitInstalled': False,
                'repairKitInstalled': False,
                'fireExtinguisherInstalled': False,
                'PveTriggerShown': False,
                'isEpicPerformanceWarningClicked': False,
                LAST_PROMO_PATCH_VERSION: '',
                LAST_CALENDAR_SHOW_TIMESTAMP: '',
                LAST_RESTORE_NOTIFICATION: None,
                'dynamicRange': 0,
                'soundDevice': 0,
                'bassBoost': False,
                'lowQualitySound': WWISE.WG_isMSR(),
                'nightMode': False,
                SOUND.DETECTION_ALERT_SOUND: 'lightbulb',
                SOUND.ARTY_SHOT_ALERT_SOUND: 'artillery_lightbulb',
                PREVIEW_INFO_PANEL_IDX: 0,
                'carouselType': 0,
                'doubleCarouselType': 0,
                'contentType': 0,
                'vehicleCarouselStats': True,
                WHEELED_DEATH_DELAY_COUNT: 10,
                FREE_CAM_USES_COUNT: 0,
                NEW_SETTINGS_COUNTER: {'GameSettings': {'gameplay_epicStandard': True,
                                                        BattleCommStorageKeys.SHOW_LOCATION_MARKERS: True,
                                                        GAME.DISPLAY_PLATOON_MEMBERS: True,
                                                        'hangarCamParallaxEnabled': True,
                                                        'hangarCamPeriod': True,
                                                        GAME.HULLLOCK_ENABLED: True,
                                                        GAME.SHOW_VEHICLE_HP_IN_MINIMAP: True,
                                                        GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL: True,
                                                        GAME.PRE_COMMANDER_CAM: True,
                                                        GAME.COMMANDER_CAM: True,
                                                        GAME.SHOW_DAMAGE_ICON: True,
                                                        ANONYMIZER: True,
                                                        GAME.SHOW_VICTIMS_DOGTAG: True,
                                                        GAME.GAMEPLAY_ONLY_10_MODE: True,
                                                        GAME.SHOW_ARTY_HIT_ON_MAP: True,
                                                        GAME.SWITCH_SETUPS_IN_LOADING: True,
                                                        GAME.SCROLL_SMOOTHING: True,
                                                        GAME.LIMITED_UI_ACTIVE: True,
                                                        GAME.GAMEPLAY_DEV_MAPS: True,
                                                        GAME.POSTMORTEM_MODE: True},
                                       'GraphicSettings': {'ScreenSettings': {'gammaSetting': True,
                                                                              'colorFilter': True},
                                                           'AdvancedGraphicSettings': {'HAVOK_ENABLED': True,
                                                                                       'TERRAIN_TESSELLATION_ENABLED': True,
                                                                                       'SNIPER_MODE_TERRAIN_TESSELLATION_ENABLED': True,
                                                                                       'TRACK_PHYSICS_QUALITY': True}},
                                       'FeedbackSettings': {'feedbackBattleBorderMap': {'battleBorderMapType': True,
                                                                                        'battleBorderMapMode': True},
                                                            'feedbackQuestsProgress': {ScorePanelStorageKeys.SHOW_HP_VALUES: True,
                                                                                       ScorePanelStorageKeys.SHOW_HP_DIFFERENCE: True,
                                                                                       ScorePanelStorageKeys.ENABLE_TIER_GROUPING: True,
                                                                                       ScorePanelStorageKeys.SHOW_HP_BAR: True,
                                                                                       'progressViewType': True,
                                                                                       'progressViewConditions': True},
                                                            'feedbackDamageIndicator': {'damageIndicatorAllies': True},
                                                            'feedbackBattleEvents': {BATTLE_EVENTS.CREW_PERKS: True}},
                                       'ControlsSettings': {'highlightLocation': True,
                                                            'showQuestProgress': True,
                                                            'chargeFire': True,
                                                            'affirmative': True,
                                                            'negative': True,
                                                            'showPersonalReserves': True},
                                       'AimSettings': {AIM.SPG: {SPGAim.AUTO_CHANGE_AIM_MODE: True,
                                                                 SPGAim.SPG_SCALE_WIDGET: True,
                                                                 SPGAim.SPG_STRATEGIC_CAM_MODE: True,
                                                                 SPGAim.SHOTS_RESULT_INDICATOR: True,
                                                                 SPGAim.AIM_ENTRANCE_MODE: True},
                                                       AIM.CONTOUR: {CONTOUR.ENHANCED_CONTOUR: True,
                                                                     CONTOUR.CONTOUR_PENETRABLE_ZONE: True,
                                                                     CONTOUR.CONTOUR_IMPENETRABLE_ZONE: True}},
                                       'SoundSettings': {'artyBulbVoices': True}},
                CLAN_PREBATTLE_SORTING_KEY: 0,
                SHOW_OPT_DEVICE_HINT: True,
                SHOW_OPT_DEVICE_HINT_TROPHY: True,
                SHOW_OPT_MODERNIZED_DEVICE_HINT: True,
                LAST_BADGES_VISIT: 0,
                LAST_SELECTED_SUFFIX_BADGE_ID: 0,
                ENABLE_RANKED_ANIMATIONS: True,
                COLOR_SETTINGS_TAB_IDX: 0,
                COLOR_SETTINGS_SHOWS_COUNT: 0,
                SELECTED_QUEST_IN_REPLAY: None,
                APPLIED_COLOR_SETTINGS: {},
                LAST_SELECTED_PM_BRANCH: 0,
                CRYSTALS_INFO_SHOWN: False,
                TRAJECTORY_VIEW_HINT_SECTION: {HINTS_LEFT: 3,
                                               LAST_DISPLAY_DAY: 0,
                                               NUM_BATTLES: 0},
                DYN_SQUAD_HINT_SECTION: {HINTS_LEFT: 3,
                                         LAST_DISPLAY_DAY: 0,
                                         NUM_BATTLES: 0},
                PRE_BATTLE_HINT_SECTION: {QUEST_PROGRESS_HINT_SECTION: {HINTS_LEFT: 3,
                                                                        LAST_DISPLAY_DAY: 0,
                                                                        NUM_BATTLES: 0},
                                          HELP_SCREEN_HINT_SECTION: {},
                                          IBC_HINT_SECTION: {HINTS_LEFT: 10},
                                          RESERVES_HINT_SECTION: {HINTS_LEFT: 10}},
                PRE_BATTLE_ROLE_HINT_SECTION: {},
                FUN_RANDOM_HINT_SECTION: {},
                MAPBOX_HINT_SECTION: {},
                DEV_MAPS_HINT_SECTION: {},
                COMMANDER_CAM_HINT_SECTION: {HINTS_LEFT: 5},
                MINIMAP_IBC_HINT_SECTION: {HINTS_LEFT: 10},
                WATCHED_PRE_BATTLE_TIPS_SECTION: {},
                SIEGE_HINT_SECTION: {HINTS_LEFT: 3,
                                     LAST_DISPLAY_DAY: 0,
                                     NUM_BATTLES: 0},
                WHEELED_MODE_HINT_SECTION: {HINTS_LEFT: 3,
                                            LAST_DISPLAY_DAY: 0,
                                            NUM_BATTLES: 0},
                TURBO_SHAFT_ENGINE_MODE_HINT_SECTION: {HINTS_LEFT: 3,
                                                       LAST_DISPLAY_DAY: 0,
                                                       NUM_BATTLES: 0},
                ROCKET_ACCELERATION_MODE_HINT_SECTION: {HINTS_LEFT: 3,
                                                        LAST_DISPLAY_DAY: 0,
                                                        NUM_BATTLES: 0},
                RADAR_HINT_SECTION: {HINTS_LEFT: 3,
                                     LAST_DISPLAY_DAY: 0,
                                     NUM_BATTLES: 0},
                CREW_SKINS_VIEWED: {},
                CREW_BOOKS_VIEWED: {CREW_BOOK_RARITY.CREW_COMMON: {},
                                    CREW_BOOK_RARITY.CREW_EPIC: {},
                                    CREW_BOOK_RARITY.CREW_RARE: {},
                                    CREW_BOOK_RARITY.PERSONAL: 0,
                                    CREW_BOOK_RARITY.UNIVERSAL: 0},
                CREW_SKINS_HISTORICAL_VISIBLE: (True, True),
                VEHICLES_WITH_BLUEPRINT_CONFIRM: {},
                IS_FIRST_ENTRY_BY_DIVISION_ID: {},
                STYLE_PREVIEW_VEHICLES_POOL: [],
                RANKED_STYLED_VEHICLES_POOL: [],
                RANKED_WEB_INFO: None,
                RANKED_WEB_INFO_UPDATE: None,
                RANKED_AWARDS_BUBBLE_YEAR_REACHED: False,
                RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED: False,
                NATION_CHANGE_VIEWED: False,
                LAST_BATTLE_PASS_POINTS_SEEN: {},
                IS_BATTLE_PASS_EXTRA_STARTED: False,
                IS_BATTLE_PASS_COLLECTION_SEEN: False,
                MODULES_ANIMATION_SHOWN: False,
                SUBTITLES: True,
                RANKED_YEAR_POSITION: None,
                TOP_OF_TREE_CONFIG: {},
                BECOME_ELITE_VEHICLES_WATCHED: set(),
                GAME.GAMEPLAY_ONLY_10_MODE: False,
                GAME.GAMEPLAY_DEV_MAPS: True,
                MAPBOX_PROGRESSION: {'previous_battles_played': 0,
                                     'visited_maps': [],
                                     'stored_rewards': {},
                                     'lastCycleId': None},
                MAPBOX_SURVEYS: {},
                UNLOCK_VEHICLES_IN_BATTLE_HINTS: 5,
                MODE_SELECTOR_BATTLE_PASS_SHOWN: {},
                RANKED_LAST_CYCLE_ID: None,
                EPIC_LAST_CYCLE_ID: None,
                FUN_RANDOM_LAST_PRESET: 'undefined',
                SHOW_DEMO_ACC_REGISTRATION: False,
                IS_CUSTOMIZATION_INTRO_VIEWED: False,
                CUSTOMIZATION_STYLE_ITEMS_VISITED: set(),
                SHOWN_WOT_PLUS_INTRO: False,
                OPT_DEVICE_TAB_VISITED: {},
                BattleMatters.BATTLE_MATTERS_SETTINGS: {BattleMatters.BATTLES_COUNT_WITHOUT_PROGRESS: 0,
                                                        BattleMatters.QUEST_IDX_FOR_LAST_UPDATED_PROGRESS: 0,
                                                        BattleMatters.LAST_QUEST_PROGRESS: 0,
                                                        BattleMatters.REMINDER_LAST_DISPLAY_TIME: 0},
                BR_PROGRESSION_POINTS_SEEN: 0,
                ROYALE_INTRO_VIDEO_SHOWN: False,
                ROYALE_SQUAD_TIP_SHOWN_FOR_SEASON: 0,
                LOOT_BOXES: {EVENT_LOOT_BOXES: {LOOT_BOXES_WAS_STARTED: False,
                                                LOOT_BOXES_WAS_FINISHED: False,
                                                LOOT_BOXES_OPEN_ANIMATION_ENABLED: True,
                                                LOOT_BOXES_VIEWED_COUNT: 0,
                                                LOOT_BOXES_EVENT_UNIQUE_ID: 0}},
                Winback.WINBACK_SETTINGS: {Winback.COMPLETED_STARTING_QUEST_COUNT: 0,
                                           Winback.INTRO_SHOWN: False,
                                           Winback.BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN: False},
                ACHIEVEMENTS_INFO: {ACHIEVEMENTS_WTR_RANKS: {},
                                    ACHIEVEMENTS_INITIAL_BATTLE_COUNT: -1,
                                    ACHIEVEMENTS_MAX_WTR_POINTS: 0,
                                    ACHIEVEMENTS_FIRST_ENTRY_STATUS: 0,
                                    ACHIEVEMENTS_RATING_CALCULATED_STATUS: 0,
                                    ACHIEVEMENTS_EDITING_ENABLED_STATUS: 0,
                                    ACHIEVEMENTS_MEDAL_ADDED_STATUS: 0,
                                    ACHIEVEMENTS_RATING_CHANGED_STATUS: 0,
                                    ACHIEVEMENTS_MEDAL_COUNT_INFO: 0,
                                    ACHIEVEMENTS_WTR_PREV_POINTS_NOTIFICATION: 0,
                                    ACHIEVEMENTS_WTR_INFO: {ACHIEVEMENTS_WTR_PREV_POINTS: 0,
                                                            ACHIEVEMENTS_WTR_PREV_RANK: 0,
                                                            ACHIEVEMENTS_WTR_PREV_SUB_RANK: 0},
                                    PREV_ACHIEVEMENTS_NAME_LIST: []}},
 KEY_COUNTERS: {NEW_HOF_COUNTER: {PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON: True},
                NEW_LOBBY_TAB_COUNTER: {},
                REFERRAL_COUNTER: 1,
                CLAN_NOTIFICATION_COUNTERS: {},
                RANKED_AWARDS_COUNTER: 1,
                RANKED_INFO_COUNTER: 1,
                RANKED_YEAR_RATING_COUNTER: 1,
                RANKED_SHOP_COUNTER: 1,
                RANKED_ENTITLEMENT_EVENTS_AMOUNT: 0,
                BOOSTERS_FOR_CREDITS_SLOT_COUNTER: 1,
                SENIORITY_AWARDS_COUNTER: 1,
                DEMOUNT_KIT_SEEN: False,
                RECERTIFICATION_FORM_SEEN: False,
                NEW_SHOP_TABS: {IS_COLLECTIBLE_VEHICLES_VISITED: False},
                VPP_ENTRY_POINT_LAST_SEEN_STEP: {}},
 KEY_NOTIFICATIONS: {ELEN_NOTIFICATIONS: {MISSIONS_CONSTANTS.ELEN_EVENT_STARTED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_FINISHED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_TAB_VISITED: set()},
                     RECRUIT_NOTIFICATIONS: set(),
                     PROGRESSIVE_REWARD_VISITED: False,
                     VIEWED_OFFERS: set(),
                     OFFERS_DISABLED_MSG_SEEN: False,
                     BLUEPRINTS_CONVERT_SALE_STARTED_SEEN: False,
                     CLAN_NEWS_SEEN: False,
                     SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP: None,
                     ACHIEVEMENTS_VISITED: False,
                     INTEGRATED_AUCTION_NOTIFICATIONS: {AUCTION_STAGE_START_SEEN: set(),
                                                        AUCTION_FINISH_STAGE_SEEN: set()},
                     FUN_RANDOM_NOTIFICATIONS: {FUN_RANDOM_NOTIFICATIONS_FROZEN: set(),
                                                FUN_RANDOM_NOTIFICATIONS_PROGRESSIONS: set(),
                                                FUN_RANDOM_NOTIFICATIONS_SUB_MODES: set()},
                     RESOURCE_WELL_NOTIFICATIONS: {RESOURCE_WELL_START_SHOWN: set(),
                                                   RESOURCE_WELL_END_SHOWN: set()},
                     COLLECTIONS_NOTIFICATIONS: {COLLECTION_START_SEEN: [],
                                                 COLLECTION_RENEW_SEEN: {},
                                                 COLLECTIONS_UPDATED_ENTRY_SEEN: False}},
 KEY_SESSION_SETTINGS: {STORAGE_VEHICLES_CAROUSEL_FILTER_1: {'ussr': False,
                                                             'germany': False,
                                                             'usa': False,
                                                             'china': False,
                                                             'france': False,
                                                             'uk': False,
                                                             'japan': False,
                                                             'czech': False,
                                                             'sweden': False,
                                                             'poland': False,
                                                             'italy': False,
                                                             'lightTank': False,
                                                             'mediumTank': False,
                                                             'heavyTank': False,
                                                             'SPG': False,
                                                             'AT-SPG': False,
                                                             'level_1': False,
                                                             'level_2': False,
                                                             'level_3': False,
                                                             'level_4': False,
                                                             'level_5': False,
                                                             'level_6': False,
                                                             'level_7': False,
                                                             'level_8': False,
                                                             'level_9': False,
                                                             'level_10': False,
                                                             'premium': False,
                                                             'elite': False,
                                                             'igr': False,
                                                             'rented': True,
                                                             'event': True,
                                                             'gameMode': False,
                                                             'favorite': False,
                                                             'bonus': False,
                                                             'battleRoyale': False,
                                                             'clanRented': False,
                                                             'searchNameVehicle': ''},
                        'storage_shells': {'filterMask': 0,
                                           'vehicleCD': None},
                        'storage_crew_books': {'filterMask': 0,
                                               'nationID': nations.NONE_INDEX},
                        'storage_consumables_tab': {'filterMask': 0},
                        'storage_modules': {'filterMask': 0,
                                            'vehicleCD': None},
                        'storage_reserves': {'filterMask': 0},
                        'storage_customization': {'filterMask': 0},
                        'storage_opt_devices': {'filterMask': 0,
                                                'vehicleCD': None},
                        STORAGE_BLUEPRINTS_CAROUSEL_FILTER: {'ussr': False,
                                                             'germany': False,
                                                             'usa': False,
                                                             'china': False,
                                                             'france': False,
                                                             'uk': False,
                                                             'japan': False,
                                                             'czech': False,
                                                             'sweden': False,
                                                             'poland': False,
                                                             'italy': False,
                                                             'lightTank': False,
                                                             'mediumTank': False,
                                                             'heavyTank': False,
                                                             'SPG': False,
                                                             'AT-SPG': False,
                                                             'level_1': False,
                                                             'level_2': False,
                                                             'level_3': False,
                                                             'level_4': False,
                                                             'level_5': False,
                                                             'level_6': False,
                                                             'level_7': False,
                                                             'level_8': False,
                                                             'level_9': False,
                                                             'level_10': False,
                                                             'premium': False,
                                                             'elite': False,
                                                             'igr': False,
                                                             'rented': True,
                                                             'event': True,
                                                             'gameMode': False,
                                                             'favorite': False,
                                                             'crystals': False,
                                                             'bonus': False,
                                                             'battleRoyale': False,
                                                             'clanRented': False,
                                                             'searchNameVehicle': '',
                                                             'unlock_available': False,
                                                             'can_convert': False,
                                                             'scroll_to': None},
                        LAST_STORAGE_VISITED_TIMESTAMP: -1,
                        SESSION_STATS_PREV_BATTLE_COUNT: 0,
                        ACTIVE_TEST_PARTICIPATION_CONFIRMED: False,
                        IS_SHOP_VISITED: False,
                        LAST_SHOP_ACTION_COUNTER_MODIFICATION: None,
                        OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES: set()},
 KEY_UI_FLAGS: {COMP7_UI_SECTION: {COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT: 0,
                                   COMP7_SHOP_SEEN_PRODUCTS: []},
                COLLECTIONS_SECTION: {COLLECTION_SHOWN_NEW_REWARDS: {},
                                      COLLECTION_SHOWN_NEW_ITEMS: {},
                                      COLLECTION_SHOWN_NEW_ITEMS_COUNT: {},
                                      COLLECTION_TUTORIAL_COMPLETED: set(),
                                      COLLECTION_WAS_ENABLED: True,
                                      COLLECTIONS_INTRO_SHOWN: False,
                                      COLLECTIONS_TAB_SHOWN_IDS: set(),
                                      COLLECTIONS_TAB_SHOWN_NEW_ITEMS: {},
                                      SHOWN_COMPLETED_COLLECTIONS: set(),
                                      LAST_SHOWN_NEW_COLLECTION: 0,
                                      LAST_SHOWN_COLLECTION_BALANCE: {}},
                'uiSpamVisited_store': False,
                'uiSpamVisited_profile': False,
                'uiSpamVisited_profileHof': False,
                'uiSpamVisited_profileTechniquePage': False,
                'uiSpamVisited_sessionStats': False,
                'uiSpamVisited_blueprintsButton': False,
                'uiSpamVisited_missions': False,
                'uiSpamVisited_MissionsMarathonView': False,
                'uiSpamVisited_PersonalMissionOperations': False,
                'uiSpamVisited_referralButtonCounter': False,
                'uiSpamVisited_AmmunitionPanelHintZoneHint': False,
                'uiSpamVisited_AmmunitionPanelBattleAbilitiesHint': False,
                'uiSpamVisited_CustomizationProgressionViewHint': False,
                'uiSpamVisited_TechTreeEvent': False,
                'uiSpamVisited_DogTagHangarHint': False,
                'uiSpamVisited_ModeSelectorWidgetsBtnHint': False,
                'uiSpamVisited_PersonalReservesHangarHint': False,
                'uiSpamVisited_ModernizedSetupTabHint': False,
                'uiSpamVisited_OfferBannerWindow': False,
                'uiSpamVisited_StrongholdView': False},
 KEY_BATTLE_HINTS: {},
 KEY_NEWBIE_HINTS: {}}

def _filterAccountSection(dataSec):
    for key, section in dataSec.items()[:]:
        if key == 'account':
            yield (key, section)


def _pack(value):
    return base64.b64encode(pickle.dumps(value))


def _unpack(value):
    return pickle.loads(base64.b64decode(value)) if value else None


def _recursiveStep(defaultDict, savedDict, finalDict):
    for key in defaultDict:
        defaultElement = defaultDict[key]
        savedElement = savedDict.get(key, None)
        if type(defaultElement) == dict:
            if savedElement is not None and type(savedElement) == dict:
                finalDict[key] = dict()
                _recursiveStep(defaultElement, savedElement, finalDict[key])
            else:
                finalDict[key] = deepcopy(defaultElement)
        if savedElement is not None:
            finalDict[key] = savedElement
        finalDict[key] = defaultElement

    return


class AccountSettings(object):
    onSettingsChanging = Event.Event()
    version = 75
    settingsCore = dependency.descriptor(ISettingsCore)
    __cache = {'login': None,
     'section': None}
    __sessionSettings = {'login': None,
     'section': None}
    __isFirstRun = True
    __isCleanPC = False

    @staticmethod
    def clearCache():
        AccountSettings.__cache['login'] = None
        AccountSettings.__cache['section'] = None
        AccountSettings.__sessionSettings['login'] = None
        AccountSettings.__sessionSettings['section'] = None
        return

    @staticmethod
    def _readSection(ds, name):
        if not ds.has_key(name):
            ds.write(name, '')
        return ds[name]

    @staticmethod
    def _readUserSection():
        if AccountSettings.__isFirstRun:
            AccountSettings.convert()
            AccountSettings.invalidateNewSettingsCounter()
            AccountSettings.__isFirstRun = False
        userLogin = AccountSettings.__getPlayerName()
        if AccountSettings.__cache['login'] != userLogin:
            ads = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
            for key, section in ads.items():
                if key == 'account' and section.readString('login') == userLogin:
                    AccountSettings.__cache['login'] = userLogin
                    AccountSettings.__cache['section'] = section
                    break
            else:
                newSection = ads.createSection('account')
                newSection.writeString('login', userLogin)
                AccountSettings.__cache['login'] = userLogin
                AccountSettings.__cache['section'] = newSection

        return AccountSettings.__cache['section']

    @staticmethod
    def isCleanPC():
        return AccountSettings.__isCleanPC

    @staticmethod
    def overrideDefaultSettings(name, value):
        if name not in DEFAULT_VALUES:
            return
        DEFAULT_VALUES[name].update(value)

    @staticmethod
    def convert():
        ads = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
        currVersion = ads.readInt('version', 0)
        if currVersion != AccountSettings.version:
            if currVersion < 1:
                AccountSettings.__isCleanPC = True
                for key, section in ads.items()[:]:
                    newSection = ads.createSection('account')
                    newSection.copy(section)
                    newSection.writeString('login', key)
                    ads.deleteSection(key)

            else:
                AccountSettings.__isCleanPC = False
            if currVersion < 2:
                MARKER_SETTINGS_MAP = {'showVehicleIcon': 'markerBaseIcon',
                 'showVehicleLevel': 'markerBaseLevel',
                 'showExInf4Destroyed': 'markerBaseDead'}
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        defaultMarker = DEFAULT_VALUES[KEY_SETTINGS]['markers'].copy()
                        needUpdate = False
                        for key1, section1 in accSettings.items()[:]:
                            if key1 in MARKER_SETTINGS_MAP:
                                defaultMarker[MARKER_SETTINGS_MAP[key1]] = pickle.loads(base64.b64decode(accSettings.readString(key1)))
                                accSettings.deleteSection(key1)
                                needUpdate = True

                        if needUpdate:
                            accSettings.write('markers', base64.b64encode(pickle.dumps(defaultMarker)))

            if currVersion < 3:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        defaultCursor = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()
                        cassetteDefValues = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()['cassette']
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'cursors':
                                defaultCursor = pickle.loads(base64.b64decode(section1.asString))
                                defaultCursor['cassette'] = cassetteDefValues
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write('cursors', base64.b64encode(pickle.dumps(defaultCursor)))

            if currVersion < 4:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        defaultCursor = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'cursors':
                                defaultCursor = pickle.loads(base64.b64decode(section1.asString))
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write('arcade', base64.b64encode(pickle.dumps(defaultCursor)))

            if currVersion < 5:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'markers':
                                accSettings.deleteSection(key1)

            if currVersion < 6:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        defaultSorting = DEFAULT_VALUES[KEY_SETTINGS]['statsSorting'].copy()
                        accSettings.write('statsSorting', base64.b64encode(pickle.dumps(defaultSorting)))

            if currVersion < 7:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        result = DEFAULT_VALUES[KEY_SETTINGS]['sniper'].copy()
                        for settingName, settingPickle in accSettings.items()[:]:
                            if settingName == 'sniper':
                                settingValues = pickle.loads(base64.b64decode(settingPickle.asString))
                                accSettings.deleteSection(settingName)
                                try:
                                    for k, v in settingValues.iteritems():
                                        newName = k[3].lower() + k[4:]
                                        result[newName] = v

                                except Exception:
                                    pass

                            break

                        accSettings.write('sniper', base64.b64encode(pickle.dumps(result)))

            if currVersion < 8:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                        for filterName, filterPickle in accFilters.items()[:]:
                            if filterName in ('cs_intro_view_vehicle', 'cs_list_view_vehicle', 'cs_unit_view_vehicle', 'cs_unit_view_settings'):
                                result = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                                value = pickle.loads(base64.b64decode(filterPickle.asString))
                                result.update(value)
                                accFilters.write(filterName, base64.b64encode(pickle.dumps(result)))

            if currVersion < 9:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                        for filterName, filterPickle in accFilters.items()[:]:
                            if filterName in ('cs_intro_view_vehicle', 'cs_list_view_vehicle', 'cs_unit_view_vehicle', 'cs_unit_view_settings'):
                                defaults = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                                userValue = pickle.loads(base64.b64decode(filterPickle.asString))
                                userValue['compatibleOnly'] = defaults['compatibleOnly']
                                accFilters.write(filterName, base64.b64encode(pickle.dumps(userValue)))

            if currVersion < 10:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        result = set(DEFAULT_VALUES[KEY_SETTINGS][KNOWN_SELECTOR_BATTLES]).copy()
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'unitWindow':
                                unitWindowVal = pickle.loads(base64.b64decode(section1.asString))
                                if 'isOpened' in unitWindowVal:
                                    if unitWindowVal['isOpened']:
                                        result.add(SELECTOR_BATTLE_TYPES.UNIT)
                                        accSettings.write(KNOWN_SELECTOR_BATTLES, base64.b64encode(pickle.dumps(result)))
                                    section1.deleteSection('isOpened')
                                    break

            if currVersion < 11:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                        defaultSorting = DEFAULT_VALUES[KEY_SETTINGS]['statsSortingSortie'].copy()
                        accSettings.write('statsSortingSortie', base64.b64encode(pickle.dumps(defaultSorting)))

            if currVersion < 12:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if KNOWN_SELECTOR_BATTLES in accSettings.keys():
                        known = _unpack(accSettings[KNOWN_SELECTOR_BATTLES].asString)
                        if SELECTOR_BATTLE_TYPES.UNIT in known:
                            known.remove(SELECTOR_BATTLE_TYPES.UNIT)
                            accSettings.write(KNOWN_SELECTOR_BATTLES, _pack(known))
                    if 'unitWindow' in accSettings.keys():
                        accSettings.deleteSection('unitWindow')

            if currVersion < 13:
                enableVoIPVal = False
                if Settings.g_instance.userPrefs.has_key('enableVoIP'):
                    enableVoIPVal = Settings.g_instance.userPrefs.readBool('enableVoIP')
                for key, section in _filterAccountSection(ads):
                    AccountSettings._readSection(section, KEY_SETTINGS).write('enableVoIP', _pack(enableVoIPVal))

                Settings.g_instance.userPrefs.deleteSection('enableVoIP')
            if currVersion < 17:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings._readSection(section, KEY_FAVORITES)
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == FALLOUT_VEHICLES:
                                accSettings.deleteSection(key1)

            if currVersion < 18:
                cmSection = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
                for command, section in cmSection.items()[:]:
                    newSection = None
                    satelliteKeys = ''
                    fireKey = AccountSettings._readSection(section, 'fireKey').asString
                    if fireKey == 'KEY_SPACE':
                        if command == 'CMD_BLOCK_TRACKS':
                            pass
                        elif command == 'CMD_STOP_UNTIL_FIRE':
                            satelliteKeys = AccountSettings._readSection(section, 'satelliteKeys').asString
                            cmSection.deleteSection('CMD_STOP_UNTIL_FIRE')
                            newSection = cmSection.createSection('CMD_STOP_UNTIL_FIRE')
                        else:
                            newSection = cmSection.createSection('CMD_BLOCK_TRACKS')
                    if newSection is not None:
                        newSection.writeString('fireKey', 'KEY_NONE')
                        newSection.writeString('satelliteKeys', satelliteKeys)

                CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 19:
                pass
            if currVersion < 20:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    accSettings.write('battleLoadingInfo', base64.b64encode(pickle.dumps(0)))
                    AccountSettings._readSection(section, KEY_FILTERS).deleteSection('joinCommandPressed')

            if currVersion < 21:
                import SoundGroups
                SoundGroups.g_instance.setMasterVolume(1.0)
                SoundGroups.g_instance.setVolume('music', 1.0)
                SoundGroups.g_instance.setVolume('vehicles', 1.0)
                SoundGroups.g_instance.setVolume('effects', 1.0)
                SoundGroups.g_instance.setVolume('gui', 1.0)
                SoundGroups.g_instance.setVolume('ambient', 1.0)
                SoundGroups.g_instance.savePreferences()
            if currVersion < 22:
                pass
            if currVersion < 23:
                for key, section in _filterAccountSection(ads):
                    AccountSettings._readSection(section, KEY_SETTINGS).deleteSection('FootballVehSelectedOnce')

            if currVersion < 24:
                for key, section in _filterAccountSection(ads):
                    AccountSettings._readSection(section, KEY_SETTINGS).deleteSection('FootballCustTriggerShown')
                    AccountSettings._readSection(section, KEY_SETTINGS).deleteSection('FootballVehSelectedOnce')

            if currVersion < 24:
                import SoundGroups
                SoundGroups.g_instance.setVolume('music_hangar', 1.0)
                SoundGroups.g_instance.setVolume('voice', 1.0)
                SoundGroups.g_instance.setVolume('ev_ambient', 0.8)
                SoundGroups.g_instance.setVolume('ev_effects', 0.8)
                SoundGroups.g_instance.setVolume('ev_gui', 0.8)
                SoundGroups.g_instance.setVolume('ev_music', 0.8)
                SoundGroups.g_instance.setVolume('ev_vehicles', 0.8)
                SoundGroups.g_instance.setVolume('ev_voice', 0.8)
                SoundGroups.g_instance.savePreferences()
            if currVersion < 25:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                    for filterName, filterPickle in accFilters.items():
                        if filterName in ('shop_module', 'shop_shell', 'inventory_vehicle', 'inventory_module', 'inventory_shell', 'inventory_optionalDevice', 'inventory_equipment'):
                            defaults = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                            accFilters.write(filterName, base64.b64encode(pickle.dumps(defaults)))

            if currVersion < 26:
                for key, section in _filterAccountSection(ads):
                    AccountSettings._readSection(section, KEY_SETTINGS).deleteSection('new_customization_items')
                    AccountSettings._readSection(section, KEY_SETTINGS).deleteSection('statsSortingEvent')

            if currVersion < 27:
                legacyToNewMode = {'hidden': 0,
                 'short': 1,
                 'medium': 2,
                 'medium2': 3,
                 'large': 4}
                for key, section in _filterAccountSection(ads):
                    settingsSection = AccountSettings._readSection(section, KEY_SETTINGS)
                    if 'players_panel' in settingsSection.keys():
                        panelSettings = _unpack(settingsSection['players_panel'].asString)
                        if 'state' in panelSettings:
                            presentMode = panelSettings['state']
                            if presentMode in legacyToNewMode.keys():
                                panelSettings['state'] = legacyToNewMode[presentMode]
                                settingsSection.write('players_panel', _pack(panelSettings))

            if currVersion < 28:
                for key, section in _filterAccountSection(ads):
                    filters = AccountSettings._readSection(section, KEY_FILTERS)
                    filters.deleteSection('lastClubOpenedForApps')
                    filters.deleteSection('showInviteCommandBtnAnimation')

            if currVersion < 29:
                getSection = AccountSettings._readSection
                cmSection = getSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
                cmdItems = cmSection.items()[:]
                if cmdItems:
                    checkUserKeyBinding = AccountSettings.__checkUserKeyBinding
                    hasKeyG, hasCmdVoice, bindedG = checkUserKeyBinding('KEY_G', 'CMD_VOICECHAT_ENABLE', cmdItems)
                    hasKeyH, hasCmdHorn, bindedH = checkUserKeyBinding('KEY_H', 'CMD_USE_HORN', cmdItems)
                    if hasCmdHorn:
                        cmSection.deleteSection('CMD_USE_HORN')
                    isKeyGDefault = not hasKeyG or bindedG
                    keyForCmdTraject = 'KEY_G' if isKeyGDefault else 'KEY_NONE'
                    getSection(cmSection, 'CMD_CM_TRAJECTORY_VIEW').writeString('fireKey', keyForCmdTraject)
                    if not hasCmdVoice or bindedG:
                        isKeyHDefault = not hasKeyH or bindedH
                        keyForCmdVoice = 'KEY_H' if isKeyHDefault else 'KEY_NONE'
                        getSection(cmSection, 'CMD_VOICECHAT_ENABLE').writeString('fireKey', keyForCmdVoice)
                    CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 29:
                for key, section in _filterAccountSection(ads):
                    filtersSection = AccountSettings._readSection(section, KEY_FILTERS)
                    if 'searchNameVehicle' in filtersSection.keys():
                        searchName = _unpack(filtersSection['searchNameVehicle'].asString)
                        filtersSection.write(CAROUSEL_FILTER_CLIENT_1, _pack({'searchNameVehicle': searchName}))
                        filtersSection.deleteSection('searchNameVehicle')

            if currVersion < 30:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                    for filterName, filterPickle in accFilters.items():
                        if filterName in ('inventory_vehicle', 'shop_current', 'inventory_current', 'shop_tradeInVehicle', 'shop_restoreVehicle'):
                            defaults = DEFAULT_VALUES[KEY_FILTERS][filterName]
                            accFilters.write(filterName, base64.b64encode(pickle.dumps(defaults)))

            if currVersion < 32:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    accSettings.deleteSection(NEW_SETTINGS_COUNTER)

            if currVersion < 32:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    accSettings.deleteSection(SHOW_CRYSTAL_HEADER_BAND)

            if currVersion < 33:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if QUESTS in accSettings.keys():
                        quests = _unpack(accSettings[QUESTS].asString)
                        if 'potapov' in quests:
                            newVersion = quests.pop('potapov')
                            newVersion['operationsVisited'] = newVersion.pop('tilesVisited')
                            accSettings.write(QUESTS, _pack(quests))

            if currVersion < 34:
                import SoundGroups
                maxVolume = max((SoundGroups.g_instance.getVolume(category) for category in ('vehicles', 'ambient', 'voice', 'gui', 'effects', 'music', 'music_hangar')))
                SoundGroups.g_instance.setVolume('music', maxVolume)
                SoundGroups.g_instance.setVolume('music_hangar', maxVolume)
                SoundGroups.g_instance.savePreferences()
            if currVersion < 35:
                AccountSettings.settingsCore.applySetting('loginServerSelection', False)
            if currVersion < 36:
                from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_COUNTERS)
                    if NEW_LOBBY_TAB_COUNTER in accSettings.keys():
                        counters = _unpack(accSettings[NEW_LOBBY_TAB_COUNTER].asString)
                        if LobbyHeader.TABS.PERSONAL_MISSIONS in counters:
                            counters[LobbyHeader.TABS.PERSONAL_MISSIONS] = True
                            accSettings.write(NEW_LOBBY_TAB_COUNTER, _pack(counters))

            if currVersion < 37:
                AccountSettings.checkAndResetFireKeyIfInUse('CMD_QUEST_PROGRESS_SHOW', 'KEY_N')
                CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 38:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if CUSTOMIZATION_SECTION in accSettings.keys():
                        accSettings.write(CUSTOMIZATION_SECTION, _pack({}))
                    obsoleteKeys = ('questProgressShowsCount', 'trajectoryViewHintCounter', 'siegeModeHintCounter')
                    for sectionName in obsoleteKeys:
                        if sectionName in accSettings.keys():
                            accSettings.deleteSection(sectionName)

            if currVersion < 39:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if CUSTOMIZATION_SECTION in accSettings.keys():
                        custSett = _unpack(accSettings[CUSTOMIZATION_SECTION].asString)
                        if CAROUSEL_ARROWS_HINT_SHOWN_FIELD in custSett:
                            del custSett[CAROUSEL_ARROWS_HINT_SHOWN_FIELD]
                        accSettings.write(CUSTOMIZATION_SECTION, _pack(custSett))

            if currVersion < 40:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    obsoleteKeys = ('questProgressHint', 'helpScreenHint')
                    for sectionName in obsoleteKeys:
                        if sectionName in accSettings.keys():
                            accSettings.deleteSection(sectionName)

            if currVersion < 41:
                for key, section in _filterAccountSection(ads):
                    keyFlush = (RANKED_AWARDS_BUBBLE_YEAR_REACHED, RANKED_WEB_INFO, RANKED_WEB_INFO_UPDATE)
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    for flushName in keyFlush:
                        if flushName in keySettings.keys():
                            keySettings.write(flushName, _pack(None))

                    countersFlush = (RANKED_AWARDS_COUNTER, RANKED_INFO_COUNTER)
                    counterSettings = AccountSettings._readSection(section, KEY_COUNTERS)
                    for flushName in countersFlush:
                        if flushName in counterSettings.keys():
                            counterSettings.write(flushName, _pack(1))

            if currVersion < 42:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if PRE_BATTLE_HINT_SECTION in accSettings.keys():
                        preBattleSection = DEFAULT_VALUES[KEY_SETTINGS][PRE_BATTLE_HINT_SECTION].copy()
                        defPre = DEFAULT_VALUES[KEY_SETTINGS][PRE_BATTLE_HINT_SECTION].copy()[IBC_HINT_SECTION]
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == PRE_BATTLE_HINT_SECTION:
                                preBattleSection = _unpack(section1.asString)
                                preBattleSection[IBC_HINT_SECTION] = defPre
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write('preBattleHintSection', _pack(preBattleSection))

            if currVersion < 43:
                AccountSettings.checkAndResetFireKeyIfInUse(expectedCommand='CMD_CHAT_SHORTCUT_THANKYOU', expectedKey='KEY_F3')
                AccountSettings.checkAndResetFireKeyIfInUse(expectedCommand='CMD_CHAT_SHORTCUT_CONTEXT_COMMIT', expectedKey='KEY_F2')
                AccountSettings.removeOldCommandAndReuseFireKey(oldCommand='CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET', newCommand='CMD_CHAT_SHORTCUT_CONTEXT_COMMAND')
                CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 44:
                AccountSettings.checkAndResetFireKeyIfInUse(expectedCommand='CMD_CHAT_SHORTCUT_AFFIRMATIVE', expectedKey='KEY_F5')
                AccountSettings.checkAndResetFireKeyIfInUse(expectedCommand='CMD_CHAT_SHORTCUT_NEGATIVE', expectedKey='KEY_F6')
                AccountSettings.removeOldCommandAndReuseFireKey(oldCommand='CMD_CHAT_SHORTCUT_POSITIVE', newCommand='CMD_CHAT_SHORTCUT_AFFIRMATIVE')
                CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 45:
                pass
            if currVersion < 46:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                    if GUI_START_BEHAVIOR in accFilters.keys():
                        guiSettings = _unpack(accFilters[GUI_START_BEHAVIOR].asString)
                        obsoleteKeys = ('lastShownEpicWelcomeScreen', 'isEpicWelcomeViewShowed')
                        for sectionName in obsoleteKeys:
                            if sectionName in guiSettings:
                                del guiSettings[sectionName]

                        accFilters.write(GUI_START_BEHAVIOR, _pack(guiSettings))

            if currVersion < 47:
                for key, section in _filterAccountSection(ads):
                    filtersSection = AccountSettings._readSection(section, KEY_FILTERS)
                    existingSections = set(filtersSection.keys()).intersection((CAROUSEL_FILTER_CLIENT_1,
                     BATTLEPASS_CAROUSEL_FILTER_CLIENT_1,
                     RANKED_CAROUSEL_FILTER_CLIENT_1,
                     MAPBOX_CAROUSEL_FILTER_CLIENT_1,
                     EPICBATTLE_CAROUSEL_FILTER_CLIENT_1,
                     ROYALE_CAROUSEL_FILTER_CLIENT_1,
                     STORAGE_BLUEPRINTS_CAROUSEL_FILTER,
                     STORAGE_VEHICLES_CAROUSEL_FILTER_1))
                    for filterSection in existingSections:
                        savedFilters = _unpack(filtersSection[filterSection].asString)
                        defaults = AccountSettings.getFilterDefault(filterSection)
                        updatedFilters = {key:savedFilters.get(key, defaults[key]) for key in defaults}
                        filtersSection.write(filterSection, _pack(updatedFilters))

            if currVersion < 48:
                pass
            if currVersion < 49:
                for key, section in _filterAccountSection(ads):
                    filtersSection = AccountSettings._readSection(section, KEY_FILTERS)
                    existingSections = set(filtersSection.keys()).intersection((CAROUSEL_FILTER_CLIENT_1,
                     RANKED_CAROUSEL_FILTER_CLIENT_1,
                     ROYALE_CAROUSEL_FILTER_CLIENT_1,
                     EPICBATTLE_CAROUSEL_FILTER_CLIENT_1,
                     EPICBATTLE_CAROUSEL_FILTER_CLIENT_2,
                     MAPBOX_CAROUSEL_FILTER_CLIENT_1,
                     STORAGE_VEHICLES_CAROUSEL_FILTER_1,
                     STORAGE_BLUEPRINTS_CAROUSEL_FILTER))
                    for filterSection in existingSections:
                        savedFilters = _unpack(filtersSection[filterSection].asString)
                        if 'clanRented' in savedFilters:
                            savedFilters['clanRented'] = False
                        filtersSection.write(filterSection, _pack(savedFilters))

            if currVersion < 50:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                    if GUI_START_BEHAVIOR in accFilters.keys():
                        guiSettings = _unpack(accFilters[GUI_START_BEHAVIOR].asString)
                        obsoleteKeys = ('techTreeIntroBlueprintsReceived', 'techTreeIntroShowed')
                        for sectionName in obsoleteKeys:
                            if sectionName in guiSettings:
                                del guiSettings[sectionName]

                        accFilters.write(GUI_START_BEHAVIOR, _pack(guiSettings))

            if currVersion < 51:
                for key, section in _filterAccountSection(ads):
                    keyFlush = (RANKED_AWARDS_BUBBLE_YEAR_REACHED, RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED)
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    for flushName in keyFlush:
                        if flushName in keySettings.keys():
                            keySettings.write(flushName, _pack(False))

            if currVersion < 52:
                pass
            if currVersion < 53:
                for key, section in _filterAccountSection(ads):
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if LAST_BATTLE_PASS_POINTS_SEEN in keySettings.keys():
                        keySettings.write(LAST_BATTLE_PASS_POINTS_SEEN, _pack({}))
                    if IS_BATTLE_PASS_EXTRA_STARTED in keySettings.keys():
                        keySettings.write(IS_BATTLE_PASS_EXTRA_STARTED, _pack(False))

            if currVersion < 54:
                for key, section in _filterAccountSection(ads):
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    obsoleteKey = 'battleRoyaleHangarBottomPanelViewed'
                    if obsoleteKey in keySettings.keys():
                        keySettings.deleteSection(obsoleteKey)

            if currVersion < 55:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if PRE_BATTLE_HINT_SECTION in accSettings.keys():
                        preBattleSection = DEFAULT_VALUES[KEY_SETTINGS][PRE_BATTLE_HINT_SECTION].copy()
                        defPre = preBattleSection[RESERVES_HINT_SECTION].copy()
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == PRE_BATTLE_HINT_SECTION:
                                preBattleSection = _unpack(section1.asString)
                                preBattleSection[RESERVES_HINT_SECTION] = defPre
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write(PRE_BATTLE_HINT_SECTION, _pack(preBattleSection))

            if currVersion < 56:
                for key, section in _filterAccountSection(ads):
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if FUN_RANDOM_HINT_SECTION in keySettings.keys():
                        keySettings.write(FUN_RANDOM_HINT_SECTION, _pack({}))

            if currVersion < 57:
                for key, section in _filterAccountSection(ads):
                    obsoleteKeys = (RESOURCE_WELL_START_SHOWN, RESOURCE_WELL_END_SHOWN)
                    settings = AccountSettings._readSection(section, KEY_NOTIFICATIONS)
                    for sectionName in obsoleteKeys:
                        if sectionName in settings.keys():
                            settings.deleteSection(sectionName)

            if currVersion < 58:
                for key, section in _filterAccountSection(ads):
                    accSessionSettings = AccountSettings._readSection(section, KEY_SESSION_SETTINGS)
                    obsoleteKey = 'seniorityAwardsWindowShown'
                    if obsoleteKey in accSessionSettings.keys():
                        accSessionSettings.deleteSection(obsoleteKey)

            if currVersion < 59:
                for key, section in _filterAccountSection(ads):
                    keySettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if IS_BATTLE_PASS_COLLECTION_SEEN in keySettings.keys():
                        keySettings.write(IS_BATTLE_PASS_COLLECTION_SEEN, _pack(False))

            if currVersion < 60:
                if Settings.g_instance.userPrefs.has_key('loginPage'):
                    Settings.g_instance.userPrefs.deleteSection('loginPage')
            if currVersion < 61:
                for key, section in _filterAccountSection(ads):
                    accSessionSettings = AccountSettings._readSection(section, KEY_FILTERS)
                    obsoleteKey = 'awards'
                    if obsoleteKey in accSessionSettings.keys():
                        accSessionSettings.deleteSection(obsoleteKey)

            if currVersion < 62:
                pass
            if currVersion < 63:
                pass
            if currVersion < 64:
                obsoleteKeys = ['isEntryPointsEnabled',
                 'isTankRentalEnabled',
                 'isFreeDirectivesEnabled',
                 'rentPendingVehCD']
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if WOT_PLUS in accSettings.keys():
                        wotPlusSettings = _unpack(accSettings[WOT_PLUS].asString)
                        for key in obsoleteKeys:
                            wotPlusSettings.pop(key, None)

                        accSettings.write(WOT_PLUS, _pack(wotPlusSettings))

            if currVersion < 65:
                for key, section in _filterAccountSection(ads):
                    accSessionSettings = AccountSettings._readSection(section, KEY_COUNTERS)
                    obsoleteKey = 'battleMattersSeen'
                    if obsoleteKey in accSessionSettings.keys():
                        accSessionSettings.deleteSection(obsoleteKey)

            if currVersion < 66:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    bmKey = BattleMatters.BATTLE_MATTERS_SETTINGS
                    if bmKey in accSettings.keys():
                        bmSettings = DEFAULT_VALUES[KEY_SETTINGS][bmKey].copy()
                        bmAccSettings = _unpack(accSettings[bmKey].asString)
                        bmSettings.update(bmAccSettings)
                        accSettings.write(bmKey, _pack(bmSettings))

            if currVersion < 67:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if CREW_SKINS_VIEWED in accSettings.keys():
                        accSettings.deleteSection(CREW_SKINS_VIEWED)

            if currVersion < 68:
                for key, section in _filterAccountSection(ads):
                    keySettings = AccountSettings._readSection(section, KEY_NOTIFICATIONS)
                    if SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP in keySettings.keys():
                        keySettings.write(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, _pack(None))

            if currVersion < 69:
                pass
            if currVersion < 70:
                pass
            if currVersion < 71:
                isZeroVersion = currVersion is 0
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    panelSettingsExist = 'players_panel' in accSettings.keys()
                    if not isZeroVersion:
                        panelSettings = _unpack(accSettings['players_panel'].asString) if panelSettingsExist else DEFAULT_VALUES[KEY_SETTINGS]['players_panel']
                        panelSettings['state'] = panelSettings.get('state')
                        if panelSettings['state'] is None:
                            panelSettings['state'] = 2
                        accSettings.write('players_panel', _pack(panelSettings))

            if currVersion < 72:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings._readSection(section, KEY_FILTERS)
                    obsoleteKey = 'barracks_filter'
                    if obsoleteKey in accFilters.keys():
                        accFilters.deleteSection(obsoleteKey)

            if currVersion < 73:
                oldShowPersonalReservesKey = 'shownPersonalReserves'
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if oldShowPersonalReservesKey in accSettings.keys():
                        accSettings.deleteSection(oldShowPersonalReservesKey)

            if currVersion < 74:
                for key, section in _filterAccountSection(ads):
                    counterSettings = AccountSettings._readSection(section, KEY_COUNTERS)
                    if counterSettings.has_key(CLAN_NOTIFICATION_COUNTERS):
                        clanNotificationCounters = _unpack(counterSettings[CLAN_NOTIFICATION_COUNTERS].asString)
                        if 'wgcq_hangar_bubble' in clanNotificationCounters:
                            clanNotificationCounters.pop('wgcq_hangar_bubble')
                            counterSettings.write(CLAN_NOTIFICATION_COUNTERS, _pack(clanNotificationCounters))

            if currVersion < 75:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
                    if WOT_PLUS in accSettings.keys():
                        wotPlusSettings = _unpack(accSettings[WOT_PLUS].asString)
                        wotPlusSettings['isOnboardingShown'] = False
                        accSettings.write(WOT_PLUS, _pack(wotPlusSettings))
                    if SHOWN_WOT_PLUS_INTRO in accSettings.keys():
                        accSettings.write(SHOWN_WOT_PLUS_INTRO, _pack(False))

            ads.writeInt('version', AccountSettings.version)
        return

    @staticmethod
    def getFilterDefault(name):
        return DEFAULT_VALUES[KEY_FILTERS].get(name, None)

    @staticmethod
    def invalidateNewSettingsCounter():
        ads = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
        currentDefaults = AccountSettings.getSettingsDefault(NEW_SETTINGS_COUNTER)
        filtered = _filterAccountSection(ads)
        for _, section in filtered:
            accSettings = AccountSettings._readSection(section, KEY_SETTINGS)
            if NEW_SETTINGS_COUNTER in accSettings.keys():
                savedNewSettingsCounters = _unpack(accSettings[NEW_SETTINGS_COUNTER].asString)
                if savedNewSettingsCounters is not None:
                    newSettingsCounters = AccountSettings.updateNewSettingsCounter(currentDefaults, savedNewSettingsCounters)
                    accSettings.write(NEW_SETTINGS_COUNTER, _pack(newSettingsCounters))

        return

    @staticmethod
    def checkAndResetFireKeyIfInUse(expectedCommand, expectedKey):
        cmSection = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
        for command, section in cmSection.items()[:]:
            fireKey = AccountSettings._readSection(section, 'fireKey').asString
            if fireKey == expectedKey:
                if command == expectedCommand:
                    break
                else:
                    cmSection.deleteSection(expectedCommand)
                    newSection = cmSection.createSection(expectedCommand)
                    newSection.writeString('fireKey', 'KEY_NONE')
                    break

    @staticmethod
    def removeOldCommandAndReuseFireKey(oldCommand, newCommand):
        cmSection = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
        for command, section in cmSection.items()[:]:
            if command == oldCommand:
                fireKey = AccountSettings._readSection(section, 'fireKey').asString
                cmSection.deleteSection(newCommand)
                newSection = cmSection.createSection(newCommand)
                newSection.writeString('fireKey', fireKey)
                cmSection.deleteSection(command)
                break

    @staticmethod
    def getFilterDefaults(names):
        result = {}
        for name in names:
            result.update(AccountSettings.getFilterDefault(name))

        return result

    @staticmethod
    def getFilter(name):
        return AccountSettings._getValue(name, KEY_FILTERS)

    @staticmethod
    def setFilter(name, value):
        AccountSettings._setValue(name, value, KEY_FILTERS)

    @staticmethod
    def getSettingsDefault(name):
        return DEFAULT_VALUES[KEY_SETTINGS].get(name, None)

    @classmethod
    def getSettings(cls, name):
        return cls._getValue(name, KEY_SETTINGS)

    @classmethod
    def setSettings(cls, name, value):
        cls._setValue(name, value, KEY_SETTINGS)

    @staticmethod
    def getManualData(name):
        return AccountSettings._getValue(name, KEY_MANUAL)

    @staticmethod
    def setManualData(name, value):
        AccountSettings._setValue(name, value, KEY_MANUAL)

    @staticmethod
    def setManualUnreadPages(content):
        ver = getClientVersion()
        return AccountSettings.setManualData(MANUAL_NEW_CONTENT, {ver: content})

    @staticmethod
    def getManualUnreadPages():
        ver = getClientVersion()
        data = AccountSettings.getManualData(MANUAL_NEW_CONTENT)
        return data.get(ver, None)

    @staticmethod
    def getFavorites(name):
        return AccountSettings._getValue(name, KEY_FAVORITES)

    @staticmethod
    def setFavorites(name, value):
        AccountSettings._setValue(name, value, KEY_FAVORITES)

    @staticmethod
    def getCounters(name):
        return AccountSettings._getValue(name, KEY_COUNTERS)

    @staticmethod
    def setCounters(name, value):
        AccountSettings._setValue(name, value, KEY_COUNTERS)

    @staticmethod
    def getNotifications(name):
        return AccountSettings._getValue(name, KEY_NOTIFICATIONS)

    @staticmethod
    def setNotifications(name, value):
        AccountSettings._setValue(name, value, KEY_NOTIFICATIONS)

    @staticmethod
    def getSessionSettings(name):
        return AccountSettings.__getSessionSettings(name)

    @staticmethod
    def setSessionSettings(name, value):
        AccountSettings.__setSessionSettings(name, value)

    @staticmethod
    def getSessionSettingsDefault(name):
        return DEFAULT_VALUES[KEY_SESSION_SETTINGS].get(name, None)

    @staticmethod
    def updateNewSettingsCounter(defaultDict, savedDict):
        finalDict = {}
        _recursiveStep(defaultDict, savedDict, finalDict)
        return finalDict

    @classmethod
    def getUIFlag(cls, name):
        return cls._getValue(name, KEY_UI_FLAGS, force=True)

    @classmethod
    def setUIFlag(cls, name, value):
        return cls._setValue(name, value, KEY_UI_FLAGS, force=True)

    @classmethod
    def getBattleMattersSetting(cls, name):
        return cls.getSettings(BattleMatters.BATTLE_MATTERS_SETTINGS).get(name)

    @classmethod
    def setBattleMattersSetting(cls, name, value):
        bmSection = cls.getSettings(BattleMatters.BATTLE_MATTERS_SETTINGS)
        if name in bmSection:
            bmSection[name] = value
            cls._setValue(BattleMatters.BATTLE_MATTERS_SETTINGS, bmSection, KEY_SETTINGS)
        else:
            _logger.error("Cann't set value in %s section for %s.", BattleMatters.BATTLE_MATTERS_SETTINGS, name)

    @classmethod
    def getNewbieHints(cls, name, default=None):
        return cls._getValue(name, KEY_NEWBIE_HINTS, force=True, default=default)

    @classmethod
    def setNewbieHints(cls, name, value, default=None):
        return cls._setValue(name, value, KEY_NEWBIE_HINTS, force=True, default=default)

    @classmethod
    def getBattleHints(cls, name, default=None):
        return cls._getValue(name, KEY_BATTLE_HINTS, force=True, default=default)

    @classmethod
    def setBattleHints(cls, name, value, default=None):
        return cls._setValue(name, value, KEY_BATTLE_HINTS, force=True, default=default)

    @classmethod
    def getVehicleViewedModules(cls, vehIntCD):
        viewedModules = cls.getUIFlag(VIEWED_MODULES_SECTION)
        return viewedModules.get(vehIntCD, None) if viewedModules else None

    @classmethod
    def setVehicleViewedModules(cls, vehIntCD, modules):
        viewedModules = cls.getUIFlag(VIEWED_MODULES_SECTION)
        if viewedModules is None:
            viewedModules = {}
        viewedModules.update({vehIntCD: modules})
        cls.setUIFlag(VIEWED_MODULES_SECTION, viewedModules)
        return

    @classmethod
    def clearVehicleViewedModules(cls, vehIntCD):
        viewedModules = cls.getUIFlag(VIEWED_MODULES_SECTION)
        if viewedModules is not None and vehIntCD in viewedModules:
            del viewedModules[vehIntCD]
        cls.setUIFlag(VIEWED_MODULES_SECTION, viewedModules)
        return

    @classmethod
    def isVersionedRuleCompleted(cls, ruleID):
        versionedRules = cls.getUIFlag(LIMITED_UI_VERSIONED_RULES)
        return ruleID in versionedRules if versionedRules else False

    @classmethod
    def getCompletedVersionedRules(cls):
        return cls.getUIFlag(LIMITED_UI_VERSIONED_RULES)

    @classmethod
    def completeVersionedRules(cls, ruleIDs):
        versionedRules = cls.getUIFlag(LIMITED_UI_VERSIONED_RULES)
        if versionedRules is None:
            versionedRules = []
        versionedRules = list(set(ruleIDs + versionedRules))
        cls.setUIFlag(LIMITED_UI_VERSIONED_RULES, versionedRules)
        return

    @classmethod
    def clearVersionedRules(cls, ruleIDs):
        versionedRules = cls.getUIFlag(LIMITED_UI_VERSIONED_RULES)
        if versionedRules is None:
            return
        else:
            for ruleID in ruleIDs:
                if ruleID in versionedRules:
                    versionedRules.remove(ruleID)

            cls.setUIFlag(LIMITED_UI_VERSIONED_RULES, versionedRules)
            return

    @staticmethod
    def _getValue(name, setting, force=False, default=None):
        fds = AccountSettings._readSection(AccountSettings._readUserSection(), setting)
        try:
            if fds.has_key(name):
                return pickle.loads(base64.b64decode(fds.readString(name)))
        except Exception:
            if constants.IS_DEVELOPMENT:
                LOG_CURRENT_EXCEPTION()

        return copy.deepcopy(DEFAULT_VALUES[setting][name]) if name in DEFAULT_VALUES[setting] else default

    @staticmethod
    def _setValue(name, value, setting, force=False, default=None):
        if name not in DEFAULT_VALUES[setting] and not force:
            raise SoftException('Default value "{}" is not found in "{}"'.format(name, type))
        if AccountSettings._getValue(name, setting, force, default=default) != value:
            fds = AccountSettings._readSection(AccountSettings._readUserSection(), setting)
            if name in DEFAULT_VALUES[setting] and DEFAULT_VALUES[setting][name] == value:
                fds.deleteSection(name)
            else:
                fds.write(name, base64.b64encode(pickle.dumps(value)))
            AccountSettings.onSettingsChanging(name, value)

    @staticmethod
    def __getSessionSettings(name):
        if name in DEFAULT_VALUES[KEY_SESSION_SETTINGS]:
            sessionSettings = AccountSettings.__getUserSessionSettings()
            if isinstance(sessionSettings, dict) and name in sessionSettings.keys():
                return copy.deepcopy(sessionSettings.get(name))
            return copy.deepcopy(DEFAULT_VALUES[KEY_SESSION_SETTINGS][name])
        else:
            return None

    @staticmethod
    def __setSessionSettings(name, value):
        if name not in DEFAULT_VALUES[KEY_SESSION_SETTINGS]:
            raise SoftException('Default value "{}" is not found in "{}"'.format(name, type))
        if AccountSettings.__getSessionSettings(name) != value:
            sessionSettings = AccountSettings.__getUserSessionSettings()
            if isinstance(sessionSettings, dict):
                if DEFAULT_VALUES[KEY_SESSION_SETTINGS][name] != value:
                    sessionSettings.update({name: value})
                elif name in sessionSettings.keys():
                    sessionSettings.pop(name)

    @staticmethod
    def __getUserSessionSettings():
        userLogin = AccountSettings.__getPlayerName()
        if AccountSettings.__sessionSettings['section'] is None:
            AccountSettings.__sessionSettings['section'] = dict()
        if AccountSettings.__sessionSettings['login'] != userLogin and userLogin != '':
            AccountSettings.__sessionSettings['section'] = dict()
            AccountSettings.__sessionSettings['login'] = userLogin
        return AccountSettings.__sessionSettings['section']

    @staticmethod
    def __checkUserKeyBinding(key=None, command=None, commandSectionItems=None):
        if commandSectionItems is None:
            commandSection = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
            commandSectionItems = commandSection.items()[:]
        hasKey, hasCommand, binded = False, False, False
        for cmd, section in commandSectionItems:
            fireKey = AccountSettings._readSection(section, 'fireKey').asString
            if key is not None and fireKey == key:
                if cmd == command:
                    return (True, True, True)
                hasKey = True
            if command is not None and cmd == command:
                hasCommand = True

        return (hasKey, hasCommand, binded)

    @classmethod
    def __getPlayerName(cls):
        playerName = getattr(BigWorld.player(), 'name', '')
        return Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('user', playerName) if not playerName else playerName
