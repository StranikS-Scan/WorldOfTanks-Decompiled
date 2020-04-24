# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountSettings.py
import base64
import copy
import cPickle as pickle
from copy import deepcopy
import constants
import BigWorld
import CommandMapping
import Settings
import Event
import WWISE
from constants import VEHICLE_CLASSES, MAX_VEHICLE_LEVEL
from items.components.crew_books_constants import CREW_BOOK_RARITY
from account_helpers.settings_core.settings_constants import GAME
from account_helpers import gameplay_ctx
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.genConsts.MISSIONS_CONSTANTS import MISSIONS_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from soft_exception import SoftException
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
import nations
KEY_FILTERS = 'filters'
KEY_SESSION_SETTINGS = 'session_settings'
KEY_SETTINGS = 'settings'
KEY_FAVORITES = 'favorites'
KEY_COUNTERS = 'counters'
KEY_NOTIFICATIONS = 'notifications'
KEY_UI_FLAGS = 'ui_flags'
CAROUSEL_FILTER_1 = 'CAROUSEL_FILTER_1'
CAROUSEL_FILTER_2 = 'CAROUSEL_FILTER_2'
CAROUSEL_FILTER_CLIENT_1 = 'CAROUSEL_FILTER_CLIENT_1'
MISSION_SELECTOR_FILTER = 'MISSION_SELECTOR_FILTER'
PM_SELECTOR_FILTER = 'PM_SELECTOR_FILTER'
BLUEPRINTS_STORAGE_FILTER = 'BLUEPRINTS_STORAGE_FILTER'
RANKED_CAROUSEL_FILTER_1 = 'RANKED_CAROUSEL_FILTER_1'
RANKED_CAROUSEL_FILTER_2 = 'RANKED_CAROUSEL_FILTER_2'
RANKED_CAROUSEL_FILTER_CLIENT_1 = 'RANKED_CAROUSEL_FILTER_CLIENT_1'
EPICBATTLE_CAROUSEL_FILTER_1 = 'EPICBATTLE_CAROUSEL_FILTER_1'
EPICBATTLE_CAROUSEL_FILTER_2 = 'EPICBATTLE_CAROUSEL_FILTER_2'
EPICBATTLE_CAROUSEL_FILTER_CLIENT_1 = 'EPICBATTLE_CAROUSEL_FILTER_CLIENT_1'
BOB_CAROUSEL_FILTER_1 = 'BOB_CAROUSEL_FILTER_1'
BOB_CAROUSEL_FILTER_2 = 'BOB_CAROUSEL_FILTER_2'
BOB_CAROUSEL_FILTER_CLIENT_1 = 'BOB_CAROUSEL_FILTER_CLIENT_1'
STORAGE_VEHICLES_CAROUSEL_FILTER_1 = 'STORAGE_CAROUSEL_FILTER_1'
BATTLEPASS_CAROUSEL_FILTER_1 = 'BATTLEPASS_CAROUSEL_FILTER_1'
BATTLEPASS_CAROUSEL_FILTER_CLIENT_1 = 'BATTLEPASS_CAROUSEL_FILTER_CLIENT_1'
BARRACKS_FILTER = 'barracks_filter'
ORDERS_FILTER = 'ORDERS_FILTER'
CURRENT_VEHICLE = 'current'
GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
EULA_VERSION = 'EULA_VERSION'
LINKEDSET_QUESTS = 'LINKEDSET_QUEST'
FORT_MEMBER_TUTORIAL = 'FORT_MEMBER_TUTORIAL'
IGR_PROMO = 'IGR_PROMO'
PROMO = 'PROMO'
AWARDS = 'awards'
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
PROGRESSIVE_REWARD_VISITED = 'progressiveRewardVisited'
RANKED_AWARDS_COUNTER = 'rankedAwardsCounter'
RANKED_INFO_COUNTER = 'rankedInfoCounter'
BOOSTERS_FOR_CREDITS_SLOT_COUNTER = 'boostersForCreditsSlotCounter'
SENIORITY_AWARDS_COUNTER = 'seniorityAwardsCounter'
DEMOUNT_KIT_SEEN = 'demountKitSeen'
PROFILE_TECHNIQUE = 'profileTechnique'
PROFILE_TECHNIQUE_MEMBER = 'profileTechniqueMember'
SHOW_CRYSTAL_HEADER_BAND = 'showCrystalHeaderBand'
ELEN_NOTIFICATIONS = 'elenNotifications'
RECRUIT_NOTIFICATIONS = 'recruitNotifications'
SPEAKERS_DEVICE = 'speakersDevice'
SESSION_STATS_PREV_BATTLE_COUNT = 'sessionStatsPrevBattleCnt'
DEFAULT_QUEUE = 'defaultQueue'
STORE_TAB = 'store_tab'
STATS_REGULAR_SORTING = 'statsSorting'
STATS_SORTIE_SORTING = 'statsSortingSortie'
MISSIONS_PAGE = 'missions_page'
DEFAULT_VEHICLE_TYPES_FILTER = [False] * len(VEHICLE_CLASSES)
DEFAULT_LEVELS_FILTERS = [False] * MAX_VEHICLE_LEVEL
SHOW_OPT_DEVICE_HINT = 'showOptDeviceHint'
SHOW_OPT_DEVICE_HINT_TROPHY = 'showOptDeviceHintTrophy'
LAST_BADGES_VISIT = 'lastBadgesVisit'
ENABLE_RANKED_ANIMATIONS = 'enableRankedAnimations'
COLOR_SETTINGS_TAB_IDX = 'colorSettingsTabIdx'
COLOR_SETTINGS_SHOWS_COUNT = 'colorSettingsShowsCount'
APPLIED_COLOR_SETTINGS = 'appliedColorSettings'
SELECTED_QUEST_IN_REPLAY = 'SELECTED_QUEST_IN_REPLAY'
LAST_SELECTED_PM_BRANCH = 'lastSelectedPMBranch'
WHEELED_DEATH_DELAY_COUNT = 'wheeledDeathCounter'
LAST_BATTLE_PASS_POINTS_SEEN = 'lastBattlePassPointsSeen'
BATTLE_PASS_VIDEOS_CONFIG = 'battlePassVideosConfig'
ANONYMIZER = GAME.ANONYMIZER
CUSTOMIZATION_SECTION = 'customization'
PROJECTION_DECAL_TAB_SHOWN_FIELD = CUSTOMIZATION_ALIASES.PROJECTION_DECAL_TAB_SHOWN_FIELD
USER_NUMBER_TAB_SHOWN_FIELD = CUSTOMIZATION_ALIASES.USER_NUMBER_TAB_SHOWN_FIELD
CAROUSEL_ARROWS_HINT_SHOWN_FIELD = 'isCarouselsArrowsHintShown'
PROJECTION_DECAL_ONLY_ONCE_HINT_SHOWN_FIELD = 'isProjectionDecalOnlyOnceHintShown'
SESSION_STATS_SECTION = 'sessionStats'
BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD = 'battleEfficiencySectionExpanded'
SIEGE_HINT_SECTION = 'siegeModeHint'
WHEELED_MODE_HINT_SECTION = 'wheeledModeScreenHint'
TRAJECTORY_VIEW_HINT_SECTION = 'trajectoryViewHint'
PRE_BATTLE_HINT_SECTION = 'preBattleHintSection'
QUEST_PROGRESS_HINT_SECTION = 'questProgressHint'
HELP_SCREEN_HINT_SECTION = 'helpScreenHint'
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
RANKED_WEB_LEAGUE = 'rankedWebLeague'
RANKED_WEB_LEAGUE_UPDATE = 'rankedWebLeagueUpdate'
RANKED_AWARDS_BUBBLE_YEAR_REACHED = 'rankedAwardsBubbleYearReached'
MARATHON_REWARD_WAS_SHOWN_PREFIX = 'marathonRewardScreenWasShown'
MARATHON_VIDEO_WAS_SHOWN_PREFIX = 'marathonRewardVideoWasShown'
SUBTITLES = 'subtitles'
TECHTREE_INTRO_BLUEPRINTS = 'techTreeIntroBlueprints'
MODULES_ANIMATION_SHOWN = 'collectibleVehiclesAnimWasShown'
NEW_SHOP_TABS = 'newShopTabs'
IS_COLLECTIBLE_VEHICLES_VISITED = 'isCollectibleVehiclesVisited'
QUESTS = 'quests'
QUEST_DELTAS = 'questDeltas'
QUEST_DELTAS_COMPLETION = 'questCompletion'
QUEST_DELTAS_PROGRESS = 'questProgress'
QUEST_DELTAS_TOKENS_PROGRESS = 'tokensProgress'
TOP_OF_TREE_CONFIG = 'topOfTree'
TEN_YEARS_COUNTDOWN_ON_BOARDING_LAST_VISITED_BLOCK = 'tenYearsCountdownOnBoardingLastVisitedBlock'
KNOWN_SELECTOR_BATTLES = 'knownSelectorBattles'
DEFAULT_VALUES = {KEY_FILTERS: {STORE_TAB: 0,
               'shop_current': (-1, STORE_CONSTANTS.VEHICLE, False),
               'scroll_to_item': None,
               'shop_vehicle': {'obtainingType': STORE_CONSTANTS.VEHICLE,
                                'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                'selectedLevels': DEFAULT_LEVELS_FILTERS,
                                'extra': [STORE_CONSTANTS.LOCKED_EXTRA_NAME]},
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
               'shop_optionalDevice': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                       'vehicleCD': -1,
                                       'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'shop_equipment': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                  'vehicleCD': -1,
                                  'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
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
                                   'bonus': False},
               CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
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
                                          'level_10': True},
               RANKED_CAROUSEL_FILTER_2: {'premium': False,
                                          'elite': False,
                                          'igr': False,
                                          'rented': True,
                                          'event': True,
                                          'gameMode': False,
                                          'favorite': False,
                                          'bonus': False},
               RANKED_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
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
                                              'level_9': False,
                                              'level_10': False},
               EPICBATTLE_CAROUSEL_FILTER_2: {'premium': False,
                                              'elite': False,
                                              'igr': False,
                                              'rented': True,
                                              'event': True,
                                              'gameMode': False,
                                              'favorite': False,
                                              'bonus': False},
               EPICBATTLE_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
               BATTLEPASS_CAROUSEL_FILTER_1: {'isCommonProgression': False},
               BOB_CAROUSEL_FILTER_1: {'ussr': False,
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
                                       'level_10': True},
               BOB_CAROUSEL_FILTER_2: {'premium': False,
                                       'elite': False,
                                       'igr': False,
                                       'rented': True,
                                       'event': True,
                                       'gameMode': False,
                                       'favorite': False,
                                       'bonus': False},
               BOB_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
               MISSION_SELECTOR_FILTER: {'inventory': False},
               PM_SELECTOR_FILTER: {'inventory': False},
               BLUEPRINTS_STORAGE_FILTER: {'unlock_available': False,
                                           'can_convert': False},
               BARRACKS_FILTER: {'nation': -1,
                                 'role': 'None',
                                 'tankType': 'None',
                                 'location': 3,
                                 'nationID': None},
               ORDERS_FILTER: {'isSelected': False},
               GUI_START_BEHAVIOR: {'isFreeXPInfoDialogShowed': False,
                                    'isRankedWelcomeViewShowed': False,
                                    'isRankedWelcomeViewStarted': False,
                                    'isEpicRandomCheckboxClicked': False,
                                    'isEpicWelcomeViewShowed': False,
                                    'lastShownEpicWelcomeScreen': 0,
                                    'techTreeIntroBlueprintsReceived': False,
                                    'techTreeIntroShowed': False},
               EULA_VERSION: {'version': 0},
               LINKEDSET_QUESTS: {'shown': 0},
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
               'linkedset_view_vehicle': {'nation': -1,
                                          'vehicleType': 'none'},
               'epic_rent_view_vehicle': {'nation': -1,
                                          'vehicleType': 'none',
                                          'isMain': False,
                                          'level': -1,
                                          'compatibleOnly': True},
               PROMO: {},
               AWARDS: {'vehicleResearchAward': -1,
                        'victoryAward': -1,
                        'battlesCountAward': -1,
                        'pveBattlesCountAward': -1},
               PROFILE_TECHNIQUE: {'selectedColumn': 4,
                                   'selectedColumnSorting': 'descending',
                                   'isInHangarSelected': False},
               PROFILE_TECHNIQUE_MEMBER: {'selectedColumn': 4,
                                          'selectedColumnSorting': 'descending'},
               SPEAKERS_DEVICE: 0},
 KEY_FAVORITES: {CURRENT_VEHICLE: 0,
                 FALLOUT_VEHICLES: {}},
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
                'markers': {'ally': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': False,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 0,
                                     'markerBaseVehicleName': False,
                                     'markerBasePlayerName': True,
                                     'markerBaseAimMarker2D': False,
                                     'markerAltIcon': True,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': True,
                                     'markerAltPlayerName': False,
                                     'markerAltAimMarker2D': False},
                            'enemy': {'markerBaseIcon': False,
                                      'markerBaseLevel': False,
                                      'markerBaseHpIndicator': False,
                                      'markerBaseDamage': True,
                                      'markerBaseHp': 0,
                                      'markerBaseVehicleName': False,
                                      'markerBasePlayerName': True,
                                      'markerBaseAimMarker2D': True,
                                      'markerAltIcon': True,
                                      'markerAltLevel': True,
                                      'markerAltHpIndicator': True,
                                      'markerAltDamage': True,
                                      'markerAltHp': 1,
                                      'markerAltVehicleName': True,
                                      'markerAltPlayerName': False,
                                      'markerAltAimMarker2D': True},
                            'dead': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': False,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 0,
                                     'markerBaseVehicleName': False,
                                     'markerBasePlayerName': True,
                                     'markerBaseAimMarker2D': False,
                                     'markerAltIcon': True,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': True,
                                     'markerAltPlayerName': False,
                                     'markerAltAimMarker2D': False}},
                'showVehicleIcon': False,
                'showVehicleLevel': False,
                'showExInf4Destroyed': False,
                'ingameHelpVersion': -1,
                'isColorBlind': False,
                'useServerAim': False,
                'showDamageIcon': True,
                'showVehiclesCounter': True,
                'minimapAlpha': 0,
                'minimapSize': 1,
                'minimapRespawnSize': 0,
                'minimapViewRange': True,
                'minimapMaxViewRange': True,
                'minimapDrawRange': True,
                'minimapAlphaEnabled': False,
                'epicMinimapZoom': 1.5,
                'increasedZoom': True,
                'sniperModeByShift': True,
                'nationalVoices': False,
                'enableVoIP': True,
                'replayEnabled': 1,
                'hangarCamPeriod': 1,
                'hangarCamParallaxEnabled': True,
                'players_panel': {'state': 2,
                                  'showLevels': True,
                                  'showTypes': True},
                'epic_random_players_panel': {'state': 5},
                'gameplayMask': gameplay_ctx.getDefaultMask(),
                'statsSorting': {'iconType': 'tank',
                                 'sortDirection': 'descending'},
                'statsSortingSortie': {'iconType': 'tank',
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
                CUSTOMIZATION_SECTION: {},
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
                DEFAULT_QUEUE: constants.QUEUE_TYPE.SANDBOX,
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
                'bulbVoices': 'lightbulb',
                PREVIEW_INFO_PANEL_IDX: 0,
                'carouselType': 0,
                'doubleCarouselType': 0,
                'vehicleCarouselStats': True,
                WHEELED_DEATH_DELAY_COUNT: 10,
                NEW_SETTINGS_COUNTER: {'GameSettings': {'gameplay_epicStandard': True,
                                                        'c11nHistoricallyAccurate': True,
                                                        'hangarCamParallaxEnabled': True,
                                                        'hangarCamPeriod': True,
                                                        'showDamageIcon': True,
                                                        ANONYMIZER: True,
                                                        GAME.DISABLE_EVENT_COMMON_CHAT: True},
                                       'GraphicSettings': {'ScreenSettings': {'gammaSetting': True,
                                                                              'colorFilter': True},
                                                           'AdvancedGraphicSettings': {'HAVOK_ENABLED': True,
                                                                                       'TERRAIN_TESSELLATION_ENABLED': True,
                                                                                       'SNIPER_MODE_TERRAIN_TESSELLATION_ENABLED': True}},
                                       'FeedbackSettings': {'feedbackBattleBorderMap': {'battleBorderMapType': True,
                                                                                        'battleBorderMapMode': True},
                                                            'feedbackQuestsProgress': {'progressViewType': True,
                                                                                       'progressViewConditions': True},
                                                            'feedbackDamageIndicator': {'damageIndicatorAllies': True}},
                                       'ControlsSettings': {'showQuestProgress': True,
                                                            'chargeFire': True}},
                SHOW_OPT_DEVICE_HINT: True,
                SHOW_OPT_DEVICE_HINT_TROPHY: True,
                'c11nHistoricallyAccurate': True,
                LAST_BADGES_VISIT: 0,
                ENABLE_RANKED_ANIMATIONS: True,
                COLOR_SETTINGS_TAB_IDX: 0,
                COLOR_SETTINGS_SHOWS_COUNT: 0,
                SELECTED_QUEST_IN_REPLAY: None,
                APPLIED_COLOR_SETTINGS: {},
                LAST_SELECTED_PM_BRANCH: 0,
                TRAJECTORY_VIEW_HINT_SECTION: {HINTS_LEFT: 3,
                                               LAST_DISPLAY_DAY: 0,
                                               NUM_BATTLES: 0},
                PRE_BATTLE_HINT_SECTION: {QUEST_PROGRESS_HINT_SECTION: {HINTS_LEFT: 3,
                                                                        LAST_DISPLAY_DAY: 0,
                                                                        NUM_BATTLES: 0},
                                          HELP_SCREEN_HINT_SECTION: {}},
                WATCHED_PRE_BATTLE_TIPS_SECTION: {},
                SIEGE_HINT_SECTION: {HINTS_LEFT: 3,
                                     LAST_DISPLAY_DAY: 0,
                                     NUM_BATTLES: 0},
                WHEELED_MODE_HINT_SECTION: {HINTS_LEFT: 3,
                                            LAST_DISPLAY_DAY: 0,
                                            NUM_BATTLES: 0},
                CREW_SKINS_VIEWED: set(),
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
                RANKED_WEB_LEAGUE: None,
                RANKED_WEB_LEAGUE_UPDATE: None,
                RANKED_AWARDS_BUBBLE_YEAR_REACHED: False,
                NATION_CHANGE_VIEWED: False,
                LAST_BATTLE_PASS_POINTS_SEEN: 0,
                BATTLE_PASS_VIDEOS_CONFIG: {},
                TECHTREE_INTRO_BLUEPRINTS: {},
                MODULES_ANIMATION_SHOWN: False,
                SUBTITLES: True,
                NATION_CHANGE_VIEWED: False,
                TOP_OF_TREE_CONFIG: {},
                TEN_YEARS_COUNTDOWN_ON_BOARDING_LAST_VISITED_BLOCK: 0},
 KEY_COUNTERS: {NEW_HOF_COUNTER: {PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON: True},
                NEW_LOBBY_TAB_COUNTER: {},
                REFERRAL_COUNTER: 1,
                RANKED_AWARDS_COUNTER: 1,
                RANKED_INFO_COUNTER: 1,
                BOOSTERS_FOR_CREDITS_SLOT_COUNTER: 1,
                SENIORITY_AWARDS_COUNTER: 1,
                DEMOUNT_KIT_SEEN: False,
                NEW_SHOP_TABS: {IS_COLLECTIBLE_VEHICLES_VISITED: False}},
 KEY_NOTIFICATIONS: {ELEN_NOTIFICATIONS: {MISSIONS_CONSTANTS.ELEN_EVENT_STARTED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_FINISHED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_TAB_VISITED: set()},
                     RECRUIT_NOTIFICATIONS: set(),
                     PROGRESSIVE_REWARD_VISITED: False},
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
                                                             'searchNameVehicle': ''},
                        'storage_shells': {'filterMask': 0,
                                           'vehicleCD': None},
                        'storage_crew_books': {'filterMask': 0,
                                               'nationID': nations.NONE_INDEX},
                        'storage_consumables_tab': {'filterMask': 0},
                        'storage_modules': {'filterMask': 0,
                                            'vehicleCD': None},
                        'storage_reserves': {'filterMask': 0},
                        LAST_STORAGE_VISITED_TIMESTAMP: -1,
                        SESSION_STATS_PREV_BATTLE_COUNT: 0},
 KEY_UI_FLAGS: {}}

