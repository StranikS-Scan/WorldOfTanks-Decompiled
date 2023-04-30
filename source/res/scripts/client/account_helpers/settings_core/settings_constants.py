# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/settings_constants.py
from shared_utils import CONST_CONTAINER
VERSION = 'VERSION'

class GRAPHICS(CONST_CONTAINER):
    MONITOR = 'monitor'
    VIDEO_MODE = 'screenMode'
    WINDOW_MODE = 'windowMode'
    WINDOW_SIZE = 'windowSize'
    RESOLUTION = 'resolution'
    BORDERLESS_SIZE = 'borderlessSize'
    REFRESH_RATE = 'refreshRate'
    GAMMA_SETTING = 'gammaSetting'
    NATIVE_RESOLUTION = 'nativeResolution'
    VERTICAL_SYNC = 'vertSync'
    TRIPLE_BUFFERED = 'tripleBuffered'
    IGB_HARDWARE_ACCELERATION = 'igbHardwareAcceleration'
    COLOR_BLIND = 'isColorBlind'
    GRAPHICS_QUALITY_HD_SD = 'graphicsQualityHDSD'
    GRAPHICS_QUALITY_HD_SD_HIGH = 'graphicsQualityHDSDHigh'
    IS_SD_QUALITY = 'isSDQuality'
    GRAPHICS_SETTINGS_LIST = 'qualityOrder'
    PRESETS = 'presets'
    QUALITY_PRESET = 'graphicsQuality'
    DYNAMIC_RENDERER = 'dynamicRenderer'
    COLOR_FILTER_INTENSITY = 'colorFilterIntensity'
    BRIGHTNESS_CORRECTION = 'brightnessCorrection'
    CONTRAST_CORRECTION = 'contrastCorrection'
    SATURATION_CORRECTON = 'saturationCorrection'
    COLOR_FILTER_SETTING = 'colorFilter'
    COLOR_FILTER_IMAGES = 'colorFilterImages'
    FOV = 'fov'
    DYNAMIC_FOV_ENABLED = 'dynamicFov'
    INTERFACE_SCALE = 'interfaceScale'
    DRR_AUTOSCALER_ENABLED = 'DRR_AUTOSCALER_ENABLED'
    RENDER_PIPELINE = 'RENDER_PIPELINE'
    TESSELLATION_SUPPORTED = 'tessellationSupported'
    COLOR_GRADING_TECHNIQUE = 'COLOR_GRADING_TECHNIQUE'

    @classmethod
    def getScreenConstants(cls):
        return (cls.MONITOR,
         cls.VIDEO_MODE,
         cls.WINDOW_SIZE,
         cls.RESOLUTION,
         cls.BORDERLESS_SIZE,
         cls.REFRESH_RATE,
         cls.DYNAMIC_RENDERER,
         cls.INTERFACE_SCALE)

    @classmethod
    def getColorSettings(cls):
        return (cls.COLOR_FILTER_INTENSITY,
         cls.BRIGHTNESS_CORRECTION,
         cls.CONTRAST_CORRECTION,
         cls.COLOR_GRADING_TECHNIQUE,
         cls.SATURATION_CORRECTON)

    @classmethod
    def getCustomColorSettings(cls):
        return (cls.BRIGHTNESS_CORRECTION, cls.CONTRAST_CORRECTION, cls.SATURATION_CORRECTON)


