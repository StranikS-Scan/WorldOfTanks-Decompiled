# Embedded file name: scripts/client/account_helpers/settings_core/ServerSettingsManager.py
import weakref
from collections import namedtuple
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCache import g_settingsCache
from account_helpers.settings_core.migrations import migrateToVersion
from account_helpers.settings_core.settings_constants import TUTORIAL
from adisp import process, async
from debug_utils import LOG_ERROR, LOG_DEBUG
from shared_utils import CONST_CONTAINER

class SETTINGS_SECTIONS(CONST_CONTAINER):
    GAME = 'GAME'
    GAME_EXTENDED = 'GAME_EXTENDED'
    GAMEPLAY = 'GAMEPLAY'
    GRAPHICS = 'GRAPHICS'
    SOUND = 'SOUND'
    CONTROLS = 'CONTROLS'
    AIM_1 = 'AIM_1'
    AIM_2 = 'AIM_2'
    AIM_3 = 'AIM_3'
    MARKERS = 'MARKERS'
    CAROUSEL_FILTER = 'CAROUSEL_FILTER'
    FALLOUT_CAROUSEL_FILTER = 'FALLOUT_CAROUSEL_FILTER'
    GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
    EULA_VERSION = 'EULA_VERSION'
    MARKS_ON_GUN = 'MARKS_ON_GUN'
    CONTACTS = 'CONTACTS'
    FALLOUT = 'FALLOUT'
    TUTORIAL = 'TUTORIAL'
    ONCE_ONLY_HINTS = 'ONCE_ONLY_HINTS'


