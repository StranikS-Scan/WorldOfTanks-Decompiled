# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/ServerSettingsManager.py
import weakref
from collections import namedtuple
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.migrations import migrateToVersion
from account_helpers.settings_core.settings_constants import TUTORIAL, VERSION, GuiSettingsBehavior, OnceOnlyHints, SPGAim, CONTOUR
from adisp import adisp_process, adisp_async
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.battle_pass.battle_pass_helpers import updateBattlePassSettings
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCache
GUI_START_BEHAVIOR = 'guiStartBehavior'

class SETTINGS_SECTIONS(CONST_CONTAINER):
    GAME = 'GAME'
    GAME_EXTENDED = 'GAME_EXTENDED'
    GAME_EXTENDED_2 = 'GAME_EXTENDED_2'
    GAMEPLAY = 'GAMEPLAY'
    GRAPHICS = 'GRAPHICS'
    SOUND = 'SOUND'
    CONTROLS = 'CONTROLS'
    AIM_1 = 'AIM_1'
    AIM_2 = 'AIM_2'
    AIM_3 = 'AIM_3'
    AIM_4 = 'AIM_4'
    MARKERS = 'MARKERS'
    CAROUSEL_FILTER_1 = 'CAROUSEL_FILTER_1'
    CAROUSEL_FILTER_2 = 'CAROUSEL_FILTER_2'
    RANKED_CAROUSEL_FILTER_1 = 'RANKED_CAROUSEL_FILTER_1'
    RANKED_CAROUSEL_FILTER_2 = 'RANKED_CAROUSEL_FILTER_2'
    ROYALE_CAROUSEL_FILTER_1 = 'ROYALE_CAROUSEL_FILTER_1'
    ROYALE_CAROUSEL_FILTER_2 = 'ROYALE_CAROUSEL_FILTER_2'
    EPICBATTLE_CAROUSEL_FILTER_1 = 'EPICBATTLE_CAROUSEL_FILTER_1'
    EPICBATTLE_CAROUSEL_FILTER_2 = 'EPICBATTLE_CAROUSEL_FILTER_2'
    BATTLEPASS_CAROUSEL_FILTER_1 = 'BATTLEPASS_CAROUSEL_FILTER_1'
    MAPBOX_CAROUSEL_FILTER_1 = 'MAPBOX_CAROUSEL_FILTER_1'
    MAPBOX_CAROUSEL_FILTER_2 = 'MAPBOX_CAROUSEL_FILTER_2'
    FUN_RANDOM_CAROUSEL_FILTER_1 = 'FUN_RANDOM_CAROUSEL_FILTER_1'
    FUN_RANDOM_CAROUSEL_FILTER_2 = 'FUN_RANDOM_CAROUSEL_FILTER_2'
    COMP7_CAROUSEL_FILTER_1 = 'COMP7_CAROUSEL_FILTER_1'
    COMP7_CAROUSEL_FILTER_2 = 'COMP7_CAROUSEL_FILTER_2'
    GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
    EULA_VERSION = 'EULA_VERSION'
    MARKS_ON_GUN = 'MARKS_ON_GUN'
    CONTACTS = 'CONTACTS'
    FALLOUT = 'FALLOUT'
    TUTORIAL = 'TUTORIAL'
    ONCE_ONLY_HINTS = 'ONCE_ONLY_HINTS'
    ONCE_ONLY_HINTS_2 = 'ONCE_ONLY_HINTS_2'
    FEEDBACK = 'FEEDBACK'
    DAMAGE_INDICATOR = 'FEEDBACK_DAMAGE_INDICATOR'
    DAMAGE_LOG = 'FEEDBACK_DAMAGE_LOG'
    BATTLE_EVENTS = 'FEEDBACK_BATTLE_EVENTS'
    BATTLE_BORDER_MAP = 'FEEDBACK_BORDER_MAP'
    QUESTS_PROGRESS = 'QUESTS_PROGRESS'
    UI_STORAGE = 'UI_STORAGE'
    UI_STORAGE_2 = 'UI_STORAGE_2'
    BATTLE_MATTERS_QUESTS = 'BATTLE_MATTERS_QUESTS'
    SESSION_STATS = 'SESSION_STATS'
    BATTLE_PASS_STORAGE = 'BATTLE_PASS_STORAGE'
    BATTLE_COMM = 'BATTLE_COMM'
    DOG_TAGS = 'DOG_TAGS'
    UNIT_FILTER = 'UNIT_FILTER'
    BATTLE_HUD = 'BATTLE_HUD'
    SPG_AIM = 'SPG_AIM'
    CONTOUR = 'CONTOUR'
    ONCE_ONLY_HINTS_GROUP = (ONCE_ONLY_HINTS, ONCE_ONLY_HINTS_2)


class UI_STORAGE_KEYS(CONST_CONTAINER):
    AUTO_RELOAD_HIGHLIGHTS_COUNTER = 'auto_reload_highlights_count'
    AUTO_RELOAD_MARK_IS_SHOWN = 'auto_reload_mark_shown'
    DISABLE_ANIMATED_TOOLTIP = 'disable_animated_tooltip'
    FIELD_POST_HINT_IS_SHOWN = 'field_post_hint'
    REFERRAL_BUTTON_CIRCLES_SHOWN = 'referral_button_circles_shown'
    DUAL_GUN_HIGHLIGHTS_COUNTER = 'dual_gun_highlights_count'
    DUAL_GUN_MARK_IS_SHOWN = 'dual_gun_mark_shown'
    DISABLE_EDITABLE_STYLE_REWRITE_WARNING = 'disable_editable_style_rewrite_warning'
    OPTIONAL_DEVICE_SETUP_INTRO_SHOWN = 'optional_device_setup_intro_shown'
    TURBOSHAFT_HIGHLIGHTS_COUNTER = 'turboshaft_highlights_count'
    ROCKET_ACCELERATION_HIGHLIGHTS_COUNTER = 'rocket_acceleration_highlights_count'
    TURBOSHAFT_MARK_IS_SHOWN = 'turboshaft_mark_shown'
    ROCKET_ACCELERATION_MARK_IS_SHOWN = 'rocket_acceleration_mark_shown'
    EPIC_BATTLE_ABILITIES_INTRO_SHOWN = 'epic_battle_abilities_intro_shown'
    POST_PROGRESSION_INTRO_SHOWN = 'post_progression_intro_shown'
    VEH_PREVIEW_POST_PROGRESSION_BULLET_SHOWN = 'veh_preview_post_progression_bullet_shown'