class GAME(CONST_CONTAINER):
    ENABLE_OL_FILTER = 'enableOlFilter'
    ENABLE_SPAM_FILTER = 'enableSpamFilter'
    DATE_TIME_MESSAGE_INDEX = 'datetimeIdx'
    SHOW_DATE_MESSAGE = 'showDateMessage'
    SHOW_TIME_MESSAGE = 'showTimeMessage'
    INVITES_FROM_FRIENDS = 'invitesFromFriendsOnly'
    RECEIVE_CLAN_INVITES_NOTIFICATIONS = 'receiveClanInvitesNotifications'
    RECEIVE_INVITES_IN_BATTLE = 'receiveInvitesInBattle'
    BATTLE_LOADING_INFO = 'battleLoadingInfo'
    BATTLE_LOADING_RANKED_INFO = 'battleLoadingRankedInfo'
    RECEIVE_FRIENDSHIP_REQUEST = 'receiveFriendshipRequest'
    STORE_RECEIVER_IN_BATTLE = 'storeReceiverInBattle'
    DISABLE_BATTLE_CHAT = 'disableBattleChat'
    CHAT_CONTACTS_LIST_ONLY = 'chatContactsListOnly'
    LENS_EFFECT = 'enableOpticalSnpEffect'
    MINIMAP_ALPHA = 'minimapAlpha'
    ENABLE_POSTMORTEM_DELAY = 'enablePostMortemDelay'
    REPLAY_ENABLED = 'replayEnabled'
    SNIPER_ZOOM = 'sniperZoom'
    PRE_COMMANDER_CAM = 'preCommanderCam'
    COMMANDER_CAM = 'commanderCam'
    HULLLOCK_ENABLED = 'hullLockEnabled'
    SHOW_VEHICLE_HP_IN_PLAYERS_PANEL = 'showVehicleHPinPlayersPanel'
    SHOW_VEHICLE_HP_IN_MINIMAP = 'showVehicleHPinMinimap'
    ENABLE_SERVER_AIM = 'useServerAim'
    SHOW_DAMAGE_ICON = 'showDamageIcon'
    SHOW_VEHICLES_COUNTER = 'showVehiclesCounter'
    SHOW_MARKS_ON_GUN = 'showMarksOnGun'
    ANONYMIZER = 'anonymizer'
    SHOW_VICTIMS_DOGTAG = 'showVictimsDogTag'
    SHOW_DOGTAG_TO_KILLER = 'showDogTagToKiller'
    DYNAMIC_CAMERA = 'dynamicCamera'
    SNIPER_MODE_STABILIZATION = 'horStabilizationSnp'
    INCREASED_ZOOM = 'increasedZoom'
    SNIPER_MODE_BY_SHIFT = 'sniperModeByShift'
    ENABLE_SPEEDOMETER = 'enableSpeedometer'
    ENABLE_REPAIR_TIMER = 'enableRepairTimer'
    ENABLE_BATTLE_NOTIFIER = 'enableBattleNotifier'
    HANGAR_CAM_PERIOD = 'hangarCamPeriod'
    HANGAR_CAM_PARALLAX_ENABLED = 'hangarCamParallaxEnabled'
    PLAYERS_PANELS_SHOW_LEVELS = 'ppShowLevels'
    PLAYERS_PANELS_SHOW_TYPES = 'ppShowTypes'
    PLAYERS_PANELS_STATE = 'ppState'
    EPIC_RANDOM_PLAYERS_PANELS_STATE = 'epicppState'
    GAMEPLAY_MASK = 'gameplayMask'
    GAMEPLAY_CTF = 'gameplay_ctf'
    GAMEPLAY_DOMINATION = 'gameplay_domination'
    GAMEPLAY_ASSAULT = 'gameplay_assault'
    GAMEPLAY_NATIONS = 'gameplay_nations'
    GAMEPLAY_EPIC_STANDARD = 'gameplay_epicStandard'
    GAMEPLAY_ONLY_10_MODE = 'gameplay_only10Mode'
    GAMEPLAY_EPIC_DOMINATION = 'gameplay_epicDomination'
    SHOW_VECTOR_ON_MAP = 'showVectorOnMap'
    SHOW_SECTOR_ON_MAP = 'showSectorOnMap'
    SHOW_VEH_MODELS_ON_MAP = 'showVehModelsOnMap'
    SHOW_ARTY_HIT_ON_MAP = 'showArtyHitOnMap'
    MINIMAP_VIEW_RANGE = 'minimapViewRange'
    MINIMAP_MAX_VIEW_RANGE = 'minimapMaxViewRange'
    MINIMAP_DRAW_RANGE = 'minimapDrawRange'
    MINIMAP_MIN_SPOTTING_RANGE = 'minimapMinSpottingRange'
    SNIPER_MODE_SWINGING_ENABLED = 'SNIPER_MODE_SWINGING_ENABLED'
    CAROUSEL_TYPE = 'carouselType'
    CUSTOMIZATION_DISPLAY_TYPE = 'customizationDisplayType'
    DOUBLE_CAROUSEL_TYPE = 'doubleCarouselType'
    VEHICLE_CAROUSEL_STATS = 'vehicleCarouselStats'
    MINIMAP_ALPHA_ENABLED = 'minimapAlphaEnabled'
    DISPLAY_PLATOON_MEMBERS = 'displayPlatoonMembers'
    LOGIN_SERVER_SELECTION = 'loginServerSelection'
    UNIT_FILTER = 'unitFilter'
    SWITCH_SETUPS_IN_LOADING = 'switchEquipment'
    SCROLL_SMOOTHING = 'scrollSmoothing'