def _filterAccountSection(dataSec):
    for key, section in dataSec.items()[:]:
        if key == 'account':
            yield (key, section)


def _pack(value):
    return base64.b64encode(pickle.dumps(value))


def _unpack(value):
    return pickle.loads(base64.b64decode(value))


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
    version = 40
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
        userLogin = getattr(BigWorld.player(), 'name', '')
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
                        if filterName in ('shop_vehicle', 'shop_module', 'shop_shell', 'shop_optionalDevice', 'shop_equipment', 'inventory_vehicle', 'inventory_module', 'inventory_shell', 'inventory_optionalDevice', 'inventory_equipment'):
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
                        if filterName in ('shop_vehicle', 'inventory_vehicle', 'shop_current', 'inventory_current', 'shop_tradeInVehicle', 'shop_restoreVehicle'):
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
                cmSection = AccountSettings._readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
                for command, section in cmSection.items()[:]:
                    newSection = None
                    fireKey = AccountSettings._readSection(section, 'fireKey').asString
                    if fireKey == 'KEY_N':
                        if command == 'CMD_QUEST_PROGRESS_SHOW':
                            pass
                        else:
                            newSection = cmSection.createSection('CMD_QUEST_PROGRESS_SHOW')
                    if newSection is not None:
                        newSection.writeString('fireKey', 'KEY_NONE')

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
                newSettingsCounters = AccountSettings.updateNewSettingsCounter(currentDefaults, savedNewSettingsCounters)
                accSettings.write(NEW_SETTINGS_COUNTER, _pack(newSettingsCounters))

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

    @staticmethod
    def _getValue(name, setting, force=False):
        fds = AccountSettings._readSection(AccountSettings._readUserSection(), setting)
        try:
            if fds.has_key(name):
                return pickle.loads(base64.b64decode(fds.readString(name)))
        except Exception:
            if constants.IS_DEVELOPMENT:
                LOG_CURRENT_EXCEPTION()

        return copy.deepcopy(DEFAULT_VALUES[setting][name]) if name in DEFAULT_VALUES[setting] else None

    @staticmethod
    def _setValue(name, value, setting, force=False):
        if name not in DEFAULT_VALUES[setting] and not force:
            raise SoftException('Default value "{}" is not found in "{}"'.format(name, type))
        if AccountSettings._getValue(name, setting, force) != value:
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
        userLogin = getattr(BigWorld.player(), 'name', '')
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