class ServerSettingsManager(object):
    settingsCache = dependency.descriptor(ISettingsCache)
    GAME = settings_constants.GAME
    GRAPHICS = settings_constants.GRAPHICS
    SOUND = settings_constants.SOUND
    CONTROLS = settings_constants.CONTROLS
    Section = namedtuple('Section', ['masks', 'offsets'])
    Offset = namedtuple('Offset', ['offset', 'mask'])
    CONTACTS = settings_constants.CONTACTS
    DAMAGE_INDICATOR = settings_constants.DAMAGE_INDICATOR
    DAMAGE_LOG = settings_constants.DAMAGE_LOG
    BATTLE_EVENTS = settings_constants.BATTLE_EVENTS
    BATTLE_BORDER_MAP = settings_constants.BATTLE_BORDER_MAP
    QUESTS_PROGRESS = settings_constants.QUESTS_PROGRESS
    SESSION_STATS = settings_constants.SESSION_STATS
    BATTLE_COMM = settings_constants.BattleCommStorageKeys
    BATTLE_PASS = settings_constants.BattlePassStorageKeys
    SCORE_PANEL = settings_constants.ScorePanelStorageKeys
    SECTIONS = {SETTINGS_SECTIONS.GAME: Section(masks={GAME.ENABLE_OL_FILTER: 0,
                              GAME.ENABLE_SPAM_FILTER: 1,
                              GAME.INVITES_FROM_FRIENDS: 2,
                              GAME.STORE_RECEIVER_IN_BATTLE: 3,
                              GAME.PLAYERS_PANELS_SHOW_LEVELS: 4,
                              GAME.SHOW_DAMAGE_ICON: 5,
                              GAME.DYNAMIC_CAMERA: 6,
                              GAME.ENABLE_POSTMORTEM_DELAY: 7,
                              GAME.ENABLE_SERVER_AIM: 8,
                              GAME.SHOW_VEHICLES_COUNTER: 9,
                              GAME.SHOW_VECTOR_ON_MAP: 10,
                              GAME.SHOW_SECTOR_ON_MAP: 11,
                              GAME.RECEIVE_FRIENDSHIP_REQUEST: 12,
                              GAME.SNIPER_MODE_STABILIZATION: 13,
                              GAME.DISABLE_BATTLE_CHAT: 28}, offsets={GAME.REPLAY_ENABLED: Offset(14, 49152),
                              GAME.DATE_TIME_MESSAGE_INDEX: Offset(16, 983040),
                              GAME.MINIMAP_ALPHA: Offset(20, 267386880),
                              GAME.SHOW_VEH_MODELS_ON_MAP: Offset(29, 1610612736)}),
     SETTINGS_SECTIONS.GAME_EXTENDED: Section(masks={GAME.PRE_COMMANDER_CAM: 0,
                                       GAME.CHAT_CONTACTS_LIST_ONLY: 1,
                                       GAME.RECEIVE_INVITES_IN_BATTLE: 2,
                                       GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS: 3,
                                       GAME.MINIMAP_VIEW_RANGE: 6,
                                       GAME.MINIMAP_MAX_VIEW_RANGE: 7,
                                       GAME.MINIMAP_DRAW_RANGE: 8,
                                       GAME.INCREASED_ZOOM: 9,
                                       GAME.SNIPER_MODE_BY_SHIFT: 10,
                                       GAME.COMMANDER_CAM: 11,
                                       GAME.CAROUSEL_TYPE: 12,
                                       GAME.DOUBLE_CAROUSEL_TYPE: 13,
                                       GAME.VEHICLE_CAROUSEL_STATS: 14,
                                       GAME.MINIMAP_ALPHA_ENABLED: 15,
                                       GAME.HANGAR_CAM_PARALLAX_ENABLED: 16,
                                       GAME.ENABLE_SPEEDOMETER: 23,
                                       GAME.DISPLAY_PLATOON_MEMBERS: 24,
                                       GAME.MINIMAP_MIN_SPOTTING_RANGE: 25,
                                       GAME.ENABLE_REPAIR_TIMER: 26,
                                       GAME.ENABLE_BATTLE_NOTIFIER: 29,
                                       GAME.HULLLOCK_ENABLED: 30}, offsets={GAME.BATTLE_LOADING_INFO: Offset(4, 48),
                                       GAME.BATTLE_LOADING_RANKED_INFO: Offset(21, 6291456),
                                       GAME.HANGAR_CAM_PERIOD: Offset(18, 1835008),
                                       GAME.SNIPER_ZOOM: Offset(27, 402653184)}),
     SETTINGS_SECTIONS.GAME_EXTENDED_2: Section(masks={GAME.SHOW_ARTY_HIT_ON_MAP: 0,
                                         GAME.GAMEPLAY_ONLY_10_MODE: 1,
                                         GAME.SCROLL_SMOOTHING: 4}, offsets={GAME.CUSTOMIZATION_DISPLAY_TYPE: Offset(2, 12)}),
     SETTINGS_SECTIONS.GAMEPLAY: Section(masks={}, offsets={GAME.GAMEPLAY_MASK: Offset(0, 65535)}),
     SETTINGS_SECTIONS.GRAPHICS: Section(masks={GAME.LENS_EFFECT: 1}, offsets={}),
     SETTINGS_SECTIONS.SOUND: Section(masks={}, offsets={SOUND.ALT_VOICES: Offset(0, 255)}),
     SETTINGS_SECTIONS.CONTROLS: Section(masks={CONTROLS.MOUSE_HORZ_INVERSION: 0,
                                  CONTROLS.MOUSE_VERT_INVERSION: 1,
                                  CONTROLS.BACK_DRAFT_INVERSION: 2}, offsets={}),
     SETTINGS_SECTIONS.AIM_1: Section(masks={}, offsets={'net': Offset(0, 255),
                               'netType': Offset(8, 65280),
                               'centralTag': Offset(16, 16711680),
                               'centralTagType': Offset(24, 4278190080L)}),
     SETTINGS_SECTIONS.AIM_2: Section(masks={}, offsets={'reloader': Offset(0, 255),
                               'condition': Offset(8, 65280),
                               'mixing': Offset(16, 16711680),
                               'mixingType': Offset(24, 4278190080L)}),
     SETTINGS_SECTIONS.AIM_3: Section(masks={}, offsets={'cassette': Offset(0, 255),
                               'gunTag': Offset(8, 65280),
                               'gunTagType': Offset(16, 16711680),
                               'reloaderTimer': Offset(24, 4278190080L)}),
     SETTINGS_SECTIONS.AIM_4: Section(masks={}, offsets={'zoomIndicator': Offset(0, 255)}),
     SETTINGS_SECTIONS.SPG_AIM: Section(masks={SPGAim.SHOTS_RESULT_INDICATOR: 0,
                                 SPGAim.SPG_SCALE_WIDGET: 1,
                                 SPGAim.SPG_STRATEGIC_CAM_MODE: 2,
                                 SPGAim.AUTO_CHANGE_AIM_MODE: 3}, offsets={SPGAim.AIM_ENTRANCE_MODE: Offset(4, 48)}),
     SETTINGS_SECTIONS.CONTOUR: Section(masks={CONTOUR.ENHANCED_CONTOUR: 0}, offsets={CONTOUR.CONTOUR_PENETRABLE_ZONE: Offset(1, 6),
                                 CONTOUR.CONTOUR_IMPENETRABLE_ZONE: Offset(3, 24)}),
     SETTINGS_SECTIONS.MARKERS: Section(masks={'markerBaseIcon': 0,
                                 'markerBaseLevel': 1,
                                 'markerBaseHpIndicator': 2,
                                 'markerBaseDamage': 3,
                                 'markerBaseVehicleName': 4,
                                 'markerBasePlayerName': 5,
                                 'markerBaseAimMarker2D': 6,
                                 'markerAltIcon': 16,
                                 'markerAltLevel': 17,
                                 'markerAltHpIndicator': 18,
                                 'markerAltDamage': 19,
                                 'markerAltVehicleName': 20,
                                 'markerAltPlayerName': 21,
                                 'markerAltAimMarker2D': 22}, offsets={'markerBaseHp': Offset(8, 65280),
                                 'markerAltHp': Offset(24, 4278190080L)}),
     SETTINGS_SECTIONS.CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                           'germany': 1,
                                           'usa': 2,
                                           'china': 3,
                                           'france': 4,
                                           'uk': 5,
                                           'japan': 6,
                                           'czech': 7,
                                           'sweden': 8,
                                           'poland': 9,
                                           'italy': 10,
                                           'lightTank': 15,
                                           'mediumTank': 16,
                                           'heavyTank': 17,
                                           'SPG': 18,
                                           'AT-SPG': 19,
                                           'level_1': 20,
                                           'level_2': 21,
                                           'level_3': 22,
                                           'level_4': 23,
                                           'level_5': 24,
                                           'level_6': 25,
                                           'level_7': 26,
                                           'level_8': 27,
                                           'level_9': 28,
                                           'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                           'elite': 1,
                                           'rented': 2,
                                           'igr': 3,
                                           'favorite': 5,
                                           'bonus': 6,
                                           'event': 7,
                                           'crystals': 8,
                                           'role_HT_assault': 11,
                                           'role_HT_break': 12,
                                           'role_HT_support': 13,
                                           'role_HT_universal': 14,
                                           'role_MT_universal': 15,
                                           'role_MT_sniper': 16,
                                           'role_MT_assault': 17,
                                           'role_MT_support': 18,
                                           'role_ATSPG_assault': 19,
                                           'role_ATSPG_universal': 20,
                                           'role_ATSPG_sniper': 21,
                                           'role_ATSPG_support': 22,
                                           'role_LT_universal': 23,
                                           'role_LT_wheeled': 24,
                                           'role_SPG': 25}, offsets={}),
     SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                  'germany': 1,
                                                  'usa': 2,
                                                  'china': 3,
                                                  'france': 4,
                                                  'uk': 5,
                                                  'japan': 6,
                                                  'czech': 7,
                                                  'sweden': 8,
                                                  'poland': 9,
                                                  'italy': 10,
                                                  'lightTank': 15,
                                                  'mediumTank': 16,
                                                  'heavyTank': 17,
                                                  'SPG': 18,
                                                  'AT-SPG': 19,
                                                  'level_1': 20,
                                                  'level_2': 21,
                                                  'level_3': 22,
                                                  'level_4': 23,
                                                  'level_5': 24,
                                                  'level_6': 25,
                                                  'level_7': 26,
                                                  'level_8': 27,
                                                  'level_9': 28,
                                                  'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                  'elite': 1,
                                                  'rented': 2,
                                                  'igr': 3,
                                                  'gameMode': 4,
                                                  'favorite': 5,
                                                  'bonus': 6,
                                                  'event': 7,
                                                  'crystals': 8,
                                                  'ranked': 9,
                                                  'role_HT_assault': 11,
                                                  'role_HT_break': 12,
                                                  'role_HT_support': 13,
                                                  'role_HT_universal': 14,
                                                  'role_MT_universal': 15,
                                                  'role_MT_sniper': 16,
                                                  'role_MT_assault': 17,
                                                  'role_MT_support': 18,
                                                  'role_ATSPG_assault': 19,
                                                  'role_ATSPG_universal': 20,
                                                  'role_ATSPG_sniper': 21,
                                                  'role_ATSPG_support': 22,
                                                  'role_LT_universal': 23,
                                                  'role_LT_wheeled': 24,
                                                  'role_SPG': 25}, offsets={}),
     SETTINGS_SECTIONS.EPICBATTLE_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                      'germany': 1,
                                                      'usa': 2,
                                                      'china': 3,
                                                      'france': 4,
                                                      'uk': 5,
                                                      'japan': 6,
                                                      'czech': 7,
                                                      'sweden': 8,
                                                      'poland': 9,
                                                      'italy': 10,
                                                      'lightTank': 15,
                                                      'mediumTank': 16,
                                                      'heavyTank': 17,
                                                      'SPG': 18,
                                                      'AT-SPG': 19,
                                                      'level_1': 20,
                                                      'level_2': 21,
                                                      'level_3': 22,
                                                      'level_4': 23,
                                                      'level_5': 24,
                                                      'level_6': 25,
                                                      'level_7': 26,
                                                      'level_8': 27,
                                                      'level_9': 28,
                                                      'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.EPICBATTLE_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                      'elite': 1,
                                                      'rented': 2,
                                                      'igr': 3,
                                                      'gameMode': 4,
                                                      'favorite': 5,
                                                      'bonus': 6,
                                                      'event': 7,
                                                      'crystals': 8,
                                                      'role_HT_assault': 11,
                                                      'role_HT_break': 12,
                                                      'role_HT_support': 13,
                                                      'role_HT_universal': 14,
                                                      'role_MT_universal': 15,
                                                      'role_MT_sniper': 16,
                                                      'role_MT_assault': 17,
                                                      'role_MT_support': 18,
                                                      'role_ATSPG_assault': 19,
                                                      'role_ATSPG_universal': 20,
                                                      'role_ATSPG_sniper': 21,
                                                      'role_ATSPG_support': 22,
                                                      'role_LT_universal': 23,
                                                      'role_LT_wheeled': 24,
                                                      'role_SPG': 25}, offsets={}),
     SETTINGS_SECTIONS.BATTLEPASS_CAROUSEL_FILTER_1: Section(masks={'isCommonProgression': 0}, offsets={}),
     SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                 'germany': 1,
                                                 'usa': 2,
                                                 'china': 3,
                                                 'france': 4,
                                                 'uk': 5,
                                                 'japan': 6,
                                                 'czech': 7,
                                                 'sweden': 8,
                                                 'poland': 9,
                                                 'italy': 10,
                                                 'lightTank': 15,
                                                 'mediumTank': 16,
                                                 'heavyTank': 17,
                                                 'SPG': 18,
                                                 'AT-SPG': 19,
                                                 'level_1': 20,
                                                 'level_2': 21,
                                                 'level_3': 22,
                                                 'level_4': 23,
                                                 'level_5': 24,
                                                 'level_6': 25,
                                                 'level_7': 26,
                                                 'level_8': 27,
                                                 'level_9': 28,
                                                 'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                 'elite': 1,
                                                 'rented': 2,
                                                 'igr': 3,
                                                 'gameMode': 4,
                                                 'favorite': 5,
                                                 'bonus': 6,
                                                 'event': 7,
                                                 'crystals': 8,
                                                 'comp7': 9,
                                                 'role_HT_assault': 11,
                                                 'role_HT_break': 12,
                                                 'role_HT_support': 13,
                                                 'role_HT_universal': 14,
                                                 'role_MT_universal': 15,
                                                 'role_MT_sniper': 16,
                                                 'role_MT_assault': 17,
                                                 'role_MT_support': 18,
                                                 'role_ATSPG_assault': 19,
                                                 'role_ATSPG_universal': 20,
                                                 'role_ATSPG_sniper': 21,
                                                 'role_ATSPG_support': 22,
                                                 'role_LT_universal': 23,
                                                 'role_LT_wheeled': 24,
                                                 'role_SPG': 25}, offsets={}),
     SETTINGS_SECTIONS.GUI_START_BEHAVIOR: Section(masks={GuiSettingsBehavior.FREE_XP_INFO_DIALOG_SHOWED: 0,
                                            GuiSettingsBehavior.RANKED_WELCOME_VIEW_SHOWED: 1,
                                            GuiSettingsBehavior.RANKED_WELCOME_VIEW_STARTED: 2,
                                            GuiSettingsBehavior.EPIC_RANDOM_CHECKBOX_CLICKED: 3,
                                            GuiSettingsBehavior.DISPLAY_PLATOON_MEMBER_CLICKED: 25,
                                            GuiSettingsBehavior.VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW: 26,
                                            GuiSettingsBehavior.BIRTHDAY_CALENDAR_INTRO_SHOWED: 27,
                                            GuiSettingsBehavior.RESOURCE_WELL_INTRO_SHOWN: 28,
                                            GuiSettingsBehavior.CREW_LAMP_WELCOME_SCREEN_SHOWN: 29,
                                            GuiSettingsBehavior.COMP7_INTRO_SHOWN: 30}, offsets={}),
     SETTINGS_SECTIONS.EULA_VERSION: Section(masks={}, offsets={'version': Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.MARKS_ON_GUN: Section(masks={}, offsets={GAME.SHOW_MARKS_ON_GUN: Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.CONTACTS: Section(masks={CONTACTS.SHOW_OFFLINE_USERS: 0,
                                  CONTACTS.SHOW_OTHERS_CATEGORY: 1}, offsets={CONTACTS.ANTISPAM_MESSAGES_COUNTER: Offset(2, 28)}),
     SETTINGS_SECTIONS.FALLOUT: Section(masks={'isEnabled': 3,
                                 'isAutomatch': 4,
                                 'hasVehicleLvl8': 5,
                                 'hasVehicleLvl10': 6}, offsets={'falloutBattleType': Offset(8, 65280)}),
     SETTINGS_SECTIONS.TUTORIAL: Section(masks={TUTORIAL.CUSTOMIZATION: 0,
                                  TUTORIAL.TECHNICAL_MAINTENANCE: 1,
                                  TUTORIAL.PERSONAL_CASE: 2,
                                  TUTORIAL.RESEARCH: 3,
                                  TUTORIAL.RESEARCH_TREE: 4,
                                  TUTORIAL.MEDKIT_USED: 6,
                                  TUTORIAL.REPAIRKIT_USED: 8,
                                  TUTORIAL.FIRE_EXTINGUISHER_USED: 10,
                                  TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED: 11}, offsets={}),
     SETTINGS_SECTIONS.ONCE_ONLY_HINTS: Section(masks={OnceOnlyHints.FALLOUT_QUESTS_TAB: 0,
                                         OnceOnlyHints.C11N_PROGRESSION_VIEW_HINT: 1,
                                         OnceOnlyHints.SHOP_TRADE_IN_HINT: 2,
                                         OnceOnlyHints.VEH_COMPARE_CONFIG_HINT: 3,
                                         OnceOnlyHints.HOLD_SHEET_HINT: 4,
                                         OnceOnlyHints.HAVE_NEW_BADGE_HINT: 5,
                                         OnceOnlyHints.EPIC_RESERVES_SLOT_HINT: 6,
                                         OnceOnlyHints.SHOW_ABILITIES_BUTTON_HINT: 7,
                                         OnceOnlyHints.PAUSE_HINT: 8,
                                         OnceOnlyHints.HAVE_NEW_SUFFIX_BADGE_HINT: 9,
                                         OnceOnlyHints.BADGE_PAGE_NEW_SUFFIX_BADGE_HINT: 10,
                                         OnceOnlyHints.C11N_AUTOPROLONGATION_HINT: 11,
                                         OnceOnlyHints.BLUEPRINTS_SWITCHBUTTON_HINT: 12,
                                         OnceOnlyHints.BLUEPRINTS_RESEARCH_BUTTON_HINT: 13,
                                         OnceOnlyHints.BLUEPRINTS_TECHTREE_CONVERT_BUTTON_HINT: 14,
                                         OnceOnlyHints.BLUEPRINTS_RESEARCH_CONVERT_BUTTON_HINT: 15,
                                         OnceOnlyHints.BLUEPRINT_SCREEN_CONVERT_FRAGMENT_HINT: 16,
                                         OnceOnlyHints.ACCOUNT_BUTTON_HINT: 17,
                                         OnceOnlyHints.SESSION_STATS_OPEN_BTN_HINT: 18,
                                         OnceOnlyHints.BATTLE_SESSION_UP_BUTTON_TOURNAMENT_HINT: 19,
                                         OnceOnlyHints.CREW_OPERATION_BTN_HINT: 20,
                                         OnceOnlyHints.SOUND_BUTTONEX_HINT: 21,
                                         OnceOnlyHints.SESSION_STATS_SETTINGS_BTN_HINT: 22,
                                         OnceOnlyHints.VEHICLE_PREVIEW_MODULES_BUTTON_HINT: 23,
                                         OnceOnlyHints.C11N_EDITABLE_STYLES_HINT: 24,
                                         OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT: 25,
                                         OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT: 26,
                                         OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT: 27,
                                         OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT: 28,
                                         OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT: 29,
                                         OnceOnlyHints.CRYSTAL_BTN_HINT: 30}, offsets={}),
     SETTINGS_SECTIONS.ONCE_ONLY_HINTS_2: Section(masks={OnceOnlyHints.AMMUNITION_PANEL_HINT: 0,
                                           OnceOnlyHints.AMMUNITION_FILTER_HINT: 1,
                                           OnceOnlyHints.OPT_DEV_DRAG_AND_DROP_HINT: 2,
                                           OnceOnlyHints.DOGTAG_HANGAR_HINT: 3,
                                           OnceOnlyHints.DOGTAG_PROFILE_HINT: 4,
                                           OnceOnlyHints.PLATOON_BTN_HINT: 5,
                                           OnceOnlyHints.MODE_SELECTOR_WIDGETS_BTN_HINT: 6,
                                           OnceOnlyHints.HANGAR_MANUAL_HINT: 7,
                                           OnceOnlyHints.MAPS_TRAINING_NEWBIE_HINT: 8,
                                           OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT: 9,
                                           OnceOnlyHints.VEHICLE_PREVIEW_POST_PROGRESSION_BUTTON_HINT: 10,
                                           OnceOnlyHints.VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT: 11,
                                           OnceOnlyHints.HERO_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT: 12,
                                           OnceOnlyHints.SWITCH_EQUIPMENT_AUXILIARY_LOADOUT_HINT: 13,
                                           OnceOnlyHints.SWITCH_EQUIPMENT_ESSENTIALS_LOADOUT_HINT: 14,
                                           OnceOnlyHints.COMPARE_MODIFICATIONS_PANEL_HINT: 15,
                                           OnceOnlyHints.COMPARE_SPECIALIZATION_BUTTON_HINT: 16,
                                           OnceOnlyHints.TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT: 17,
                                           OnceOnlyHints.PERSONAL_TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT: 18,
                                           OnceOnlyHints.RESEARCH_POST_PROGRESSION_ENTRY_POINT_HINT: 19,
                                           OnceOnlyHints.WOTPLUS_HANGAR_HINT: 20,
                                           OnceOnlyHints.WOTPLUS_PROFILE_HINT: 21,
                                           OnceOnlyHints.HANGAR_HAVE_NEW_BADGE_HINT: 22,
                                           OnceOnlyHints.HANGAR_HAVE_NEW_SUFFIX_BADGE_HINT: 23,
                                           OnceOnlyHints.APPLY_ABILITIES_TO_TYPE_CHECKBOX_HINT: 24,
                                           OnceOnlyHints.BATTLE_MATTERS_FIGHT_BUTTON_HINT: 25,
                                           OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT: 26,
                                           OnceOnlyHints.PERSONAL_RESERVES_HANGAR_HINT: 27,
                                           OnceOnlyHints.PERSONAL_RESERVES_ACTIVATION_HINT: 28}, offsets={}),
     SETTINGS_SECTIONS.DAMAGE_INDICATOR: Section(masks={DAMAGE_INDICATOR.TYPE: 0,
                                          DAMAGE_INDICATOR.PRESET_CRITS: 1,
                                          DAMAGE_INDICATOR.DAMAGE_VALUE: 2,
                                          DAMAGE_INDICATOR.VEHICLE_INFO: 3,
                                          DAMAGE_INDICATOR.ANIMATION: 4,
                                          DAMAGE_INDICATOR.DYNAMIC_INDICATOR: 5,
                                          DAMAGE_INDICATOR.PRESET_ALLIES: 6}, offsets={}),
     SETTINGS_SECTIONS.DAMAGE_LOG: Section(masks={DAMAGE_LOG.TOTAL_DAMAGE: 0,
                                    DAMAGE_LOG.BLOCKED_DAMAGE: 1,
                                    DAMAGE_LOG.ASSIST_DAMAGE: 2,
                                    DAMAGE_LOG.ASSIST_STUN: 3}, offsets={DAMAGE_LOG.SHOW_DETAILS: Offset(4, 48),
                                    DAMAGE_LOG.SHOW_EVENT_TYPES: Offset(6, 192),
                                    DAMAGE_LOG.EVENT_POSITIONS: Offset(8, 768)}),
     SETTINGS_SECTIONS.BATTLE_EVENTS: Section(masks={BATTLE_EVENTS.SHOW_IN_BATTLE: 0,
                                       BATTLE_EVENTS.ENEMY_HP_DAMAGE: 1,
                                       BATTLE_EVENTS.ENEMY_BURNING: 2,
                                       BATTLE_EVENTS.ENEMY_RAM_ATTACK: 3,
                                       BATTLE_EVENTS.BLOCKED_DAMAGE: 4,
                                       BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE: 5,
                                       BATTLE_EVENTS.ENEMY_TRACK_DAMAGE: 6,
                                       BATTLE_EVENTS.ENEMY_DETECTION: 7,
                                       BATTLE_EVENTS.ENEMY_KILL: 8,
                                       BATTLE_EVENTS.BASE_CAPTURE_DROP: 9,
                                       BATTLE_EVENTS.BASE_CAPTURE: 10,
                                       BATTLE_EVENTS.ENEMY_CRITICAL_HIT: 11,
                                       BATTLE_EVENTS.EVENT_NAME: 12,
                                       BATTLE_EVENTS.VEHICLE_INFO: 13,
                                       BATTLE_EVENTS.ENEMY_WORLD_COLLISION: 14,
                                       BATTLE_EVENTS.RECEIVED_DAMAGE: 15,
                                       BATTLE_EVENTS.RECEIVED_CRITS: 16,
                                       BATTLE_EVENTS.ENEMY_ASSIST_STUN: 17,
                                       BATTLE_EVENTS.ENEMIES_STUN: 18}, offsets={}),
     SETTINGS_SECTIONS.BATTLE_BORDER_MAP: Section(masks={}, offsets={BATTLE_BORDER_MAP.MODE_SHOW_BORDER: Offset(0, 3),
                                           BATTLE_BORDER_MAP.TYPE_BORDER: Offset(2, 12)}),
     SETTINGS_SECTIONS.UI_STORAGE: Section(masks={PM_TUTOR_FIELDS.GREETING_SCREEN_SHOWN: 0,
                                    PM_TUTOR_FIELDS.FIRST_ENTRY_AWARDS_SHOWN: 1,
                                    PM_TUTOR_FIELDS.ONE_FAL_SHOWN: 7,
                                    PM_TUTOR_FIELDS.MULTIPLE_FAL_SHOWN: 8,
                                    UI_STORAGE_KEYS.AUTO_RELOAD_MARK_IS_SHOWN: 9,
                                    UI_STORAGE_KEYS.DISABLE_ANIMATED_TOOLTIP: 13,
                                    UI_STORAGE_KEYS.FIELD_POST_HINT_IS_SHOWN: 14,
                                    PM_TUTOR_FIELDS.PM2_ONE_FAL_SHOWN: 15,
                                    PM_TUTOR_FIELDS.PM2_MULTIPLE_FAL_SHOWN: 16,
                                    UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN: 17,
                                    UI_STORAGE_KEYS.DUAL_GUN_MARK_IS_SHOWN: 18,
                                    UI_STORAGE_KEYS.DISABLE_EDITABLE_STYLE_REWRITE_WARNING: 22,
                                    UI_STORAGE_KEYS.TURBOSHAFT_MARK_IS_SHOWN: 26,
                                    UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN: 27,
                                    UI_STORAGE_KEYS.EPIC_BATTLE_ABILITIES_INTRO_SHOWN: 28,
                                    UI_STORAGE_KEYS.POST_PROGRESSION_INTRO_SHOWN: 29,
                                    UI_STORAGE_KEYS.VEH_PREVIEW_POST_PROGRESSION_BULLET_SHOWN: 30}, offsets={PM_TUTOR_FIELDS.INITIAL_FAL_COUNT: Offset(2, 124),
                                    UI_STORAGE_KEYS.AUTO_RELOAD_HIGHLIGHTS_COUNTER: Offset(10, 7168),
                                    UI_STORAGE_KEYS.DUAL_GUN_HIGHLIGHTS_COUNTER: Offset(19, 3670016),
                                    UI_STORAGE_KEYS.TURBOSHAFT_HIGHLIGHTS_COUNTER: Offset(23, 58720256)}),
     SETTINGS_SECTIONS.UI_STORAGE_2: Section(masks={UI_STORAGE_KEYS.ROCKET_ACCELERATION_MARK_IS_SHOWN: 0}, offsets={UI_STORAGE_KEYS.ROCKET_ACCELERATION_HIGHLIGHTS_COUNTER: Offset(1, 14)}),
     SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS: Section(masks={}, offsets={'shown': Offset(0, 255)}),
     SETTINGS_SECTIONS.QUESTS_PROGRESS: Section(masks={}, offsets={QUESTS_PROGRESS.VIEW_TYPE: Offset(0, 3),
                                         QUESTS_PROGRESS.DISPLAY_TYPE: Offset(2, 12)}),
     SETTINGS_SECTIONS.SESSION_STATS: Section(masks={SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY: 0,
                                       SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB: 1,
                                       SESSION_STATS.CURRENT_TAB: 2,
                                       SESSION_STATS.ECONOMIC_BLOCK_VIEW: 3,
                                       SESSION_STATS.SHOW_WTR: 4,
                                       SESSION_STATS.SHOW_RATIO_DAMAGE: 5,
                                       SESSION_STATS.SHOW_RATIO_KILL: 6,
                                       SESSION_STATS.SHOW_WINS: 7,
                                       SESSION_STATS.SHOW_AVERAGE_DAMAGE: 8,
                                       SESSION_STATS.SHOW_HELP_DAMAGE: 9,
                                       SESSION_STATS.SHOW_BLOCKED_DAMAGE: 10,
                                       SESSION_STATS.SHOW_AVERAGE_XP: 11,
                                       SESSION_STATS.SHOW_WIN_RATE: 12,
                                       SESSION_STATS.SHOW_AVERAGE_VEHICLE_LEVEL: 13,
                                       SESSION_STATS.SHOW_AVERAGE_FRAGS: 14,
                                       SESSION_STATS.SHOW_SURVIVED_RATE: 15,
                                       SESSION_STATS.SHOW_SPOTTED: 16,
                                       SESSION_STATS.ONLY_ONCE_HINT_SHOWN_FIELD: 17}, offsets={}),
     SETTINGS_SECTIONS.BATTLE_PASS_STORAGE: Section(masks={BATTLE_PASS.INTRO_SHOWN: 16,
                                             BATTLE_PASS.EXTRA_CHAPTER_VIDEO_SHOWN: 18,
                                             BATTLE_PASS.EXTRA_CHAPTER_INTRO_SHOWN: 19,
                                             BATTLE_PASS.INTRO_VIDEO_SHOWN: 20,
                                             BATTLE_PASS.DAILY_QUESTS_INTRO_SHOWN: 27}, offsets={BATTLE_PASS.BUY_ANIMATION_WAS_SHOWN: Offset(10, 15360),
                                             BATTLE_PASS.FLAGS_VERSION: Offset(21, 132120576)}),
     SETTINGS_SECTIONS.BATTLE_COMM: Section(masks={BATTLE_COMM.ENABLE_BATTLE_COMMUNICATION: 0,
                                     BATTLE_COMM.SHOW_COM_IN_PLAYER_LIST: 1,
                                     BATTLE_COMM.SHOW_STICKY_MARKERS: 2,
                                     BATTLE_COMM.SHOW_CALLOUT_MESSAGES: 3,
                                     BATTLE_COMM.SHOW_BASE_MARKERS: 4,
                                     BATTLE_COMM.SHOW_LOCATION_MARKERS: 5}, offsets={}),
     SETTINGS_SECTIONS.DOG_TAGS: Section(masks={GAME.SHOW_VICTIMS_DOGTAG: 0,
                                  GAME.SHOW_DOGTAG_TO_KILLER: 1}, offsets={}),
     SETTINGS_SECTIONS.BATTLE_HUD: Section(masks={SCORE_PANEL.SHOW_HP_VALUES: 0,
                                    SCORE_PANEL.SHOW_HP_DIFFERENCE: 1,
                                    SCORE_PANEL.ENABLE_TIER_GROUPING: 2,
                                    SCORE_PANEL.SHOW_HP_BAR: 3}, offsets={GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL: Offset(4, 48),
                                    GAME.SHOW_VEHICLE_HP_IN_MINIMAP: Offset(6, 192)}),
     SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                  'germany': 1,
                                                  'usa': 2,
                                                  'china': 3,
                                                  'france': 4,
                                                  'uk': 5,
                                                  'japan': 6,
                                                  'czech': 7,
                                                  'sweden': 8,
                                                  'poland': 9,
                                                  'italy': 10,
                                                  'lightTank': 15,
                                                  'mediumTank': 16,
                                                  'heavyTank': 17,
                                                  'SPG': 18,
                                                  'AT-SPG': 19,
                                                  'level_1': 20,
                                                  'level_2': 21,
                                                  'level_3': 22,
                                                  'level_4': 23,
                                                  'level_5': 24,
                                                  'level_6': 25,
                                                  'level_7': 26,
                                                  'level_8': 27,
                                                  'level_9': 28,
                                                  'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                  'elite': 1,
                                                  'rented': 2,
                                                  'igr': 3,
                                                  'gameMode': 4,
                                                  'favorite': 5,
                                                  'bonus': 6,
                                                  'event': 7,
                                                  'crystals': 8,
                                                  'battleRoyale': 9}, offsets={}),
     SETTINGS_SECTIONS.MAPBOX_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                  'germany': 1,
                                                  'usa': 2,
                                                  'china': 3,
                                                  'france': 4,
                                                  'uk': 5,
                                                  'japan': 6,
                                                  'czech': 7,
                                                  'sweden': 8,
                                                  'poland': 9,
                                                  'italy': 10,
                                                  'lightTank': 15,
                                                  'mediumTank': 16,
                                                  'heavyTank': 17,
                                                  'SPG': 18,
                                                  'AT-SPG': 19,
                                                  'level_1': 20,
                                                  'level_2': 21,
                                                  'level_3': 22,
                                                  'level_4': 23,
                                                  'level_5': 24,
                                                  'level_6': 25,
                                                  'level_7': 26,
                                                  'level_8': 27,
                                                  'level_9': 28,
                                                  'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.MAPBOX_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                  'elite': 1,
                                                  'rented': 2,
                                                  'igr': 3,
                                                  'gameMode': 4,
                                                  'favorite': 5,
                                                  'bonus': 6,
                                                  'event': 7,
                                                  'crystals': 8,
                                                  'role_HT_assault': 11,
                                                  'role_HT_break': 12,
                                                  'role_HT_support': 13,
                                                  'role_HT_universal': 14,
                                                  'role_MT_universal': 15,
                                                  'role_MT_sniper': 16,
                                                  'role_MT_assault': 17,
                                                  'role_MT_support': 18,
                                                  'role_ATSPG_assault': 19,
                                                  'role_ATSPG_universal': 20,
                                                  'role_ATSPG_sniper': 21,
                                                  'role_ATSPG_support': 22,
                                                  'role_LT_universal': 23,
                                                  'role_LT_wheeled': 24,
                                                  'role_SPG': 25}, offsets={}),
     SETTINGS_SECTIONS.UNIT_FILTER: Section(masks={}, offsets={GAME.UNIT_FILTER: Offset(0, 2047)}),
     SETTINGS_SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                      'germany': 1,
                                                      'usa': 2,
                                                      'china': 3,
                                                      'france': 4,
                                                      'uk': 5,
                                                      'japan': 6,
                                                      'czech': 7,
                                                      'sweden': 8,
                                                      'poland': 9,
                                                      'italy': 10,
                                                      'lightTank': 15,
                                                      'mediumTank': 16,
                                                      'heavyTank': 17,
                                                      'SPG': 18,
                                                      'AT-SPG': 19,
                                                      'level_1': 20,
                                                      'level_2': 21,
                                                      'level_3': 22,
                                                      'level_4': 23,
                                                      'level_5': 24,
                                                      'level_6': 25,
                                                      'level_7': 26,
                                                      'level_8': 27,
                                                      'level_9': 28,
                                                      'level_10': 29}, offsets={}),
     SETTINGS_SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                      'elite': 1,
                                                      'rented': 2,
                                                      'igr': 3,
                                                      'gameMode': 4,
                                                      'favorite': 5,
                                                      'bonus': 6,
                                                      'event': 7,
                                                      'crystals': 8,
                                                      'funRandom': 9,
                                                      'role_HT_assault': 11,
                                                      'role_HT_break': 12,
                                                      'role_HT_support': 13,
                                                      'role_HT_universal': 14,
                                                      'role_MT_universal': 15,
                                                      'role_MT_sniper': 16,
                                                      'role_MT_assault': 17,
                                                      'role_MT_support': 18,
                                                      'role_ATSPG_assault': 19,
                                                      'role_ATSPG_universal': 20,
                                                      'role_ATSPG_sniper': 21,
                                                      'role_ATSPG_support': 22,
                                                      'role_LT_universal': 23,
                                                      'role_LT_wheeled': 24,
                                                      'role_SPG': 25}, offsets={})}
    AIM_MAPPING = {'net': 1,
     'netType': 1,
     'centralTag': 1,
     'centralTagType': 1,
     'reloader': 2,
     'condition': 2,
     'mixing': 2,
     'mixingType': 2,
     'cassette': 3,
     'gunTag': 3,
     'gunTagType': 3,
     'reloaderTimer': 3,
     'zoomIndicator': 4}
    _MAX_AUTO_RELOAD_HIGHLIGHTS_COUNT = 5
    _MAX_DUAL_GUN_HIGHLIGHTS_COUNT = 5
    _MAX_TURBOSHAFT_HIGHLIGHTS_COUNT = 5
    _MAX_ROCKET_ACCELERATION_HIGHLIGHTS_COUNT = 5

    def __init__(self, core):
        self._core = weakref.proxy(core)

    @adisp_process
    def applySettings(self):
        import BattleReplay
        if not BattleReplay.isPlaying():
            yield self._updateToVersion()
        self._core.options.refresh()
        enableDynamicCamera = self._core.options.getSetting(self.GAME.DYNAMIC_CAMERA)
        enableDynamicCameraValue = enableDynamicCamera.get()
        enableSniperStabilization = self._core.options.getSetting(self.GAME.SNIPER_MODE_STABILIZATION)
        enableSniperStabilizationValue = enableSniperStabilization.get()
        enableSniperHullLock = self._core.options.getSetting(self.GAME.HULLLOCK_ENABLED)
        enableSniperHullLockValue = enableSniperHullLock.get()
        from AvatarInputHandler import AvatarInputHandler
        AvatarInputHandler.enableDynamicCamera(enableDynamicCameraValue, enableSniperStabilizationValue)
        AvatarInputHandler.enableHullLock(enableSniperHullLockValue)
        if not BattleReplay.isPlaying():
            from messenger.doc_loaders import user_prefs
            from messenger import g_settings as messenger_settings
            user_prefs.loadFromServer(messenger_settings)
        self._core.storages.get('FOV').apply(False, True)

    def getAimSetting(self, section, key, default=None):
        number = self.AIM_MAPPING[key]
        storageKey = 'AIM_{section}_{number}'.format(section=section.upper(), number=number)
        settingsKey = 'AIM_{number}'.format(number=number)
        storedValue = self.settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[settingsKey].masks
        offsets = self.SECTIONS[settingsKey].offsets
        return self._extractValue(key, storedValue, default, masks, offsets) if storedValue is not None else default

    def getOnceOnlyHintsSetting(self, key, default=None):
        for onlyHintSection in SETTINGS_SECTIONS.ONCE_ONLY_HINTS_GROUP:
            if self._hasKeyInSection(onlyHintSection, key):
                return self.getSectionSettings(onlyHintSection, key, default)

        LOG_ERROR('Trying to extract unsupported key in once only hints group: ', key)
        return default

    def getOnceOnlyHintsSettings(self):
        return self.getSections(SETTINGS_SECTIONS.ONCE_ONLY_HINTS_GROUP)

    def setOnceOnlyHintsSettings(self, settings):
        settingToServer = {}
        onceOnlyHintsDiff = {}
        for section in SETTINGS_SECTIONS.ONCE_ONLY_HINTS_GROUP:
            keys = self.SECTIONS[section].masks.keys() + self.SECTIONS[section].offsets.keys()
            currentSettings = {key:value for key, value in settings.items() if key in keys}
            storedSettings = self.getSection(section)
            stored = self.settingsCache.getSectionSettings(section, None)
            storing = self._buildSectionSettings(section, currentSettings)
            if stored != storing:
                settingToServer[section] = storing
                for k, v in currentSettings.iteritems():
                    if storedSettings.get(k) != v:
                        onceOnlyHintsDiff[k] = v

        if settingToServer:
            self.setSettings(settingToServer)
        if onceOnlyHintsDiff:
            self._core.onOnceOnlyHintsChanged(onceOnlyHintsDiff)
        return

    def getUIStorage(self, defaults=None):
        return self.getSection(SETTINGS_SECTIONS.UI_STORAGE, defaults)

    def saveInUIStorage(self, fields):
        return self.setSections([SETTINGS_SECTIONS.UI_STORAGE], fields)

    def getUIStorage2(self, defaults=None):
        return self.getSection(SETTINGS_SECTIONS.UI_STORAGE_2, defaults)

    def saveInUIStorage2(self, fields):
        return self.setSections([SETTINGS_SECTIONS.UI_STORAGE_2], fields)

    def getBPStorage(self, defaults=None):
        if not self.settingsCache.isSynced():
            return {}
        storageData = self.getSection(SETTINGS_SECTIONS.BATTLE_PASS_STORAGE, defaults)
        if updateBattlePassSettings(storageData):
            self.saveInBPStorage(storageData)
        return storageData

    def saveInBPStorage(self, settings):
        if self.settingsCache.isSynced():
            self.setSectionSettings(SETTINGS_SECTIONS.BATTLE_PASS_STORAGE, settings)

    def checkAutoReloadHighlights(self, increase=False):
        return self.__checkUIHighlights(UI_STORAGE_KEYS.AUTO_RELOAD_HIGHLIGHTS_COUNTER, self._MAX_AUTO_RELOAD_HIGHLIGHTS_COUNT, increase)

    def checkDualGunHighlights(self, increase=False):
        return self.__checkUIHighlights(UI_STORAGE_KEYS.DUAL_GUN_HIGHLIGHTS_COUNTER, self._MAX_DUAL_GUN_HIGHLIGHTS_COUNT, increase)

    def checkTurboshaftHighlights(self, increase=False):
        return self.__checkUIHighlights(UI_STORAGE_KEYS.TURBOSHAFT_HIGHLIGHTS_COUNTER, self._MAX_TURBOSHAFT_HIGHLIGHTS_COUNT, increase)

    def checkRocketAccelerationHighlights(self, increase=False):
        return self.__checkUIHighlights(UI_STORAGE_KEYS.ROCKET_ACCELERATION_HIGHLIGHTS_COUNTER, self._MAX_ROCKET_ACCELERATION_HIGHLIGHTS_COUNT, increase)

    def updateUIStorageCounter(self, key, step=1):
        storageSection = self.getSection(SETTINGS_SECTIONS.UI_STORAGE)
        if key in storageSection:
            self.saveInUIStorage({key: storageSection[key] + step})
        else:
            storageSection = self.getSection(SETTINGS_SECTIONS.UI_STORAGE_2)
            if key in storageSection:
                self.saveInUIStorage2({key: storageSection[key] + step})

    def setDisableAnimTooltipFlag(self):
        self.saveInUIStorage({UI_STORAGE_KEYS.DISABLE_ANIMATED_TOOLTIP: 1})

    def getDisableAnimTooltipFlag(self):
        return self.getUIStorage().get(UI_STORAGE_KEYS.DISABLE_ANIMATED_TOOLTIP) == 1

    def getBattleMattersQuestWasShowed(self):
        return self.getSectionSettings(SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS, 'shown', 0)

    def setBattleMattersQuestWasShowed(self, count):
        return self.setSectionSettings(SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS, {'shown': count})

    def setQuestProgressSettings(self, settings):
        self.setSectionSettings(SETTINGS_SECTIONS.QUESTS_PROGRESS, settings)

    def _buildAimSettings(self, settings):
        settingToServer = {}
        for section, options in settings.iteritems():
            mapping = {}
            for key, value in options.iteritems():
                number = self.AIM_MAPPING[key]
                mapping.setdefault(number, {})[key] = value

            for number, value in mapping.iteritems():
                settingsKey = 'AIM_{number}'.format(number=number)
                storageKey = 'AIM_{section}_{number}'.format(section=section.upper(), number=number)
                storingValue = storedValue = self.settingsCache.getSetting(storageKey)
                masks = self.SECTIONS[settingsKey].masks
                offsets = self.SECTIONS[settingsKey].offsets
                storingValue = self._mapValues(value, storingValue, masks, offsets)
                if storedValue == storingValue:
                    continue
                settingToServer[storageKey] = storingValue

        return settingToServer

    def setAimSettings(self, settings):
        storingValue = self._buildAimSettings(settings)
        if not storingValue:
            return
        self.settingsCache.setSettings(storingValue)
        LOG_DEBUG('Applying AIM server settings: ', settings)
        self._core.onSettingsChanged(settings)

    def getMarkersSetting(self, section, key, default=None):
        storageKey = 'MARKERS_{section}'.format(section=section.upper())
        storedValue = self.settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].masks
        offsets = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].offsets
        return self._extractValue(key, storedValue, default, masks, offsets) if storedValue is not None else default

    def _buildMarkersSettings(self, settings):
        settingToServer = {}
        for section, options in settings.iteritems():
            storageKey = 'MARKERS_{section}'.format(section=section.upper())
            storingValue = storedValue = self.settingsCache.getSetting(storageKey)
            masks = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].masks
            offsets = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].offsets
            storingValue = self._mapValues(options, storingValue, masks, offsets)
            if storedValue == storingValue:
                continue
            settingToServer[storageKey] = storingValue

        return settingToServer

    def setMarkersSettings(self, settings):
        storingValue = self._buildMarkersSettings(settings)
        if not storingValue:
            return
        self.settingsCache.setSettings(storingValue)
        LOG_DEBUG('Applying MARKER server settings: ', settings)
        self._core.onSettingsChanged(settings)

    def setSessionStatsSettings(self, settings):
        self.setSectionSettings(SETTINGS_SECTIONS.SESSION_STATS, settings)

    def getSessionStatsSettings(self):
        return self.getSection(SETTINGS_SECTIONS.SESSION_STATS)

    def getVersion(self):
        return self.settingsCache.getVersion()

    def setSettings(self, settings):
        self.settingsCache.setSettings(settings)
        LOG_DEBUG('Applying server settings: ', settings)
        self._core.onSettingsChanged(settings)

    def getSetting(self, key, default=None):
        return self.settingsCache.getSetting(key, default)

    def getSection(self, section, defaults=None):
        result = {}
        defaults = defaults or {}
        masks = self.SECTIONS[section].masks
        offsets = self.SECTIONS[section].offsets
        for m in masks:
            default = defaults.get(m, None)
            result[m] = self.getSectionSettings(section, m, default)

        for o in offsets:
            default = defaults.get(o, None)
            result[o] = self.getSectionSettings(section, o, default)

        return result

    def getSections(self, sections, defaults=None):
        result = {}
        for section in sections:
            result.update(self.getSection(section, defaults))

        return result

    def setSections(self, sections, settings):
        settingToServer = {}
        for section in sections:
            keys = self.SECTIONS[section].masks.keys() + self.SECTIONS[section].offsets.keys()
            currentSettings = {key:value for key, value in settings.items() if key in keys}
            stored = self.settingsCache.getSectionSettings(section, None)
            storing = self._buildSectionSettings(section, currentSettings)
            if stored != storing:
                settingToServer[section] = storing

        if settingToServer:
            self.setSettings(settingToServer)
        return

    def getSectionSettings(self, section, key, default=None):
        storedValue = self.settingsCache.getSectionSettings(section, None)
        masks = self.SECTIONS[section].masks
        offsets = self.SECTIONS[section].offsets
        return self._extractValue(key, storedValue, default, masks, offsets) if storedValue is not None else default

    def setSectionSettings(self, section, settings):
        storedSettings = self.getSection(section)
        storedValue = self.settingsCache.getSectionSettings(section, None)
        storingValue = self._buildSectionSettings(section, settings)
        if storedValue == storingValue:
            return
        else:
            self.settingsCache.setSectionSettings(section, storingValue)
            settingsDiff = {}
            for k, v in settings.iteritems():
                sV = storedSettings.get(k)
                if sV != v:
                    settingsDiff[k] = v

            LOG_DEBUG('Applying %s server settings: ' % section, settingsDiff)
            self._core.onSettingsChanged(settingsDiff)
            return

    def _buildSectionSettings(self, section, settings):
        storedValue = self.settingsCache.getSectionSettings(section, None)
        storingValue = storedValue if storedValue is not None else 0
        sectionMasks = self.SECTIONS[section]
        masks = sectionMasks.masks
        offsets = sectionMasks.offsets
        return self._mapValues(settings, storingValue, masks, offsets)

    def _extractValue(self, key, storedValue, default, masks, offsets):
        if key in masks:
            return storedValue >> masks[key] & 1
        if key in offsets:
            return (storedValue & offsets[key].mask) >> offsets[key].offset
        LOG_ERROR('Trying to extract unsupported option: ', key)
        return default

    def _mapValues(self, settings, storingValue, masks, offsets):
        for key, value in settings.iteritems():
            if key in masks:
                storingValue &= ~(1 << masks[key])
                itemValue = int(value) << masks[key]
            elif key in offsets:
                storingValue &= ~offsets[key].mask
                itemValue = int(value) << offsets[key].offset
            else:
                LOG_ERROR('Trying to apply unsupported option: ', key, value)
                continue
            storingValue |= itemValue

        return storingValue

    def _hasKeyInSection(self, section, key):
        return key in self.SECTIONS[section].masks or key in self.SECTIONS[section].offsets

    @adisp_async
    @adisp_process
    def _updateToVersion(self, callback=None):
        currentVersion = self.settingsCache.getVersion()
        data = {'gameData': {},
         'gameExtData': {},
         'gameExtData2': {},
         'gameplayData': {},
         'controlsData': {},
         'aimData': {},
         'markersData': {},
         'graphicsData': {},
         'marksOnGun': {},
         'fallout': {},
         'carousel_filter': {},
         'feedbackDamageIndicator': {},
         'feedbackDamageLog': {},
         'feedbackBattleEvents': {},
         'onceOnlyHints': {},
         'onceOnlyHints2': {},
         'uiStorage': {},
         SETTINGS_SECTIONS.UI_STORAGE_2: {},
         'epicCarouselFilter2': {},
         'rankedCarouselFilter1': {},
         'rankedCarouselFilter2': {},
         'comp7CarouselFilter1': {},
         'comp7CarouselFilter2': {},
         'sessionStats': {},
         'battleComm': {},
         'dogTags': {},
         'battleHud': {},
         'spgAim': {},
         GUI_START_BEHAVIOR: {},
         'battlePassStorage': {},
         SETTINGS_SECTIONS.CONTOUR: {},
         SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1: {},
         SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2: {},
         'clear': {},
         'delete': []}
        yield migrateToVersion(currentVersion, self._core, data)
        self._setSettingsSections(data)
        callback(self)

    def _setSettingsSections(self, data):
        settings = {}
        clear = data.get('clear', {})
        gameData = data.get('gameData', {})
        clearGame = clear.get(SETTINGS_SECTIONS.GAME, 0)
        if gameData or clearGame:
            settings[SETTINGS_SECTIONS.GAME] = self._buildSectionSettings(SETTINGS_SECTIONS.GAME, gameData) ^ clearGame
        gameExtData = data.get('gameExtData', {})
        clearGameExt = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
        if gameExtData or clearGameExt:
            settings[SETTINGS_SECTIONS.GAME_EXTENDED] = self._buildSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, gameExtData) ^ clearGameExt
        gameExtData = data.get('gameExtData2', {})
        clearGameExt = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED_2, 0)
        if gameExtData or clearGameExt:
            settings[SETTINGS_SECTIONS.GAME_EXTENDED_2] = self._buildSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED_2, gameExtData) ^ clearGameExt
        gameplayData = data.get('gameplayData', {})
        clearGameplay = clear.get(SETTINGS_SECTIONS.GAMEPLAY, 0)
        if gameplayData or clearGameplay:
            settings[SETTINGS_SECTIONS.GAMEPLAY] = self._buildSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, gameplayData) ^ clearGameplay
        controlsData = data.get('controlsData', {})
        clearControls = clear.get(SETTINGS_SECTIONS.CONTROLS, 0)
        if controlsData or clearControls:
            settings[SETTINGS_SECTIONS.CONTROLS] = self._buildSectionSettings(SETTINGS_SECTIONS.CONTROLS, controlsData) ^ clearControls
        graphicsData = data.get('graphicsData', {})
        clearGraphics = clear.get(SETTINGS_SECTIONS.GRAPHICS, 0)
        if graphicsData or clearGraphics:
            settings[SETTINGS_SECTIONS.GRAPHICS] = self._buildSectionSettings(SETTINGS_SECTIONS.GRAPHICS, graphicsData) ^ clearGraphics
        aimData = data.get('aimData', {})
        if aimData:
            settings.update(self._buildAimSettings(aimData))
        markersData = data.get('markersData', {})
        if markersData:
            settings.update(self._buildMarkersSettings(markersData))
        marksOnGun = data.get('marksOnGun', {})
        if marksOnGun:
            settings[SETTINGS_SECTIONS.MARKS_ON_GUN] = self._buildSectionSettings(SETTINGS_SECTIONS.MARKS_ON_GUN, marksOnGun)
        fallout = data.get('fallout', {})
        if fallout:
            settings[SETTINGS_SECTIONS.FALLOUT] = self._buildSectionSettings(SETTINGS_SECTIONS.FALLOUT, fallout)
        carousel_filter = data.get('carousel_filter', {})
        clearCarouselFilter = clear.get('carousel_filter', 0)
        if carousel_filter or clearCarouselFilter:
            settings[SETTINGS_SECTIONS.CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.CAROUSEL_FILTER_2, carousel_filter) ^ clearCarouselFilter
        epicFilterCarousel = data.get('epicCarouselFilter2', {})
        clearEpicFilterCarousel = clear.get('epicCarouselFilter2', 0)
        if epicFilterCarousel or clearEpicFilterCarousel:
            settings[SETTINGS_SECTIONS.EPICBATTLE_CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.EPICBATTLE_CAROUSEL_FILTER_2, epicFilterCarousel) ^ clearEpicFilterCarousel
        rankedFilterCarousel1 = data.get('rankedCarouselFilter1', {})
        clearRankedFilterCarousel1 = clear.get('rankedCarouselFilter1', 0)
        if rankedFilterCarousel1 or clearRankedFilterCarousel1:
            settings[SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_1] = self._buildSectionSettings(SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_1, rankedFilterCarousel1) ^ clearRankedFilterCarousel1
        rankedFilterCarousel2 = data.get('rankedCarouselFilter2', {})
        clearRankedFilterCarousel2 = clear.get('rankedCarouselFilter2', 0)
        if rankedFilterCarousel2 or clearRankedFilterCarousel2:
            settings[SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.RANKED_CAROUSEL_FILTER_2, rankedFilterCarousel2) ^ clearRankedFilterCarousel2
        comp7FilterCarousel1 = data.get('comp7CarouselFilter1', {})
        clearComp7FilterCarousel1 = clear.get('comp7CarouselFilter1', 0)
        if comp7FilterCarousel1 or clearComp7FilterCarousel1:
            settings[SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_1] = self._buildSectionSettings(SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_1, comp7FilterCarousel1) ^ clearComp7FilterCarousel1
        comp7FilterCarousel2 = data.get('comp7CarouselFilter2', {})
        clearComp7FilterCarousel2 = clear.get('comp7CarouselFilter2', 0)
        if comp7FilterCarousel2 or clearComp7FilterCarousel2:
            settings[SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.COMP7_CAROUSEL_FILTER_2, comp7FilterCarousel2) ^ clearComp7FilterCarousel2
        feedbackDamageIndicator = data.get('feedbackDamageIndicator', {})
        if feedbackDamageIndicator:
            settings[SETTINGS_SECTIONS.DAMAGE_INDICATOR] = self._buildSectionSettings(SETTINGS_SECTIONS.DAMAGE_INDICATOR, feedbackDamageIndicator)
        feedbackDamageLog = data.get('feedbackDamageLog', {})
        if feedbackDamageLog:
            settings[SETTINGS_SECTIONS.DAMAGE_LOG] = self._buildSectionSettings(SETTINGS_SECTIONS.DAMAGE_LOG, feedbackDamageLog)
        feedbackBattleEvents = data.get('feedbackBattleEvents', {})
        if feedbackBattleEvents:
            settings[SETTINGS_SECTIONS.BATTLE_EVENTS] = self._buildSectionSettings(SETTINGS_SECTIONS.BATTLE_EVENTS, feedbackBattleEvents)
        onceOnlyHints = data.get('onceOnlyHints', {})
        clearOnceOnlyHints = clear.get('onceOnlyHints', 0)
        if onceOnlyHints or clearOnceOnlyHints:
            settings[SETTINGS_SECTIONS.ONCE_ONLY_HINTS] = self._buildSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, onceOnlyHints) ^ clearOnceOnlyHints
        onceOnlyHints2 = data.get('onceOnlyHints2', {})
        clearOnceOnlyHints2 = clear.get('onceOnlyHints2', 0)
        if onceOnlyHints or clearOnceOnlyHints:
            settings[SETTINGS_SECTIONS.ONCE_ONLY_HINTS_2] = self._buildSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS_2, onceOnlyHints2) ^ clearOnceOnlyHints2
        uiStorage = data.get('uiStorage', {})
        clearUIStorage = clear.get('uiStorage', 0)
        if uiStorage or clearUIStorage:
            settings[SETTINGS_SECTIONS.UI_STORAGE] = self._buildSectionSettings(SETTINGS_SECTIONS.UI_STORAGE, uiStorage) ^ clearUIStorage
        uiStorage2 = data.get(SETTINGS_SECTIONS.UI_STORAGE_2, {})
        clearUIStorage2 = clear.get(SETTINGS_SECTIONS.UI_STORAGE_2, 0)
        if uiStorage2 or clearUIStorage2:
            settings[SETTINGS_SECTIONS.UI_STORAGE_2] = self._buildSectionSettings(SETTINGS_SECTIONS.UI_STORAGE_2, uiStorage2) ^ clearUIStorage2
        sessionStats = data.get('sessionStats', {})
        clearSessionStats = clear.get('sessionStats', 0)
        if sessionStats or clearSessionStats:
            settings[SETTINGS_SECTIONS.SESSION_STATS] = self._buildSectionSettings(SETTINGS_SECTIONS.SESSION_STATS, sessionStats) ^ clearSessionStats
        battleComm = data.get('battleComm', {})
        clearBattleComm = clear.get('battleComm', 0)
        if battleComm or clearBattleComm:
            settings[SETTINGS_SECTIONS.BATTLE_COMM] = self._buildSectionSettings(SETTINGS_SECTIONS.BATTLE_COMM, battleComm) ^ clearBattleComm
        dogTags = data.get('dogTags', {})
        clearDogTags = clear.get('dogTags', 0)
        if dogTags or clearDogTags:
            settings[SETTINGS_SECTIONS.DOG_TAGS] = self._buildSectionSettings(SETTINGS_SECTIONS.DOG_TAGS, dogTags) ^ clearDogTags
        battleHud = data.get('battleHud', {})
        clearBattleHud = clear.get('battleHud', 0)
        if battleHud or clearBattleHud:
            settings[SETTINGS_SECTIONS.BATTLE_HUD] = self._buildSectionSettings(SETTINGS_SECTIONS.BATTLE_HUD, battleHud) ^ clearBattleHud
        guiStartBehavior = data.get(GUI_START_BEHAVIOR, {})
        clearGuiStartBehavior = clear.get(GUI_START_BEHAVIOR, 0)
        if guiStartBehavior or clearGuiStartBehavior:
            settings[SETTINGS_SECTIONS.GUI_START_BEHAVIOR] = self._buildSectionSettings(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, guiStartBehavior) ^ clearGuiStartBehavior
        BPStorage = data.get('battlePassStorage', {})
        clearBPStorage = clear.get('battlePassStorage', 0)
        if BPStorage or clearBPStorage:
            settings[SETTINGS_SECTIONS.BATTLE_PASS_STORAGE] = self._buildSectionSettings(SETTINGS_SECTIONS.BATTLE_PASS_STORAGE, BPStorage) ^ clearBPStorage
        spgAimData = data.get('spgAim', {})
        clearSpgAimData = clear.get(SETTINGS_SECTIONS.SPG_AIM, 0)
        if spgAimData or clearSpgAimData:
            settings[SETTINGS_SECTIONS.SPG_AIM] = self._buildSectionSettings(SETTINGS_SECTIONS.SPG_AIM, spgAimData) ^ clearSpgAimData
        contourData = data.get(SETTINGS_SECTIONS.CONTOUR, {})
        clearContourData = clear.get(SETTINGS_SECTIONS.CONTOUR, 0)
        if contourData or clearContourData:
            settings[SETTINGS_SECTIONS.CONTOUR] = self._buildSectionSettings(SETTINGS_SECTIONS.CONTOUR, contourData) ^ clearContourData
        royaleFilterCarousel1 = data.get(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1, {})
        clearRoyaleFilterCarousel1 = clear.get(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1, 0)
        if royaleFilterCarousel1 or clearRoyaleFilterCarousel1:
            settings[SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1] = self._buildSectionSettings(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1, royaleFilterCarousel1) ^ clearRoyaleFilterCarousel1
        royaleFilterCarousel2 = data.get(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2, {})
        clearRoyaleFilterCarousel2 = clear.get(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2, 0)
        if royaleFilterCarousel2 or clearRoyaleFilterCarousel2:
            settings[SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2, royaleFilterCarousel2) ^ clearRoyaleFilterCarousel2
        battleMatters = data.get(SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS, {})
        clearBattleMatters = clear.get(SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS, 0)
        if battleMatters or clearBattleMatters:
            settings[SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS] = self._buildSectionSettings(SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS, battleMatters) ^ clearBattleMatters
        version = data.get(VERSION)
        if version is not None:
            settings[VERSION] = version
        if settings:
            self.setSettings(settings)
        delete = data.get('delete', ())
        if delete:
            self.settingsCache.delSettings(delete)
        return

    def __checkUIHighlights(self, key, maxVal, increase):
        storage = self.getUIStorage()
        if key not in storage:
            storage = self.getUIStorage2()
        res = storage.get(key) < maxVal
        if res and increase:
            self.updateUIStorageCounter(key)
        return res