class SOUND(CONST_CONTAINER):
    GAME_EVENT_AMBIENT = 'specialAmbientVolume'
    GAME_EVENT_EFFECTS = 'specialEffectsVolume'
    GAME_EVENT_GUI = 'specialGuiVolume'
    GAME_EVENT_MUSIC = 'specialMusicVolume'
    GAME_EVENT_VEHICLES = 'specialVehiclesVolume'
    GAME_EVENT_VOICE = 'specialVoiceNotificationVolume'
    MASTER_TOGGLE = 'masterVolumeToggle'
    SOUND_QUALITY = 'soundQuality'
    SOUND_QUALITY_VISIBLE = 'soundQualityVisible'
    SUBTITLES = 'subtitles'
    MASTER = 'masterVolume'
    MUSIC = 'musicVolume'
    MUSIC_HANGAR = 'musicHangar'
    VEHICLES = 'vehiclesVolume'
    EFFECTS = 'effectsVolume'
    GUI = 'guiVolume'
    AMBIENT = 'ambientVolume'
    NATIONS_VOICES = 'nationalVoices'
    ALT_VOICES = 'alternativeVoices'
    SOUND_DEVICE = 'soundDevice'
    SOUND_SPEAKERS = 'soundSpeakers'
    VOICE_NOTIFICATION = 'voiceNotificationVolume'
    DETECTION_ALERT_SOUND = 'bulbVoices'
    ARTY_SHOT_ALERT_SOUND = 'artyBulbVoices'
    CAPTURE_DEVICES = 'captureDevice'
    VOIP_ENABLE = 'enableVoIP'
    VOIP_ENABLE_CHANNEL = 'enableVoIPChannel'
    VOIP_MASTER = 'masterVivoxVolume'
    VOIP_MIC = 'micVivoxVolume'
    VOIP_MASTER_FADE = 'masterFadeVivoxVolume'
    VOIP_SUPPORTED = 'voiceChatSupported'
    BASS_BOOST = 'bassBoost'
    NIGHT_MODE = 'nightMode'
    LOW_QUALITY = 'lowQualitySound'


class CONTROLS(CONST_CONTAINER):
    MOUSE_ARCADE_SENS = 'mouseArcadeSens'
    MOUSE_SNIPER_SENS = 'mouseSniperSens'
    MOUSE_STRATEGIC_SENS = 'mouseStrategicSens'
    MOUSE_ASSIST_AIM_SENS = 'mouseAssistAimSens'
    MOUSE_HORZ_INVERSION = 'mouseHorzInvert'
    MOUSE_VERT_INVERSION = 'mouseVertInvert'
    BACK_DRAFT_INVERSION = 'backDraftInvert'
    KEYBOARD = 'keyboard'
    KEYBOARD_IMPORTANT_BINDS = 'keyboardImportantBinds'


class AIM(CONST_CONTAINER):
    ARCADE = 'arcade'
    SNIPER = 'sniper'
    SPG = 'spg'
    CONTOUR = 'contour'


class SPGAim(CONST_CONTAINER):
    SHOTS_RESULT_INDICATOR = 'shotsResultIndicator'
    SPG_SCALE_WIDGET = 'spgScaleWidget'
    SPG_STRATEGIC_CAM_MODE = 'spgStrategicCamMode'
    AUTO_CHANGE_AIM_MODE = 'autoChangeAimMode'
    AIM_ENTRANCE_MODE = 'aimEntranceMode'


class CONTOUR(CONST_CONTAINER):
    ENHANCED_CONTOUR = 'contour'
    CONTOUR_PENETRABLE_ZONE = 'contourPenetrableZone'
    CONTOUR_IMPENETRABLE_ZONE = 'contourImpenetrableZone'


class SPGAimEntranceModeOptions(CONST_CONTAINER):
    LAST = 'last'
    STRATEGIC = 'strategic'
    TRAJECTORY = 'trajectory'
    SETTINGS_OPTIONS = [LAST, STRATEGIC, TRAJECTORY]


class MARKERS(CONST_CONTAINER):
    ALLY = 'ally'
    ENEMY = 'enemy'
    DEAD = 'dead'