class ServerSettingsManager(object):
    __version = 17
    GAME = settings_constants.GAME
    GRAPHICS = settings_constants.GRAPHICS
    SOUND = settings_constants.SOUND
    CONTROLS = settings_constants.CONTROLS
    Section = namedtuple('Section', ['masks', 'offsets'])
    Offset = namedtuple('Offset', ['offset', 'mask'])
    CONTACTS = settings_constants.CONTACTS
    SECTIONS = {SETTINGS_SECTIONS.GAME: Section(masks={GAME.ENABLE_OL_FILTER: 0,
                              GAME.ENABLE_SPAM_FILTER: 1,
                              GAME.INVITES_FROM_FRIENDS: 2,
                              GAME.STORE_RECEIVER_IN_BATTLE: 3,
                              GAME.PLAYERS_PANELS_SHOW_LEVELS: 4,
                              GAME.ENABLE_POSTMORTEM: 5,
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
     SETTINGS_SECTIONS.GAME_EXTENDED: Section(masks={GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS: 0,
                                       GAME.CHAT_CONTACTS_LIST_ONLY: 1,
                                       GAME.RECEIVE_INVITES_IN_BATTLE: 2,
                                       GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS: 3}, offsets={}),
     SETTINGS_SECTIONS.GAMEPLAY: Section(masks={}, offsets={GAME.GAMEPLAY_MASK: Offset(0, 65535)}),
     SETTINGS_SECTIONS.GRAPHICS: Section(masks={GRAPHICS.FPS_PERFOMANCER: 0,
                                  GAME.LENS_EFFECT: 1}, offsets={}),
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
     SETTINGS_SECTIONS.MARKERS: Section(masks={'markerBaseIcon': 0,
                                 'markerBaseLevel': 1,
                                 'markerBaseHpIndicator': 2,
                                 'markerBaseDamage': 3,
                                 'markerBaseVehicleName': 4,
                                 'markerBasePlayerName': 5,
                                 'markerAltIcon': 16,
                                 'markerAltLevel': 17,
                                 'markerAltHpIndicator': 18,
                                 'markerAltDamage': 19,
                                 'markerAltVehicleName': 20,
                                 'markerAltPlayerName': 21}, offsets={'markerBaseHp': Offset(8, 65280),
                                 'markerAltHp': Offset(24, 4278190080L)}),
     SETTINGS_SECTIONS.CAROUSEL_FILTER: Section(masks={'ready': 1,
                                         'nationIsNegative': 2,
                                         'tankTypeIsNegative': 3,
                                         'gameModeFilter': 4}, offsets={'nation': Offset(8, 65280),
                                         'tankType': Offset(16, 16711680)}),
     SETTINGS_SECTIONS.FALLOUT_CAROUSEL_FILTER: Section(masks={'ready': 1,
                                                 'nationIsNegative': 2,
                                                 'tankTypeIsNegative': 3,
                                                 'gameModeFilter': 4}, offsets={'nation': Offset(8, 65280),
                                                 'tankType': Offset(16, 16711680)}),
     SETTINGS_SECTIONS.GUI_START_BEHAVIOR: Section(masks={'isFreeXPInfoDialogShowed': 0}, offsets={}),
     SETTINGS_SECTIONS.EULA_VERSION: Section(masks={}, offsets={'version': Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.MARKS_ON_GUN: Section(masks={}, offsets={GAME.SHOW_MARKS_ON_GUN: Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.CONTACTS: Section(masks={CONTACTS.SHOW_OFFLINE_USERS: 0,
                                  CONTACTS.SHOW_OTHERS_CATEGORY: 1}, offsets={}),
     SETTINGS_SECTIONS.FALLOUT: Section(masks={'isEnabled': 3,
                                 'isAutomatch': 4,
                                 'hasVehicleLvl8': 5,
                                 'hasVehicleLvl10': 6}, offsets={'falloutBattleType': Offset(0, 3)}),
     SETTINGS_SECTIONS.TUTORIAL: Section(masks={TUTORIAL.CUSTOMIZATION: 0,
                                  TUTORIAL.TECHNICAL_MAINTENANCE: 1,
                                  TUTORIAL.PERSONAL_CASE: 2,
                                  TUTORIAL.RESEARCH: 3,
                                  TUTORIAL.RESEARCH_TREE: 4,
                                  TUTORIAL.MEDKIT_USED: 6,
                                  TUTORIAL.REPAIRKIT_USED: 8,
                                  TUTORIAL.FIRE_EXTINGUISHER_USED: 10,
                                  TUTORIAL.WAS_QUESTS_TUTORIAL_STARTED: 11}, offsets={}),
     SETTINGS_SECTIONS.ONCE_ONLY_HINTS: Section(masks={'FalloutQuestsTab': 0}, offsets={})}
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
     'reloaderTimer': 3}

    def __init__(self, core):
        self._core = weakref.proxy(core)

    @property
    def version(self):
        return self.__version

    @process
    def applySettings(self):
        import BattleReplay
        if not BattleReplay.isPlaying():
            yield self._updateToVersion()
        self._core.options.refresh()
        enableDynamicCamera = self._core.options.getSetting(self.GAME.DYNAMIC_CAMERA)
        enableDynamicCameraValue = enableDynamicCamera.get()
        enableSniperStabilization = self._core.options.getSetting(self.GAME.SNIPER_MODE_STABILIZATION)
        enableSniperStabilizationValue = enableSniperStabilization.get()
        from AvatarInputHandler import AvatarInputHandler
        AvatarInputHandler.enableDynamicCamera(enableDynamicCameraValue, enableSniperStabilizationValue)
        from messenger.doc_loaders import user_prefs
        from messenger import g_settings as messenger_settings
        user_prefs.loadFromServer(messenger_settings)
        self._core.storages.get('FOV').apply(False, True)

    def getGameSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.GAME, key, default)

    def setGameSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.GAME, settings)

    def getExtendedGameSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, key, default)

    def setExtendedGameSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, settings)

    def getTutorialSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.TUTORIAL, key, default)

    def setTutorialSetting(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.TUTORIAL, settings)

    def getGameplaySetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, key, default)

    def setGameplaySettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, settings)

    def getGraphicsSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.GRAPHICS, key, default)

    def setGraphicsSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.GRAPHICS, settings)

    def getSoundSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.SOUND, key, default)

    def setSoundSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.SOUND, settings)

    def getControlsSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.CONTROLS, key, default)

    def setControlsSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.CONTROLS, settings)

    def getAimSetting(self, section, key, default = None):
        number = self.AIM_MAPPING[key]
        storageKey = 'AIM_%(section)s_%(number)d' % {'section': section.upper(),
         'number': number}
        settingsKey = 'AIM_%(number)d' % {'number': number}
        storedValue = g_settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[settingsKey].masks
        offsets = self.SECTIONS[settingsKey].offsets
        if storedValue is not None:
            return self._extractValue(key, storedValue, default, masks, offsets)
        else:
            return default

    def getOnceOnlyHintsSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, key, default)

    def getOnceOnlyHintsSettings(self):
        return self.getSection(SETTINGS_SECTIONS.ONCE_ONLY_HINTS)

    def setOnceOnlyHintsSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, settings)

    def _buildAimSettings(self, settings):
        settingToServer = {}
        for section, options in settings.iteritems():
            mapping = {}
            for key, value in options.iteritems():
                number = self.AIM_MAPPING[key]
                mapping.setdefault(number, {})[key] = value

            for number, value in mapping.iteritems():
                settingsKey = 'AIM_%(number)d' % {'number': number}
                storageKey = 'AIM_%(section)s_%(number)d' % {'section': section.upper(),
                 'number': number}
                storingValue = storedValue = g_settingsCache.getSetting(storageKey)
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
        g_settingsCache.setSettings(storingValue)
        self.setVersion()
        self._core.onSettingsChanged(settings)

    def getMarkersSetting(self, section, key, default = None):
        storageKey = 'MARKERS_%(section)s' % {'section': section.upper()}
        storedValue = g_settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].masks
        offsets = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].offsets
        if storedValue is not None:
            return self._extractValue(key, storedValue, default, masks, offsets)
        else:
            return default

    def _buildMarkersSettings(self, settings):
        settingToServer = {}
        for section, options in settings.iteritems():
            storageKey = 'MARKERS_%(section)s' % {'section': section.upper()}
            storingValue = storedValue = g_settingsCache.getSetting(storageKey)
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
        g_settingsCache.setSettings(storingValue)
        self.setVersion()
        self._core.onSettingsChanged(settings)

    def setVersion(self):
        if g_settingsCache.getVersion() != self.__version:
            g_settingsCache.setVersion(self.__version)

    def getVersion(self):
        return g_settingsCache.getVersion()

    def setSettings(self, settings):
        g_settingsCache.setSettings(settings)
        self.setVersion()
        self._core.onSettingsChanged(settings)

    def getSetting(self, key, default = None):
        return g_settingsCache.getSetting(key, default)

    def getSection(self, section, defaults = None):
        result = {}
        defaults = defaults or {}
        masks = self.SECTIONS[section].masks
        offsets = self.SECTIONS[section].offsets
        for m in masks:
            default = defaults.get(m, None)
            result[m] = self._getSectionSettings(section, m, default)

        for o in offsets:
            default = defaults.get(o, None)
            result[o] = self._getSectionSettings(section, o, default)

        return result

    def setSection(self, section, settings):
        if section in self.SECTIONS:
            self._setSectionSettings(section, settings)

    def getMarksOnGunSetting(self, key, default = None):
        return self._getSectionSettings(SETTINGS_SECTIONS.MARKS_ON_GUN, key, default)

    def setMarksOnGunSettings(self, settings):
        self._setSectionSettings(SETTINGS_SECTIONS.MARKS_ON_GUN, settings)

    def _getSectionSettings(self, section, key, default = None):
        storedValue = g_settingsCache.getSectionSettings(section, None)
        masks = self.SECTIONS[section].masks
        offsets = self.SECTIONS[section].offsets
        if storedValue is not None:
            return self._extractValue(key, storedValue, default, masks, offsets)
        else:
            return default

    def _buildSectionSettings(self, section, settings):
        storedValue = g_settingsCache.getSectionSettings(section, None)
        storingValue = storedValue if storedValue is not None else 0
        masks = self.SECTIONS[section].masks
        offsets = self.SECTIONS[section].offsets
        return self._mapValues(settings, storingValue, masks, offsets)

    def _setSectionSettings(self, section, settings):
        storedValue = g_settingsCache.getSectionSettings(section, None)
        storingValue = self._buildSectionSettings(section, settings)
        if storedValue == storingValue:
            return
        else:
            LOG_DEBUG('Applying %s server settings: ' % section, settings)
            g_settingsCache.setSectionSettings(section, storingValue)
            self.setVersion()
            self._core.onSettingsChanged(settings)
            return

    def _extractValue(self, key, storedValue, default, masks, offsets):
        if key in masks:
            return storedValue >> masks[key] & 1
        elif key in offsets:
            return (storedValue & offsets[key].mask) >> offsets[key].offset
        else:
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

    @async
    @process
    def _updateToVersion(self, callback = None):
        currentVersion = g_settingsCache.getVersion()
        data = {'gameData': {},
         'gameExtData': {},
         'gameplayData': {},
         'controlsData': {},
         'aimData': {},
         'markersData': {},
         'keyboardData': {},
         'graphicsData': {},
         'marksOnGun': {},
         'clear': {}}
        yield migrateToVersion(currentVersion, self._core, data)
        self._setSettingsSections(**data)
        callback(self)

    def _setSettingsSections(self, gameData, gameExtData, gameplayData, controlsData, aimData, markersData, keyboardData, graphicsData, marksOnGun, clear):
        settings = {}
        clearGame = clear.get(SETTINGS_SECTIONS.GAME, 0)
        if gameData or clearGame:
            settings[SETTINGS_SECTIONS.GAME] = self._buildSectionSettings(SETTINGS_SECTIONS.GAME, gameData) ^ clearGame
        clearGameExt = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
        if gameExtData or clearGameExt:
            settings[SETTINGS_SECTIONS.GAME_EXTENDED] = self._buildSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, gameExtData) ^ clearGameExt
        clearGameplay = clear.get(SETTINGS_SECTIONS.GAMEPLAY, 0)
        if gameplayData or clearGameplay:
            settings[SETTINGS_SECTIONS.GAMEPLAY] = self._buildSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, gameplayData) ^ clearGameplay
        clearControls = clear.get(SETTINGS_SECTIONS.CONTROLS, 0)
        if controlsData or clearControls:
            settings[SETTINGS_SECTIONS.CONTROLS] = self._buildSectionSettings(SETTINGS_SECTIONS.CONTROLS, controlsData) ^ clearControls
        clearGraphics = clear.get(SETTINGS_SECTIONS.GRAPHICS, 0)
        if graphicsData or clearGraphics:
            settings[SETTINGS_SECTIONS.GRAPHICS] = self._buildSectionSettings(SETTINGS_SECTIONS.GRAPHICS, graphicsData) ^ clearGraphics
        if aimData:
            settings.update(self._buildAimSettings(aimData))
        if markersData:
            settings.update(self._buildMarkersSettings(markersData))
        if keyboardData:
            settings.update(keyboardData)
        if marksOnGun:
            settings[SETTINGS_SECTIONS.MARKS_ON_GUN] = self._buildSectionSettings(SETTINGS_SECTIONS.MARKS_ON_GUN, marksOnGun)
        if settings:
            self.setSettings(settings)
