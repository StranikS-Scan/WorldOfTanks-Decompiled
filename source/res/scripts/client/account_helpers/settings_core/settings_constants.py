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
    VERTICAL_SYNC = 'vertSync'
    TRIPLE_BUFFERED = 'tripleBuffered'
    COLOR_BLIND = 'isColorBlind'
    GRAPHICS_QUALITY_HD_SD = 'graphicsQualityHDSD'
    GRAPHICS_QUALITY_HD_SD_HIGH = 'graphicsQualityHDSDHigh'
    IS_SD_QUALITY = 'isSDQuality'
    GRAPHICS_SETTINGS_LIST = 'qualityOrder'
    PRESETS = 'presets'
    QUALITY_PRESET = 'graphicsQuality'
    DYNAMIC_RENDERER = 'dynamicRenderer'
    COLOR_FILTER_INTENSITY = 'colorFilterIntensity'
    COLOR_FILTER_IMAGES = 'colorFilterImages'
    FOV = 'fov'
    DYNAMIC_FOV_ENABLED = 'dynamicFov'
    INTERFACE_SCALE = 'interfaceScale'
    DRR_AUTOSCALER_ENABLED = 'DRR_AUTOSCALER_ENABLED'
    RENDER_PIPELINE = 'RENDER_PIPELINE'
    TESSELLATION_SUPPORTED = 'tessellationSupported'

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
    ENABLE_SERVER_AIM = 'useServerAim'
    SHOW_VEHICLES_COUNTER = 'showVehiclesCounter'
    SHOW_MARKS_ON_GUN = 'showMarksOnGun'
    DYNAMIC_CAMERA = 'dynamicCamera'
    SNIPER_MODE_STABILIZATION = 'horStabilizationSnp'
    INCREASED_ZOOM = 'increasedZoom'
    SNIPER_MODE_BY_SHIFT = 'sniperModeByShift'
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
    GAMEPLAY_EPIC_DOMINATION = 'gameplay_epicDomination'
    SHOW_VECTOR_ON_MAP = 'showVectorOnMap'
    SHOW_SECTOR_ON_MAP = 'showSectorOnMap'
    SHOW_VEH_MODELS_ON_MAP = 'showVehModelsOnMap'
    MINIMAP_VIEW_RANGE = 'minimapViewRange'
    MINIMAP_MAX_VIEW_RANGE = 'minimapMaxViewRange'
    MINIMAP_DRAW_RANGE = 'minimapDrawRange'
    SNIPER_MODE_SWINGING_ENABLED = 'SNIPER_MODE_SWINGING_ENABLED'
    CAROUSEL_TYPE = 'carouselType'
    DOUBLE_CAROUSEL_TYPE = 'doubleCarouselType'
    VEHICLE_CAROUSEL_STATS = 'vehicleCarouselStats'
    MINIMAP_ALPHA_ENABLED = 'minimapAlphaEnabled'
    C11N_HISTORICALLY_ACCURATE = 'c11nHistoricallyAccurate'


class TUTORIAL(CONST_CONTAINER):
    CUSTOMIZATION = 'customization'
    PERSONAL_CASE = 'personalCase'
    TECHNICAL_MAINTENANCE = 'technicalMaintenance'
    RESEARCH = 'research'
    RESEARCH_TREE = 'researchTree'
    MEDKIT_INSTALLED = 'medKitInstalled'
    REPAIRKIT_INSTALLED = 'repairKitInstalled'
    FIRE_EXTINGUISHER_INSTALLED = 'fireExtinguisherInstalled'
    MEDKIT_USED = 'medKitUsed'
    REPAIRKIT_USED = 'repairKitUsed'
    FIRE_EXTINGUISHER_USED = 'fireExtinguisherUsed'
    WAS_QUESTS_TUTORIAL_STARTED = 'wasQuestsTutorialStarted'


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
    CAPTURE_DEVICES = 'captureDevice'
    VOIP_ENABLE = 'enableVoIP'
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


class MARKERS(CONST_CONTAINER):
    ALLY = 'ally'
    ENEMY = 'enemy'
    DEAD = 'dead'


class OTHER(CONST_CONTAINER):
    VIBRO_CONNECTED = 'vibroIsConnected'
    VIBRO_GAIN = 'vibroGain'
    VIBRO_ENGINE = 'vibroEngine'
    VIBRO_ACCELERATION = 'vibroAcceleration'
    VIBRO_SHOTS = 'vibroShots'
    VIBRO_HITS = 'vibroHits'
    VIBRO_COLLISIONS = 'vibroCollisions'
    VIBRO_DAMAGE = 'vibroDamage'
    VIBRO_GUI = 'vibroGUI'


class FEEDBACK(CONST_CONTAINER):
    DAMAGE_INDICATOR = 'feedbackDamageIndicator'
    DAMAGE_LOG = 'feedbackDamageLog'
    BATTLE_EVENTS = 'feedbackBattleEvents'
    BATTLE_BORDER_MAP = 'feedbackBattleBorderMap'


class DAMAGE_INDICATOR(CONST_CONTAINER):
    TYPE = 'damageIndicatorType'
    PRESETS = 'damageIndicatorPresets'
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


class BATTLE_BORDER_MAP(CONST_CONTAINER):
    MODE_SHOW_BORDER = 'battleBorderMapMode'
    TYPE_BORDER = 'battleBorderMapType'


class CONTACTS(CONST_CONTAINER):
    SHOW_OFFLINE_USERS = 'showOfflineUsers'
    SHOW_OTHERS_CATEGORY = 'showOthersCategory'


class SETTINGS_GROUP(CONST_CONTAINER):
    GAME_SETTINGS = 'GameSettings'
    GRAPHICS_SETTINGS = 'GraphicSettings'
    SOUND_SETTINGS = 'SoundSettings'
    CONTROLS_SETTINGS = 'ControlsSettings'
    AIM_SETTINGS = 'AimSettings'
    MARKERS_SETTINGS = 'MarkerSettings'
    OTHER_SETTINGS = 'OtherSettings'
    FEEDBACK_SETTINGS = 'FeedbackSettings'