class MARKER_SETTINGS(CONST_CONTAINER):
    MARKER_BASE_VEHICLE_DIST = 'markerBaseVehicleDist'
    MARKER_ALT_VEHICLE_DIST = 'markerAltVehicleDist'


class FEEDBACK(CONST_CONTAINER):
    DAMAGE_INDICATOR = 'feedbackDamageIndicator'
    DAMAGE_LOG = 'feedbackDamageLog'
    BATTLE_EVENTS = 'feedbackBattleEvents'
    BATTLE_BORDER_MAP = 'feedbackBattleBorderMap'
    QUESTS_PROGRESS = 'feedbackQuestsProgress'


class DAMAGE_INDICATOR(CONST_CONTAINER):
    TYPE = 'damageIndicatorType'
    PRESET_CRITS = 'damageIndicatorCrits'
    PRESET_ALLIES = 'damageIndicatorAllies'
    DAMAGE_VALUE = 'damageIndicatorDamageValue'
    VEHICLE_INFO = 'damageIndicatorVehicleInfo'
    ANIMATION = 'damageIndicatorAnimation'
    DYNAMIC_INDICATOR = 'damageIndicatorDynamicIndicator'


class DAMAGE_LOG(CONST_CONTAINER):
    TOTAL_DAMAGE = 'damageLogTotalDamage'
    BLOCKED_DAMAGE = 'damageLogBlockedDamage'
    ASSIST_DAMAGE = 'damageLogAssistDamage'
    ASSIST_STUN = 'damageLogAssistStun'
    SHOW_DETAILS = 'damageLogShowDetails'
    SHOW_EVENT_TYPES = 'damageLogShowEventTypes'
    EVENT_POSITIONS = 'damageLogEventsPosition'


class BATTLE_EVENTS(CONST_CONTAINER):
    SHOW_IN_BATTLE = 'battleEventsShowInBattle'
    ENEMY_HP_DAMAGE = 'battleEventsEnemyHpDamage'
    ENEMY_BURNING = 'battleEventsEnemyBurning'
    ENEMY_RAM_ATTACK = 'battleEventsEnemyRamAttack'
    BLOCKED_DAMAGE = 'battleEventsBlockedDamage'
    ENEMY_DETECTION_DAMAGE = 'battleEventsEnemyDetectionDamage'
    ENEMY_TRACK_DAMAGE = 'battleEventsEnemyTrackDamage'
    ENEMY_DETECTION = 'battleEventsEnemyDetection'
    ENEMY_KILL = 'battleEventsEnemyKill'
    BASE_CAPTURE_DROP = 'battleEventsBaseCaptureDrop'
    BASE_CAPTURE = 'battleEventsBaseCapture'
    ENEMY_CRITICAL_HIT = 'battleEventsEnemyCriticalHit'
    EVENT_NAME = 'battleEventsEventName'
    VEHICLE_INFO = 'battleEventsVehicleInfo'
    ENEMY_WORLD_COLLISION = 'battleEventsEnemyWorldCollision'
    RECEIVED_DAMAGE = 'battleEventsReceivedDamage'
    RECEIVED_CRITS = 'battleEventsReceivedCrits'
    ENEMY_ASSIST_STUN = 'battleEventsEnemyAssistStun'
    ENEMIES_STUN = 'battleEventsEnemyStun'


class BATTLE_BORDER_MAP(CONST_CONTAINER):
    MODE_SHOW_BORDER = 'battleBorderMapMode'
    TYPE_BORDER = 'battleBorderMapType'


class QUESTS_PROGRESS(CONST_CONTAINER):
    VIEW_TYPE = 'progressViewType'
    DISPLAY_TYPE = 'progressViewConditions'


class CONTACTS(CONST_CONTAINER):
    SHOW_OFFLINE_USERS = 'showOfflineUsers'
    SHOW_OTHERS_CATEGORY = 'showOthersCategory'
    ANTISPAM_MESSAGES_COUNTER = 'antispamMessagesCounter'


class SETTINGS_GROUP(CONST_CONTAINER):
    GAME_SETTINGS = 'GameSettings'
    GRAPHICS_SETTINGS = 'GraphicSettings'
    SOUND_SETTINGS = 'SoundSettings'
    CONTROLS_SETTINGS = 'ControlsSettings'
    AIM_SETTINGS = 'AimSettings'
    MARKERS_SETTINGS = 'MarkerSettings'
    FEEDBACK_SETTINGS = 'FeedbackSettings'


