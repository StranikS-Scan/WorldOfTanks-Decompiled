# Embedded file name: scripts/client/account_helpers/settings_core/SettingsCore.py
import Event
from InterfaceScaleManager import InterfaceScaleManager
from Vibroeffects import VibroManager
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.ServerSettingsManager import ServerSettingsManager
from adisp import process
from debug_utils import LOG_DEBUG

class _SettingsCore(object):
    onSettingsChanged = Event.Event()

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
        self.__serverSettings = ServerSettingsManager(self)
        self.interfaceScale = InterfaceScaleManager(self)
        VIDEO_SETTINGS_STORAGE = settings_storages.VideoSettingsStorage(self.serverSettings, self)
        GAME_SETTINGS_STORAGE = settings_storages.GameSettingsStorage(self.serverSettings, self)
        EXTENDED_GAME_SETTINGS_STORAGE = settings_storages.ExtendedGameSettingsStorage(self.serverSettings, self)
        TUTORIAL_SETTINGS_STORAGE = settings_storages.TutorialStorage(self.serverSettings, self)
        GAMEPLAY_SETTINGS_STORAGE = settings_storages.GameplaySettingsStorage(self.serverSettings, self)
        GRAPHICS_SETTINGS_STORAGE = settings_storages.GraphicsSettingsStorage(self.serverSettings, self)
        SOUND_SETTINGS_STORAGE = settings_storages.SoundSettingsStorage(self.serverSettings, self)
        KEYBOARD_SETTINGS_STORAGE = settings_storages.KeyboardSettingsStorage(self.serverSettings, self)
        CONTROLS_SETTINGS_STORAGE = settings_storages.ControlsSettingsStorage(self.serverSettings, self)
        AIM_SETTINGS_STORAGE = settings_storages.AimSettingsStorage(self.serverSettings, self)
        MARKERS_SETTINGS_STORAGE = settings_storages.MarkersSettingsStorage(self.serverSettings, self)
        MARK_ON_GUN_SETTINGS_STORAGE = settings_storages.MarksOnGunSettingsStorage(self.serverSettings, self)
        FOV_SETTINGS_STORAGE = settings_storages.FOVSettingsStorage(self.serverSettings, self)
        MESSENGER_SETTINGS_STORAGE = settings_storages.MessengerSettingsStorage(GAME_SETTINGS_STORAGE)
        EXTENDED_MESSENGER_SETTINGS_STORAGE = settings_storages.MessengerSettingsStorage(EXTENDED_GAME_SETTINGS_STORAGE)
        self.__storages = {'game': GAME_SETTINGS_STORAGE,
         'extendedGame': EXTENDED_GAME_SETTINGS_STORAGE,
         'gameplay': GAMEPLAY_SETTINGS_STORAGE,
         'sound': SOUND_SETTINGS_STORAGE,
         'keyboard': KEYBOARD_SETTINGS_STORAGE,
         'controls': CONTROLS_SETTINGS_STORAGE,
         'aim': AIM_SETTINGS_STORAGE,
         'markers': MARKERS_SETTINGS_STORAGE,
         'graphics': GRAPHICS_SETTINGS_STORAGE,
         'video': VIDEO_SETTINGS_STORAGE,
         'messenger': MESSENGER_SETTINGS_STORAGE,
         'extendedMessenger': EXTENDED_MESSENGER_SETTINGS_STORAGE,
         'marksOnGun': MARK_ON_GUN_SETTINGS_STORAGE,
         'FOV': FOV_SETTINGS_STORAGE,
         'tutorial': TUTORIAL_SETTINGS_STORAGE}
        self.isDeviseRecreated = False
        self.isChangesConfirmed = True
        self.__options = options.SettingsContainer(((GAME.REPLAY_ENABLED, options.ReplaySetting(GAME.REPLAY_ENABLED, storage=GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_SERVER_AIM, options.StorageAccountSetting(GAME.ENABLE_SERVER_AIM, storage=GAME_SETTINGS_STORAGE)),
         (GAME.MINIMAP_ALPHA, options.StorageAccountSetting(GAME.MINIMAP_ALPHA, storage=GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_POSTMORTEM, options.PostProcessingSetting(GAME.ENABLE_POSTMORTEM, 'mortem_post_effect', storage=GAME_SETTINGS_STORAGE)),
         (GAME.ENABLE_POSTMORTEM_DELAY, options.PostMortemDelaySetting(GAME.ENABLE_POSTMORTEM_DELAY, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_VEHICLES_COUNTER, options.StorageAccountSetting(GAME.SHOW_VEHICLES_COUNTER, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS, options.ExcludeInReplayAccountSetting(GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS, storage=EXTENDED_GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_MARKS_ON_GUN, options.ShowMarksOnGunSetting(GAME.SHOW_MARKS_ON_GUN, storage=MARK_ON_GUN_SETTINGS_STORAGE)),
         (GAME.DYNAMIC_CAMERA, options.DynamicCamera(GAME.DYNAMIC_CAMERA, storage=GAME_SETTINGS_STORAGE)),
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
         (GAME.SNIPER_MODE_SWINGING_ENABLED, options.SniperModeSwingingSetting()),
         (GAME.GAMEPLAY_CTF, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'ctf', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_DOMINATION, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'domination', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_ASSAULT, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'assault', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.GAMEPLAY_NATIONS, options.GameplaySetting(GAME.GAMEPLAY_MASK, 'nations', storage=GAMEPLAY_SETTINGS_STORAGE)),
         (GAME.LENS_EFFECT, options.LensEffectSetting(GAME.LENS_EFFECT, storage=GRAPHICS_SETTINGS_STORAGE)),
         (GAME.SHOW_VECTOR_ON_MAP, options.MinimapSetting(GAME.SHOW_VECTOR_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_SECTOR_ON_MAP, options.MinimapSetting(GAME.SHOW_SECTOR_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GAME.SHOW_VEH_MODELS_ON_MAP, options.MinimapVehModelsSetting(GAME.SHOW_VEH_MODELS_ON_MAP, storage=GAME_SETTINGS_STORAGE)),
         (GRAPHICS.MONITOR, options.MonitorSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.WINDOW_SIZE, options.WindowSizeSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.RESOLUTION, options.ResolutionSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.REFRESH_RATE, options.RefreshRateSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.FULLSCREEN, options.FullscreenSetting(storage=VIDEO_SETTINGS_STORAGE)),
         (GRAPHICS.COLOR_BLIND, options.AccountDumpSetting(GRAPHICS.COLOR_BLIND, GRAPHICS.COLOR_BLIND)),
         (GRAPHICS.GRAPHICS_QUALITY_HD_SD, options.GraphicsQualityNote()),
         (GRAPHICS.GAMMA, options.GammaSetting()),
         (GRAPHICS.TRIPLE_BUFFERED, options.TripleBufferedSetting()),
         (GRAPHICS.VERTICAL_SYNC, options.VerticalSyncSetting()),
         (GRAPHICS.MULTISAMPLING, options.MultisamplingSetting()),
         (GRAPHICS.CUSTOM_AA, options.CustomAASetting()),
         (GRAPHICS.ASPECT_RATIO, options.AspectRatioSetting()),
         (GRAPHICS.FPS_PERFOMANCER, options.FPSPerfomancerSetting(GRAPHICS.FPS_PERFOMANCER, storage=GRAPHICS_SETTINGS_STORAGE)),
         (GRAPHICS.DRR_AUTOSCALER_ENABLED, options.GraphicSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED)),
         (GRAPHICS.DYNAMIC_RENDERER, options.DynamicRendererSetting()),
         (GRAPHICS.COLOR_FILTER_INTENSITY, options.ColorFilterIntensitySetting()),
         (GRAPHICS.COLOR_FILTER_IMAGES, options.ReadOnlySetting(lambda : graphics.getGraphicSettingImages(GRAPHICS.COLOR_GRADING_TECHNIQUE))),
         (GRAPHICS.FOV, options.FOVSetting(GRAPHICS.FOV, storage=FOV_SETTINGS_STORAGE)),
         (GRAPHICS.DYNAMIC_FOV_ENABLED, options.DynamicFOVEnabledSetting(storage=FOV_SETTINGS_STORAGE)),
         (GRAPHICS.PRESETS, options.GraphicsPresetSetting()),
         (GRAPHICS.RENDER_PIPELINE, options.GraphicSetting(GRAPHICS.RENDER_PIPELINE)),
         (GRAPHICS.TEXTURE_QUALITY, options.TextureQualitySetting()),
         (GRAPHICS.DECALS_QUALITY, options.GraphicSetting(GRAPHICS.DECALS_QUALITY)),
         (GRAPHICS.OBJECT_LOD, options.GraphicSetting(GRAPHICS.OBJECT_LOD)),
         (GRAPHICS.FAR_PLANE, options.GraphicSetting(GRAPHICS.FAR_PLANE)),
         (GRAPHICS.TERRAIN_QUALITY, options.TerrainQualitySetting()),
         (GRAPHICS.SHADOWS_QUALITY, options.GraphicSetting(GRAPHICS.SHADOWS_QUALITY)),
         (GRAPHICS.LIGHTING_QUALITY, options.GraphicSetting(GRAPHICS.LIGHTING_QUALITY)),
         (GRAPHICS.SPEEDTREE_QUALITY, options.GraphicSetting(GRAPHICS.SPEEDTREE_QUALITY)),
         (GRAPHICS.FLORA_QUALITY, options.FloraQualitySetting()),
         (GRAPHICS.WATER_QUALITY, options.GraphicSetting(GRAPHICS.WATER_QUALITY)),
         (GRAPHICS.EFFECTS_QUALITY, options.GraphicSetting(GRAPHICS.EFFECTS_QUALITY)),
         (GRAPHICS.POST_PROCESSING_QUALITY, options.GraphicSetting(GRAPHICS.POST_PROCESSING_QUALITY)),
         (GRAPHICS.MOTION_BLUR_QUALITY, options.GraphicSetting(GRAPHICS.MOTION_BLUR_QUALITY)),
         (GRAPHICS.SNIPER_MODE_EFFECTS_QUALITY, options.GraphicSetting(GRAPHICS.SNIPER_MODE_EFFECTS_QUALITY)),
         (GRAPHICS.VEHICLE_DUST_ENABLED, options.GraphicSetting(GRAPHICS.VEHICLE_DUST_ENABLED)),
         (GRAPHICS.SNIPER_MODE_GRASS_ENABLED, options.GraphicSetting(GRAPHICS.SNIPER_MODE_GRASS_ENABLED)),
         (GRAPHICS.VEHICLE_TRACES_ENABLED, options.GraphicSetting(GRAPHICS.VEHICLE_TRACES_ENABLED)),
         (GRAPHICS.COLOR_GRADING_TECHNIQUE, options.GraphicSetting(GRAPHICS.COLOR_GRADING_TECHNIQUE)),
         (GRAPHICS.SEMITRANSPARENT_LEAVES_ENABLED, options.GraphicSetting(GRAPHICS.SEMITRANSPARENT_LEAVES_ENABLED)),
         (GRAPHICS.GRAPHICS_SETTINGS_LIST, options.ReadOnlySetting(lambda : graphics.GRAPHICS_SETTINGS.ALL())),
         (GRAPHICS.INTERFACE_SCALE, options.InterfaceScaleSetting(GRAPHICS.INTERFACE_SCALE)),
         (SOUND.MASTER, options.SoundSetting('master')),
         (SOUND.MUSIC, options.SoundSetting('music')),
         (SOUND.VOICE, options.SoundSetting('voice')),
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
         (SOUND.ALT_VOICES, options.AltVoicesSetting(SOUND.ALT_VOICES, storage=SOUND_SETTINGS_STORAGE)),
         (CONTROLS.MOUSE_ARCADE_SENS, options.MouseSensitivitySetting('arcade')),
         (CONTROLS.MOUSE_SNIPER_SENS, options.MouseSensitivitySetting('sniper')),
         (CONTROLS.MOUSE_STRATEGIC_SENS, options.MouseSensitivitySetting('strategic')),
         (CONTROLS.MOUSE_HORZ_INVERSION, options.MouseInversionSetting(CONTROLS.MOUSE_HORZ_INVERSION, 'horzInvert', storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.MOUSE_VERT_INVERSION, options.MouseInversionSetting(CONTROLS.MOUSE_VERT_INVERSION, 'vertInvert', storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.BACK_DRAFT_INVERSION, options.BackDraftInversionSetting(storage=CONTROLS_SETTINGS_STORAGE)),
         (CONTROLS.KEYBOARD, options.KeyboardSettings(storage=KEYBOARD_SETTINGS_STORAGE)),
         (AIM.ARCADE, options.AimSetting('arcade', storage=AIM_SETTINGS_STORAGE)),
         (AIM.SNIPER, options.AimSetting('sniper', storage=AIM_SETTINGS_STORAGE)),
         (MARKERS.ENEMY, options.VehicleMarkerSetting(MARKERS.ENEMY, storage=MARKERS_SETTINGS_STORAGE)),
         (MARKERS.DEAD, options.VehicleMarkerSetting(MARKERS.DEAD, storage=MARKERS_SETTINGS_STORAGE)),
         (MARKERS.ALLY, options.VehicleMarkerSetting(MARKERS.ALLY, storage=MARKERS_SETTINGS_STORAGE)),
         (OTHER.VIBRO_CONNECTED, options.ReadOnlySetting(lambda : VibroManager.g_instance.connect())),
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
         (TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED, options.TutorialSetting(TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED, storage=TUTORIAL_SETTINGS_STORAGE))))
        self.__options.init()
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self.interfaceScale.init()
        LOG_DEBUG('SettingsCore is initialized')

    def fini(self):
        self.options.dump()
        self.__storages = None
        self.__options = None
        self.__serverSettings = None
        self.interfaceScale.fini()
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
            return result
        else:
            return None

    def previewSetting(self, name, value):
        if self.isSettingChanged(name, value):
            self.__options.getSetting(name).preview(value)

    def applySettings(self, diff):
        self.__options.apply(diff)
        from account_helpers.settings_core import settings_constants
        graphicsSettings = {k:v for k, v in diff.iteritems() if k in settings_constants.GRAPHICS.ALL()}
        if graphicsSettings:
            LOG_DEBUG('Apply graphic settings: ', graphicsSettings)
            self.onSettingsChanged(graphicsSettings)

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


g_settingsCore = _SettingsCore()
