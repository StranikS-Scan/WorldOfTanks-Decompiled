# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/SettingsCore.py
import BigWorld
import Event
from Vibroeffects import VibroManager
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.ServerSettingsManager import ServerSettingsManager, SETTINGS_SECTIONS
from adisp import process
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.SETTINGS import SETTINGS
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from InterfaceScaleManager import InterfaceScaleManager

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getStunSwitch(lobbyContext=None):
    return lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getEpicRandomSwitch(lobbyContext=None):
    return lobbyContext.getServerSettings().isEpicRandomEnabled()


class SettingsCore(ISettingsCore):
    onSettingsChanged = Event.Event()
    onSettingsApplied = Event.Event()

    def __init__(self):
        super(SettingsCore, self).__init__()
        self.__serverSettings = None
        self.__interfaceScale = None
        self.__storages = None
        self.__options = None
        return

    def init(self):
        from account_helpers.settings_core import options, settings_storages, settings_constants
        from gui.shared.utils import graphics
        GAME = settings_constants.GAME
        TUTORIAL = settings_constants.TUTORIAL
        GRAPHICS = settings_constants.GRAPHICS
        SOUND = settings_constants.SOUND
        CONTROLS = settings_constants.CONTROLS
        AIM = settings_constants.AIM
        MARKERS = settings_constants.MARKERS
        OTHER = settings_constants.OTHER
        DAMAGE_INDICATOR = settings_constants.DAMAGE_INDICATOR
        DAMAGE_LOG = settings_constants.DAMAGE_LOG
        BATTLE_EVENTS = settings_constants.BATTLE_EVENTS
        BATTLE_BORDER_MAP = settings_constants.BATTLE_BORDER_MAP
        QUESTS_PROGRESS = settings_constants.QUESTS_PROGRESS
        self.__serverSettings = ServerSettingsManager(self)
        self.__interfaceScale = InterfaceScaleManager(self)
        VIDEO_SETTINGS_STORAGE = settings_storages.VideoSettingsStorage(self.serverSettings, self)
        GAME_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.GAME)
        EXTENDED_GAME_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.GAME_EXTENDED)
        TUTORIAL_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.TUTORIAL)
        GAMEPLAY_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.GAMEPLAY)
        GRAPHICS_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.GRAPHICS)
        SOUND_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.SOUND)
        CONTROLS_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.CONTROLS)
        AIM_SETTINGS_STORAGE = settings_storages.AimSettingsStorage(self.serverSettings, self)
        MARKERS_SETTINGS_STORAGE = settings_storages.MarkersSettingsStorage(self.serverSettings, self)
        MARK_ON_GUN_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.MARKS_ON_GUN)
        FOV_SETTINGS_STORAGE = settings_storages.FOVSettingsStorage(self.serverSettings, self)
        DAMAGE_INDICATOR_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.DAMAGE_INDICATOR)
        DAMAGE_LOG_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.DAMAGE_LOG)
        BATTLE_EVENTS_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.BATTLE_EVENTS)
        BATTLE_BORDER_MAP_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.BATTLE_BORDER_MAP)
        QUESTS_PROGRESS_SETTINGS_STORAGE = settings_storages.ServerSettingsStorage(self.serverSettings, self, SETTINGS_SECTIONS.QUESTS_PROGRESS)
        MESSENGER_SETTINGS_STORAGE = settings_storages.MessengerSettingsStorage(GAME_SETTINGS_STORAGE)
        EXTENDED_MESSENGER_SETTINGS_STORAGE = settings_storages.MessengerSettingsStorage(EXTENDED_GAME_SETTINGS_STORAGE)
        self.__storages = {'game': GAME_SETTINGS_STORAGE,
         'extendedGame': EXTENDED_GAME_SETTINGS_STORAGE,
         'gameplay': GAMEPLAY_SETTINGS_STORAGE,
         'sound': SOUND_SETTINGS_STORAGE,
         'controls': CONTROLS_SETTINGS_STORAGE,
         'aim': AIM_SETTINGS_STORAGE,
         'markers': MARKERS_SETTINGS_STORAGE,
         'graphics': GRAPHICS_SETTINGS_STORAGE,
         'video': VIDEO_SETTINGS_STORAGE,
         'messenger': MESSENGER_SETTINGS_STORAGE,
         'extendedMessenger': EXTENDED_MESSENGER_SETTINGS_STORAGE,
         'marksOnGun': MARK_ON_GUN_SETTINGS_STORAGE,
         'FOV': FOV_SETTINGS_STORAGE,
         'tutorial': TUTORIAL_SETTINGS_STORAGE,
         'damageIndicator': DAMAGE_INDICATOR_SETTINGS_STORAGE,
         'damageLog': DAMAGE_LOG_SETTINGS_STORAGE,
         'battleEvents': BATTLE_EVENTS_SETTINGS_STORAGE,
         'battleBorderMap': BATTLE_BORDER_MAP_SETTINGS_STORAGE,
         'questsProgress': QUESTS_PROGRESS_SETTINGS_STORAGE}
        self.isDeviseRecreated = False
        self.isChangesConfirmed = True
        graphicSettings = tuple(((settingName, options.GraphicSetting(settingName, settingName == GRAPHICS.COLOR_GRADING_TECHNIQUE)) for settingName in BigWorld.generateGfxSettings()))
        self.__options = options.SettingsContainer(graphicSettings + ((GAME.REPLAY_ENABLED, options.ReplaySetting(GAME.REPLAY_ENABLED, storage=GAME_SETTINGS_STORAGE)),
         (GAME.HANGAR_CAM_PERIOD, options.HangarCamPeriodSetting(GAME.HANGAR_CAM_PERIOD, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.HANGAR_CAM_PARALLAX_ENABLED, options.HangarCamParallaxEnabledSetting(GAME.HANGAR_CAM_PARALLAX_ENABLED, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_SERVER_AIM, options.StorageAccountSetting(GAME.ENABLE_SERVER_AIM, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_DAMAGE_ICON, options.ShowDamageIconSetting(GAME.SHOW_DAMAGE_ICON, storage=GAME_SETTINGS_STORAGE)),
         (GAME.MINIMAP_ALPHA, options.StorageAccountSetting(GAME.MINIMAP_ALPHA, storage=GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_POSTMORTEM_DELAY, options.PostMortemDelaySetting(GAME.ENABLE_POSTMORTEM_DELAY, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_VEHICLES_COUNTER, options.StorageAccountSetting(GAME.SHOW_VEHICLES_COUNTER, storage=GAME_SETTINGS_STORAGE)),
         (GAME.BATTLE_LOADING_INFO, options.BattleLoadingTipSetting(GAME.BATTLE_LOADING_INFO, GAME.BATTLE_LOADING_INFO)),
         (GAME.BATTLE_LOADING_RANKED_INFO, options.BattleLoadingTipSetting(GAME.BATTLE_LOADING_RANKED_INFO, GAME.BATTLE_LOADING_RANKED_INFO)),
         (GAME.SHOW_MARKS_ON_GUN, options.ShowMarksOnGunSetting(GAME.SHOW_MARKS_ON_GUN, storage=MARK_ON_GUN_SETTINGS_STORAGE)),
         (GAME.ANONYMIZER, options.AnonymizerSetting(GAME.ANONYMIZER)),
         (GAME.DYNAMIC_CAMERA, options.DynamicCamera(GAME.DYNAMIC_CAMERA, storage=GAME_SETTINGS_STORAGE)),
         (GAME.INCREASED_ZOOM, options.IncreasedZoomSetting(GAME.INCREASED_ZOOM, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.SNIPER_MODE_BY_SHIFT, options.SniperModeByShiftSetting(GAME.SNIPER_MODE_BY_SHIFT, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_SPEEDOMETER, options.StorageAccountSetting(GAME.ENABLE_SPEEDOMETER, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.SNIPER_MODE_STABILIZATION, options.SniperModeStabilization(GAME.SNIPER_MODE_STABILIZATION, storage=GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_OL_FILTER, options.MessengerSetting(GAME.ENABLE_OL_FILTER, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.ENABLE_SPAM_FILTER, options.MessengerSetting(GAME.ENABLE_SPAM_FILTER, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.SHOW_DATE_MESSAGE, options.MessengerDateTimeSetting(1, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.SHOW_TIME_MESSAGE, options.MessengerDateTimeSetting(2, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.INVITES_FROM_FRIENDS, options.MessengerSetting(GAME.INVITES_FROM_FRIENDS, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS, options.ClansSetting(GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.RECEIVE_FRIENDSHIP_REQUEST, options.MessengerSetting(GAME.RECEIVE_FRIENDSHIP_REQUEST, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.RECEIVE_INVITES_IN_BATTLE, options.MessengerSetting(GAME.RECEIVE_INVITES_IN_BATTLE, storage=EXTENDED_MESSENGER_SETTINGS_STORAGE)),
         (GAME.STORE_RECEIVER_IN_BATTLE, options.MessengerSetting(GAME.STORE_RECEIVER_IN_BATTLE, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.DISABLE_BATTLE_CHAT, options.MessengerSetting(GAME.DISABLE_BATTLE_CHAT, storage=MESSENGER_SETTINGS_STORAGE)),
         (GAME.CHAT_CONTACTS_LIST_ONLY, options.MessengerSetting(GAME.CHAT_CONTACTS_LIST_ONLY, storage=EXTENDED_MESSENGER_SETTINGS_STORAGE)),
         (GAME.PLAYERS_PANELS_SHOW_LEVELS, options.PlayersPanelSetting(GAME.PLAYERS_PANELS_SHOW_LEVELS, 'players_panel', 'showLevels', storage=GAME_SETTINGS_STORAGE)),
         (GAME.PLAYERS_PANELS_SHOW_TYPES, options.AccountDumpSetting(GAME.PLAYERS_PANELS_SHOW_TYPES, 'players_panel', 'showTypes')),
         (GAME.PLAYERS_PANELS_STATE, options.AccountDumpSetting(GAME.PLAYERS_PANELS_STATE, 'players_panel', 'state')),
         (GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE, options.AccountDumpSetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE, 'epic_random_players_panel', 'state')),
         (GAME.SNIPER_MODE_SWINGING_ENABLED, options.SniperModeSwingingSetting()),
         (GAME.GAMEPLAY_CTF, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'ctf', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_DOMINATION, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'domination', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_ASSAULT, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'assault', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_NATIONS, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'nations', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_EPIC_STANDARD, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'ctf30x30', storage=GAMEPLAY_SETTINGS_STORAGE, delegate=_getEpicRandomSwitch)),
         (GAME.GAMEPLAY_EPIC_DOMINATION, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'domination30x30', storage=GAMEPLAY_SETTINGS_STORAGE, delegate=_getEpicRandomSwitch)),
         (GAME.LENS_EFFECT, options.LensEffectSetting(GAME.LENS_EFFECT, storage=GRAPHICS_SETTINGS_STORAGE)),
         (GAME.SHOW_VECTOR_ON_MAP, options.MinimapSetting(GAME.SHOW_VECTOR_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_SECTOR_ON_MAP, options.MinimapSetting(GAME.SHOW_SECTOR_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_VEH_MODELS_ON_MAP, options.MinimapVehModelsSetting(GAME.SHOW_VEH_MODELS_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GAME.MINIMAP_VIEW_RANGE, options.StorageAccountSetting(GAME.MINIMAP_VIEW_RANGE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.MINIMAP_MAX_VIEW_RANGE, options.StorageAccountSetting(GAME.MINIMAP_MAX_VIEW_RANGE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.MINIMAP_DRAW_RANGE, options.StorageAccountSetting(GAME.MINIMAP_DRAW_RANGE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.CAROUSEL_TYPE, options.CarouselTypeSetting(GAME.CAROUSEL_TYPE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.DOUBLE_CAROUSEL_TYPE, options.DoubleCarouselTypeSetting(GAME.DOUBLE_CAROUSEL_TYPE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.VEHICLE_CAROUSEL_STATS, options.VehicleCarouselStatsSetting(GAME.VEHICLE_CAROUSEL_STATS, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.C11N_HISTORICALLY_ACCURATE, options.C11nHistoricallyAccurateSetting(GAME.C11N_HISTORICALLY_ACCURATE, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.LOGIN_SERVER_SELECTION, options.LoginServerSelectionSetting(GAME.LOGIN_SERVER_SELECTION)),
         (GAME.MINIMAP_ALPHA_ENABLED, options.StorageAccountSetting(GAME.MINIMAP_ALPHA_ENABLED, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.LOOT_BOX_VIDEO_OFF, options.StorageAccountSetting(GAME.LOOT_BOX_VIDEO_OFF, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GRAPHICS.MONITOR, options.MonitorSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.WINDOW_SIZE, options.WindowSizeSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.RESOLUTION, options.ResolutionSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.REFRESH_RATE, options.RefreshRateSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.VIDEO_MODE, options.VideoModeSettings(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.BORDERLESS_SIZE, options.BorderlessSizeSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.COLOR_BLIND, options.AccountDumpSetting(GRAPHICS.COLOR_BLIND, GRAPHICS.COLOR_BLIND)),
         (GRAPHICS.TRIPLE_BUFFERED, options.TripleBufferedSetting()),
         (GRAPHICS.VERTICAL_SYNC, options.VerticalSyncSetting()),
         (GRAPHICS.GRAPHICS_QUALITY_HD_SD, options.GraphicsQualityNote()),
         (GRAPHICS.GRAPHICS_QUALITY_HD_SD_HIGH, options.GraphicsHigtQualityNote()),
         (GRAPHICS.GAMMA_SETTING, options.ReadOnlySetting(lambda : SETTINGS.GAMMABTN_LABEL)),
         (GRAPHICS.NATIVE_RESOLUTION, options.ReadOnlySetting(graphics.getNativeResolutionIndex)),
         (GRAPHICS.BRIGHTNESS_CORRECTION, options.BrightnessCorrectionSetting(True)),
         (GRAPHICS.CONTRAST_CORRECTION, options.ContrastCorrectionSetting(True)),
         (GRAPHICS.SATURATION_CORRECTON, options.SaturationCorrectionSetting(True)),
         (GRAPHICS.COLOR_FILTER_INTENSITY, options.ColorFilterIntensitySetting(True)),
         (GRAPHICS.COLOR_FILTER_SETTING, options.ReadOnlySetting(lambda : SETTINGS.COLORCORRECTIONBTN_LABEL)),
         (GRAPHICS.COLOR_FILTER_IMAGES, options.ReadOnlySetting(lambda : graphics.getGraphicSettingImages('COLOR_GRADING_TECHNIQUE'))),
         (GRAPHICS.FOV, options.FOVSetting(GRAPHICS.FOV, storage=FOV_SETTINGS_STORAGE)),
         (GRAPHICS.GRAPHICS_SETTINGS_LIST, options.ReadOnlySetting(graphics.GRAPHICS_SETTINGS.ALL)),
         (GRAPHICS.INTERFACE_SCALE, options.InterfaceScaleSetting(GRAPHICS.INTERFACE_SCALE)),
         (GRAPHICS.DYNAMIC_RENDERER, options.DynamicRendererSetting()),
         (GRAPHICS.DYNAMIC_FOV_ENABLED, options.DynamicFOVEnabledSetting(storage=FOV_SETTINGS_STORAGE)),
         (GRAPHICS.VERTICAL_SYNC, options.VerticalSyncSetting()),
         (GRAPHICS.COLOR_BLIND, options.AccountDumpSetting(GRAPHICS.COLOR_BLIND, GRAPHICS.COLOR_BLIND)),
         (GRAPHICS.TESSELLATION_SUPPORTED, options.ReadOnlySetting(BigWorld.isTesselationSupported)),
         (GRAPHICS.IS_SD_QUALITY, options.GraphicsQuality()),
         (SOUND.MASTER_TOGGLE, options.SoundEnableSetting()),
         (SOUND.SOUND_QUALITY, options.SoundQualitySetting()),
         (SOUND.SOUND_QUALITY_VISIBLE, options.ReadOnlySetting(options.SoundQualitySetting.isAvailable)),
         (SOUND.MASTER, options.SoundSetting('master')),
         (SOUND.MUSIC, options.SoundSetting('music')),
         (SOUND.MUSIC_HANGAR, options.SoundSetting('music_hangar')),
         (SOUND.VOICE_NOTIFICATION, options.SoundSetting('voice')),
         (SOUND.VEHICLES, options.SoundSetting('vehicles')),
         (SOUND.EFFECTS, options.SoundSetting('effects')),
         (SOUND.GUI, options.SoundSetting('gui')),
         (SOUND.AMBIENT, options.SoundSetting('ambient')),
         (SOUND.NATIONS_VOICES, options.AccountSetting('nationalVoices')),
         (SOUND.VOIP_MASTER_FADE, options.SoundSetting('masterFadeVivox')),
         (SOUND.VOIP_ENABLE, options.VOIPSetting(True)),
         (SOUND.VOIP_MASTER, options.VOIPMasterSoundSetting()),
         (SOUND.VOIP_MIC, options.VOIPMicSoundSetting(True)),
         (SOUND.CAPTURE_DEVICES, options.VOIPCaptureDevicesSetting()),
         (SOUND.VOIP_SUPPORTED, options.VOIPSupportSetting()),
         (SOUND.BASS_BOOST, options.BassBoostSetting()),
         (SOUND.NIGHT_MODE, options.NightModeSetting()),
         (SOUND.SOUND_DEVICE, options.SoundDevicePresetSetting(SOUND.SOUND_DEVICE, SOUND.SOUND_DEVICE, isPreview=True)),
         (SOUND.SOUND_SPEAKERS, options.SoundSpeakersPresetSetting(isPreview=True)),
         (SOUND.ALT_VOICES, options.AltVoicesSetting(SOUND.ALT_VOICES, storage=SOUND_SETTINGS_STORAGE)),
         (SOUND.DETECTION_ALERT_SOUND, options.DetectionAlertSound()),
         (SOUND.GAME_EVENT_AMBIENT, options.SoundSetting('ev_ambient')),
         (SOUND.GAME_EVENT_EFFECTS, options.SoundSetting('ev_effects')),
         (SOUND.GAME_EVENT_GUI, options.SoundSetting('ev_gui')),
         (SOUND.GAME_EVENT_MUSIC, options.SoundSetting('ev_music')),
         (SOUND.GAME_EVENT_VEHICLES, options.SoundSetting('ev_vehicles')),
         (SOUND.GAME_EVENT_VOICE, options.SoundSetting('ev_voice')),
         (CONTROLS.MOUSE_ARCADE_SENS, options.MouseSensitivitySetting('arcade')),
         (CONTROLS.MOUSE_SNIPER_SENS, options.MouseSensitivitySetting('sniper')),
         (CONTROLS.MOUSE_SNIPER_SENS, options.MouseSensitivitySetting('dualgun')),
         (CONTROLS.MOUSE_STRATEGIC_SENS, options.MouseSensitivitySetting('strategic')),
         (CONTROLS.MOUSE_ASSIST_AIM_SENS, options.MouseSensitivitySetting('arty', masterSwitch='spgAlternativeAimingCameraEnabled')),
         (CONTROLS.MOUSE_HORZ_INVERSION, options.MouseInversionSetting(CONTROLS.MOUSE_HORZ_INVERSION, 'horzInvert', storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.MOUSE_VERT_INVERSION, options.MouseInversionSetting(CONTROLS.MOUSE_VERT_INVERSION, 'vertInvert', storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.BACK_DRAFT_INVERSION, options.BackDraftInversionSetting(storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.KEYBOARD, options.KeyboardSettings()),
         (CONTROLS.KEYBOARD_IMPORTANT_BINDS, options.ReadOnlySetting(options.KeyboardSettings.getKeyboardImportantBinds)),
         (AIM.ARCADE, options.AimSetting('arcade', storage=AIM_SETTINGS_STORAGE)),
         (AIM.SNIPER, options.AimSetting('sniper', storage=AIM_SETTINGS_STORAGE)),
         (MARKERS.ENEMY, options.VehicleMarkerSetting(MARKERS.ENEMY, storage=MARKERS_SETTINGS_STORAGE)),
         (MARKERS.DEAD, options.VehicleMarkerSetting(MARKERS.DEAD, storage=MARKERS_SETTINGS_STORAGE)),
         (MARKERS.ALLY, options.VehicleMarkerSetting(MARKERS.ALLY, storage=MARKERS_SETTINGS_STORAGE)),
         (OTHER.VIBRO_CONNECTED, options.ReadOnlySetting(VibroManager.g_instance.connect)),
         (OTHER.VIBRO_GAIN, options.VibroSetting('master')),
         (OTHER.VIBRO_ENGINE, options.VibroSetting('engine')),
         (OTHER.VIBRO_ACCELERATION, options.VibroSetting('acceleration')),
         (OTHER.VIBRO_SHOTS, options.VibroSetting('shots')),
         (OTHER.VIBRO_HITS, options.VibroSetting('hits')),
         (OTHER.VIBRO_COLLISIONS, options.VibroSetting('collisions')),
         (OTHER.VIBRO_DAMAGE, options.VibroSetting('damage')),
         (OTHER.VIBRO_GUI, options.VibroSetting('gui')),
         (TUTORIAL.CUSTOMIZATION, options.TutorialSetting(TUTORIAL.CUSTOMIZATION, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.TECHNICAL_MAINTENANCE, options.TutorialSetting(TUTORIAL.TECHNICAL_MAINTENANCE, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.PERSONAL_CASE, options.TutorialSetting(TUTORIAL.PERSONAL_CASE, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.RESEARCH, options.TutorialSetting(TUTORIAL.RESEARCH, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.RESEARCH_TREE, options.TutorialSetting(TUTORIAL.RESEARCH_TREE, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.MEDKIT_USED, options.TutorialSetting(TUTORIAL.MEDKIT_USED, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.REPAIRKIT_USED, options.TutorialSetting(TUTORIAL.REPAIRKIT_USED, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.FIRE_EXTINGUISHER_USED, options.TutorialSetting(TUTORIAL.FIRE_EXTINGUISHER_USED, storage=TUTORIAL_SETTINGS_STORAGE)),
         (TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED, options.TutorialSetting(TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED, storage=TUTORIAL_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.TYPE, options.DamageIndicatorTypeSetting(DAMAGE_INDICATOR.TYPE, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.PRESETS, options.DamageIndicatorPresetsSetting(DAMAGE_INDICATOR.PRESETS, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.DAMAGE_VALUE, options.SettingFalseByDefault(DAMAGE_INDICATOR.DAMAGE_VALUE, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.VEHICLE_INFO, options.SettingFalseByDefault(DAMAGE_INDICATOR.VEHICLE_INFO, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.ANIMATION, options.SettingFalseByDefault(DAMAGE_INDICATOR.ANIMATION, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_INDICATOR.DYNAMIC_INDICATOR, options.SettingFalseByDefault(DAMAGE_INDICATOR.DYNAMIC_INDICATOR, storage=DAMAGE_INDICATOR_SETTINGS_STORAGE)),
         (DAMAGE_LOG.TOTAL_DAMAGE, options.SettingFalseByDefault(DAMAGE_LOG.TOTAL_DAMAGE, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (DAMAGE_LOG.BLOCKED_DAMAGE, options.SettingFalseByDefault(DAMAGE_LOG.BLOCKED_DAMAGE, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (DAMAGE_LOG.ASSIST_DAMAGE, options.SettingFalseByDefault(DAMAGE_LOG.ASSIST_DAMAGE, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (DAMAGE_LOG.ASSIST_STUN, options.BattleEventsSetting(DAMAGE_LOG.ASSIST_STUN, storage=DAMAGE_LOG_SETTINGS_STORAGE, delegate=_getStunSwitch)),
         (DAMAGE_LOG.SHOW_DETAILS, options.DamageLogDetailsSetting(DAMAGE_LOG.SHOW_DETAILS, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (DAMAGE_LOG.SHOW_EVENT_TYPES, options.DamageLogEventTypesSetting(DAMAGE_LOG.SHOW_EVENT_TYPES, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (DAMAGE_LOG.EVENT_POSITIONS, options.DamageLogEventPositionsSetting(DAMAGE_LOG.EVENT_POSITIONS, storage=DAMAGE_LOG_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.SHOW_IN_BATTLE, options.SettingFalseByDefault(BATTLE_EVENTS.SHOW_IN_BATTLE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_HP_DAMAGE, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_HP_DAMAGE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_BURNING, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_BURNING, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_RAM_ATTACK, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_RAM_ATTACK, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.BLOCKED_DAMAGE, options.SettingFalseByDefault(BATTLE_EVENTS.BLOCKED_DAMAGE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_TRACK_DAMAGE, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_TRACK_DAMAGE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_DETECTION, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_DETECTION, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_KILL, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_KILL, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.BASE_CAPTURE_DROP, options.SettingFalseByDefault(BATTLE_EVENTS.BASE_CAPTURE_DROP, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.BASE_CAPTURE, options.SettingFalseByDefault(BATTLE_EVENTS.BASE_CAPTURE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_CRITICAL_HIT, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_CRITICAL_HIT, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.EVENT_NAME, options.SettingFalseByDefault(BATTLE_EVENTS.EVENT_NAME, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.VEHICLE_INFO, options.SettingFalseByDefault(BATTLE_EVENTS.VEHICLE_INFO, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_WORLD_COLLISION, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMY_WORLD_COLLISION, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.RECEIVED_DAMAGE, options.SettingFalseByDefault(BATTLE_EVENTS.RECEIVED_DAMAGE, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.RECEIVED_CRITS, options.SettingFalseByDefault(BATTLE_EVENTS.RECEIVED_CRITS, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_EVENTS.ENEMY_ASSIST_STUN, options.BattleEventsSetting(BATTLE_EVENTS.ENEMY_ASSIST_STUN, storage=BATTLE_EVENTS_SETTINGS_STORAGE, delegate=_getStunSwitch)),
         (BATTLE_EVENTS.ENEMIES_STUN, options.SettingFalseByDefault(BATTLE_EVENTS.ENEMIES_STUN, storage=BATTLE_EVENTS_SETTINGS_STORAGE)),
         (BATTLE_BORDER_MAP.MODE_SHOW_BORDER, options.BattleBorderMapModeShow(BATTLE_BORDER_MAP.MODE_SHOW_BORDER, storage=BATTLE_BORDER_MAP_SETTINGS_STORAGE)),
         (BATTLE_BORDER_MAP.TYPE_BORDER, options.BattleBorderMapType(BATTLE_BORDER_MAP.TYPE_BORDER, storage=BATTLE_BORDER_MAP_SETTINGS_STORAGE)),
         (QUESTS_PROGRESS.VIEW_TYPE, options.QuestsProgressViewType(QUESTS_PROGRESS.VIEW_TYPE, storage=QUESTS_PROGRESS_SETTINGS_STORAGE)),
         (QUESTS_PROGRESS.DISPLAY_TYPE, options.QuestsProgressDisplayType(QUESTS_PROGRESS.DISPLAY_TYPE, storage=QUESTS_PROGRESS_SETTINGS_STORAGE))))
        self.__options.init()
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self.interfaceScale.init()
        LOG_DEBUG('SettingsCore is created')

    def fini(self):
        if self.__options is not None:
            self.__options.dump()
            self.__options.fini()
            self.__options = None
        self.__storages = None
        self.__serverSettings = None
        if self.__interfaceScale is not None:
            self.__interfaceScale.fini()
            self.__interfaceScale = None
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        AccountSettings.clearCache()
        LOG_DEBUG('SettingsCore is destroyed')
        return

    @property
    def options(self):
        return self.__options

    @property
    def storages(self):
        return self.__storages

    @property
    def interfaceScale(self):
        return self.__interfaceScale

    @property
    def serverSettings(self):
        return self.__serverSettings

    def packSettings(self, names):
        return self.__options.pack(names)

    def getSetting(self, name):
        return self.__options.getSetting(name).get()

    def getApplyMethod(self, diff):
        return self.__options.getApplyMethod(diff)

    def applySetting(self, key, value):
        if self.isSettingChanged(key, value):
            result = self.__options.getSetting(key).apply(value)
            from account_helpers.settings_core import settings_constants
            if key in settings_constants.GRAPHICS.ALL():
                LOG_DEBUG('Apply graphic settings: ', {key: value})
                self.onSettingsChanged({key: value})
            if key in settings_constants.GAME.LOOT_BOX_VIDEO_OFF:
                self.onSettingsChanged({key: value})
            return result
        else:
            return None

    def previewSetting(self, name, value):
        if self.isSettingChanged(name, value):
            self.__options.getSetting(name).preview(value)

    def applySettings(self, diff):
        self.__options.apply(diff)
        self.onSettingsApplied(diff)
        from account_helpers.settings_core import settings_constants
        graphicsSettings = {k:v for k, v in diff.iteritems() if k in settings_constants.GRAPHICS.ALL()}
        if graphicsSettings:
            LOG_DEBUG('Apply graphic settings: ', graphicsSettings)
            self.onSettingsChanged(graphicsSettings)
            BigWorld.updateCurrentPresetIndex()

    def revertSettings(self):
        self.__options.revert()

    def isSettingChanged(self, name, value):
        return not self.__options.getSetting(name).isEqual(value)

    def applyStorages(self, restartApproved):
        confirmators = []
        for storage in self.__storages.values():
            confirmators.append(storage.apply(restartApproved))

        return confirmators

    @process
    def confirmChanges(self, confirmators):
        yield lambda callback: callback(None)
        for confirmation, revert in confirmators:
            if confirmation is not None:
                isConfirmed = yield confirmation()
                if not isConfirmed:
                    self.isChangesConfirmed = False
                    revert()

        return

    def clearStorages(self):
        for storage in self.__storages.values():
            storage.clear()

    def __onAccountSettingsChanging(self, key, value):
        LOG_DEBUG('Apply account setting: ', {key: value})
        self.onSettingsChanged({key: value})