class GuiSettingsBehavior(CONST_CONTAINER):
    FREE_XP_INFO_DIALOG_SHOWED = 'isFreeXPInfoDialogShowed'
    RANKED_WELCOME_VIEW_SHOWED = 'isRankedWelcomeViewShowed'
    RANKED_WELCOME_VIEW_STARTED = 'isRankedWelcomeViewStarted'
    EPIC_RANDOM_CHECKBOX_CLICKED = 'isEpicRandomCheckboxClicked'
    DISPLAY_PLATOON_MEMBER_CLICKED = 'isDisplayPlatoonMembersClicked'
    VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW = 'vehPostProgressionUnlockMsgNeedShow'
    BIRTHDAY_CALENDAR_INTRO_SHOWED = 'birthdayCalendarIntroShowed'
    RESOURCE_WELL_INTRO_SHOWN = 'resourceWellIntroShown'
    COMP7_INTRO_SHOWN = 'isComp7IntroShown'
    CREW_22_WELCOME_SHOWN = 'crew22WelcomeShown'


class OnceOnlyHints(CONST_CONTAINER):
    FALLOUT_QUESTS_TAB = 'FalloutQuestsTab'
    CUSTOMIZATION_SLOTS_HINT = 'CustomizationSlotsHint'
    SHOP_TRADE_IN_HINT = 'ShopTradeInHint'
    VEH_COMPARE_CONFIG_HINT = 'VehCompareConfigHint'
    HOLD_SHEET_HINT = 'HoldSheetHint'
    HAVE_NEW_BADGE_HINT = 'HaveNewBadgeHint'
    HANGAR_HAVE_NEW_BADGE_HINT = 'HangarHaveNewBadgeHint'
    EPIC_RESERVES_SLOT_HINT = 'EpicReservesSlotHint'
    PAUSE_HINT = 'PauseHint'
    HAVE_NEW_SUFFIX_BADGE_HINT = 'HaveNewSuffixBadgeHint'
    HANGAR_HAVE_NEW_SUFFIX_BADGE_HINT = 'HangarHaveNewSuffixBadgeHint'
    BADGE_PAGE_NEW_SUFFIX_BADGE_HINT = 'BadgePageNewSuffixBadgeHint'
    C11N_AUTOPROLONGATION_HINT = 'CustomizationAutoprolongationHint'
    C11N_PROGRESSION_VIEW_HINT = 'CustomizationProgressionViewHint'
    C11N_EDITABLE_STYLES_HINT = 'CustomizationEditableStylesHint'
    C11N_EDITABLE_STYLE_SLOT_HINT = 'C11nEditableStyleSlotHint'
    C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT = 'C11nEditableStyleSlotButtonHint'
    C11N_PROGRESSION_REQUIRED_STYLES_HINT = 'C11nProgressionRequiredStylesHint'
    C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT = 'C11nProgressionRequiredStyleSlotHint'
    C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT = 'C11nProgressionRequiredStyleSlotButtonHint'
    BLUEPRINTS_SWITCHBUTTON_HINT = 'BlueprintsSwitchButtonHint'
    BLUEPRINTS_RESEARCH_BUTTON_HINT = 'BlueprintsResearchButtonHint'
    BLUEPRINTS_TECHTREE_CONVERT_BUTTON_HINT = 'BlueprintsTechtreeConvertButtonHint'
    BLUEPRINTS_RESEARCH_CONVERT_BUTTON_HINT = 'BlueprintsResearchConvertButtonHint'
    BLUEPRINT_SCREEN_CONVERT_FRAGMENT_HINT = 'BlueprintScreenConvertFragmentHint'
    ACCOUNT_BUTTON_HINT = 'AccountButtonHint'
    SESSION_STATS_OPEN_BTN_HINT = 'SessionStatsOpenBtnHint'
    SESSION_STATS_SETTINGS_BTN_HINT = 'SessionStatsSettingsBtnHint'
    BATTLE_SESSION_UP_BUTTON_TOURNAMENT_HINT = 'BattleSessionUpButtonTournamentHint'
    CREW_OPERATION_BTN_HINT = 'CrewOperationBtnHint'
    SOUND_BUTTONEX_HINT = 'SoundButtonExHint'
    VEHICLE_PREVIEW_MODULES_BUTTON_HINT = 'VehiclePreviewModulesButtonHint'
    AMMUNITION_PANEL_HINT = 'AmmunitionPanelHintZoneHint'
    PLATOON_BTN_HINT = 'PlatoonBtnHint'
    AMMUNITION_FILTER_HINT = 'FilterHintZoneHint'
    MODERNIZED_SETUP_TAB_HINT = 'ModernizedSetupTabHint'
    OPT_DEV_DRAG_AND_DROP_HINT = 'OptDevDragAndDropHint'
    HANGAR_MANUAL_HINT = 'HangarManualHint'
    DOGTAG_HANGAR_HINT = 'DogTagHangarHint'
    DOGTAG_PROFILE_HINT = 'DogTagProfileHint'
    WOTPLUS_HANGAR_HINT = 'WotPlusHangarHint'
    PERSONAL_RESERVES_HANGAR_HINT = 'PersonalReservesHangarHint'
    PERSONAL_RESERVES_ACTIVATION_HINT = 'PersonalReservesActivationHint'
    WOTPLUS_PROFILE_HINT = 'WotPlusProfileHint'
    MODE_SELECTOR_WIDGETS_BTN_HINT = 'ModeSelectorWidgetsBtnHint'
    MAPS_TRAINING_NEWBIE_HINT = 'MapsTrainingNewbieHint'
    AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT = 'AmmunitionPanelBattleAbilitiesHint'
    VEHICLE_PREVIEW_POST_PROGRESSION_BUTTON_HINT = 'VehiclePreviewPostProgressionButtonHint'
    VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT = 'VehiclePostProgressionEntryPointHint'
    RESEARCH_POST_PROGRESSION_ENTRY_POINT_HINT = 'ResearchPostProgressionEntryPointHint'
    HERO_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT = 'HeroVehiclePreviewPostProgressionButtonHint'
    SWITCH_EQUIPMENT_AUXILIARY_LOADOUT_HINT = 'SwitchEquipmentAuxiliaryLoadoutHint'
    SWITCH_EQUIPMENT_ESSENTIALS_LOADOUT_HINT = 'SwitchEquipmentEssentialsLoadoutHint'
    COMPARE_MODIFICATIONS_PANEL_HINT = 'CompareModificationsPanelHint'
    COMPARE_SPECIALIZATION_BUTTON_HINT = 'CompareSpecializationButtonHint'
    TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT = 'TradeInVehiclePreviewPostProgressionButtonHint'
    PERSONAL_TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT = 'PersonalTradeInVehiclePreviewPostProgressionButtonHint'
    APPLY_ABILITIES_TO_TYPE_CHECKBOX_HINT = 'ApplyAbilitiesToTypeCheckboxHint'
    SHOW_ABILITIES_BUTTON_HINT = 'ShowAbilitiesButtonHint'
    BATTLE_MATTERS_FIGHT_BUTTON_HINT = 'BattleMattersFightButtonHint'
    BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT = 'BattleMattersEntryPointHint'


class SESSION_STATS(CONST_CONTAINER):
    IS_NOT_NEEDED_RESET_STATS_EVERY_DAY = 'IsNotNeededResetStatsEveryDay'
    IS_NEEDED_SAVE_CURRENT_TAB = 'IsNeededSaveCurrentTab'
    CURRENT_TAB = 'CurrentTab'
    ECONOMIC_BLOCK_VIEW = 'EconomicBlockView'
    SHOW_WTR = 'ShowWtr'
    SHOW_RATIO_DAMAGE = 'ShowRatioDamage'
    SHOW_RATIO_KILL = 'ShowRatioKill'
    SHOW_WINS = 'ShowWins'
    SHOW_AVERAGE_DAMAGE = 'ShowAverageDamage'
    SHOW_HELP_DAMAGE = 'ShowHelpDamage'
    SHOW_BLOCKED_DAMAGE = 'ShowBlockedDamage'
    SHOW_AVERAGE_XP = 'ShowAverageXp'
    SHOW_WIN_RATE = 'ShowWinRate'
    SHOW_AVERAGE_VEHICLE_LEVEL = 'ShowAverageVehicleLevel'
    SHOW_AVERAGE_FRAGS = 'ShowAverageFrags'
    SHOW_SURVIVED_RATE = 'ShowSurvivedRate'
    SHOW_SPOTTED = 'ShowSpotted'
    ONLY_ONCE_HINT_SHOWN_FIELD = 'OnlyOnceHintShownField'
    ECONOMIC_BLOCK_VIEW_WITH_SPENDING = 0
    ECONOMIC_BLOCK_VIEW_WITHOUT_SPENDING = 1
    BATTLES_TAB = 0
    VEHICLES_TAB = 1

    @classmethod
    def getEfficiencyBlock(cls):
        return (cls.SHOW_WTR,
         cls.SHOW_WINS,
         cls.SHOW_WIN_RATE,
         cls.SHOW_AVERAGE_FRAGS,
         cls.SHOW_RATIO_KILL,
         cls.SHOW_AVERAGE_DAMAGE,
         cls.SHOW_RATIO_DAMAGE,
         cls.SHOW_HELP_DAMAGE,
         cls.SHOW_BLOCKED_DAMAGE,
         cls.SHOW_SPOTTED,
         cls.SHOW_AVERAGE_VEHICLE_LEVEL,
         cls.SHOW_SURVIVED_RATE,
         cls.SHOW_AVERAGE_XP)

    @classmethod
    def getAccountEfficiencyBlock(cls):
        return (cls.SHOW_WTR,
         cls.SHOW_WINS,
         cls.SHOW_WIN_RATE,
         cls.SHOW_AVERAGE_FRAGS,
         cls.SHOW_RATIO_KILL,
         cls.SHOW_AVERAGE_DAMAGE,
         cls.SHOW_RATIO_DAMAGE,
         cls.SHOW_HELP_DAMAGE,
         cls.SHOW_BLOCKED_DAMAGE,
         cls.SHOW_SPOTTED,
         cls.SHOW_AVERAGE_VEHICLE_LEVEL,
         cls.SHOW_SURVIVED_RATE,
         cls.SHOW_AVERAGE_XP)

    @classmethod
    def getVehiclesEfficiencyBlock(cls):
        return (cls.SHOW_WTR,
         cls.SHOW_WINS,
         cls.SHOW_WIN_RATE,
         cls.SHOW_AVERAGE_FRAGS,
         cls.SHOW_RATIO_KILL,
         cls.SHOW_AVERAGE_DAMAGE,
         cls.SHOW_RATIO_DAMAGE,
         cls.SHOW_HELP_DAMAGE,
         cls.SHOW_BLOCKED_DAMAGE,
         cls.SHOW_SPOTTED,
         cls.SHOW_SURVIVED_RATE,
         cls.SHOW_AVERAGE_XP)

    @classmethod
    def getImmutableEfficiencyBlockParameters(cls):
        return (cls.SHOW_WTR,)

    @classmethod
    def getCommonBlock(cls):
        return (cls.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY, cls.IS_NEEDED_SAVE_CURRENT_TAB)

    @classmethod
    def getEconomicBlockView(cls):
        return (cls.ECONOMIC_BLOCK_VIEW_WITHOUT_SPENDING, cls.ECONOMIC_BLOCK_VIEW_WITH_SPENDING)


class BattlePassStorageKeys(CONST_CONTAINER):
    INTRO_SHOWN = 'introShown'
    INTRO_VIDEO_SHOWN = 'introVideoShown'
    BUY_ANIMATION_WAS_SHOWN = 'buyAnimationWasShown'
    FLAGS_VERSION = 'flagsVersion'
    DAILY_QUESTS_INTRO_SHOWN = 'dailyQuestsIntroShown'
    EXTRA_CHAPTER_INTRO_SHOWN = 'extraChapterIntroShown'
    EXTRA_CHAPTER_VIDEO_SHOWN = 'extraChapterVideoShown'


class BattleCommStorageKeys(CONST_CONTAINER):
    ENABLE_BATTLE_COMMUNICATION = 'enableBattleComm'
    SHOW_COM_IN_PLAYER_LIST = 'showCommInPlayerlist'
    SHOW_STICKY_MARKERS = 'showStickyMarkers'
    SHOW_CALLOUT_MESSAGES = 'showCalloutMessages'
    SHOW_LOCATION_MARKERS = 'showLocationMarkers'
    SHOW_BASE_MARKERS = 'showMarkers'


class ScorePanelStorageKeys(CONST_CONTAINER):
    SHOW_HP_BAR = 'showHPBar'
    SHOW_HP_VALUES = 'showHPValues'
    SHOW_HP_DIFFERENCE = 'showHPDifference'
    ENABLE_TIER_GROUPING = 'enableTierGrouping'
