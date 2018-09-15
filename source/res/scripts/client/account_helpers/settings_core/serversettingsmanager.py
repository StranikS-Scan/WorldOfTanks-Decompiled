# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/ServerSettingsManager.py
import weakref
from collections import namedtuple
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.migrations import migrateToVersion
from account_helpers.settings_core.settings_constants import TUTORIAL, VERSION
from adisp import process, async
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCache

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
    AIM_4 = 'AIM_4'
    MARKERS = 'MARKERS'
    CAROUSEL_FILTER_1 = 'CAROUSEL_FILTER_1'
    CAROUSEL_FILTER_2 = 'CAROUSEL_FILTER_2'
    FALLOUT_CAROUSEL_FILTER_1 = 'FALLOUT_CAROUSEL_FILTER_1'
    FALLOUT_CAROUSEL_FILTER_2 = 'FALLOUT_CAROUSEL_FILTER_2'
    RANKED_CAROUSEL_FILTER_1 = 'RANKED_CAROUSEL_FILTER_1'
    RANKED_CAROUSEL_FILTER_2 = 'RANKED_CAROUSEL_FILTER_2'
    GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
    EULA_VERSION = 'EULA_VERSION'
    MARKS_ON_GUN = 'MARKS_ON_GUN'
    CONTACTS = 'CONTACTS'
    FALLOUT = 'FALLOUT'
    TUTORIAL = 'TUTORIAL'
    ONCE_ONLY_HINTS = 'ONCE_ONLY_HINTS'
    FEEDBACK = 'FEEDBACK'
    DAMAGE_INDICATOR = 'FEEDBACK_DAMAGE_INDICATOR'
    DAMAGE_LOG = 'FEEDBACK_DAMAGE_LOG'
    BATTLE_EVENTS = 'FEEDBACK_BATTLE_EVENTS'
    ENCYCLOPEDIA_RECOMMENDATIONS_1 = 'ENCYCLOPEDIA_RECOMMENDATIONS_1'
    ENCYCLOPEDIA_RECOMMENDATIONS_2 = 'ENCYCLOPEDIA_RECOMMENDATIONS_2'
    ENCYCLOPEDIA_RECOMMENDATIONS_3 = 'ENCYCLOPEDIA_RECOMMENDATIONS_3'
    UI_STORAGE = 'UI_STORAGE'


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
     SETTINGS_SECTIONS.GAME_EXTENDED: Section(masks={GAME.CHAT_CONTACTS_LIST_ONLY: 1,
                                       GAME.RECEIVE_INVITES_IN_BATTLE: 2,
                                       GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS: 3,
                                       GAME.MINIMAP_VIEW_RANGE: 6,
                                       GAME.MINIMAP_MAX_VIEW_RANGE: 7,
                                       GAME.MINIMAP_DRAW_RANGE: 8,
                                       GAME.INCREASED_ZOOM: 9,
                                       GAME.SNIPER_MODE_BY_SHIFT: 10,
                                       GAME.CAROUSEL_TYPE: 12,
                                       GAME.DOUBLE_CAROUSEL_TYPE: 13,
                                       GAME.VEHICLE_CAROUSEL_STATS: 14}, offsets={GAME.BATTLE_LOADING_INFO: Offset(4, 48),
                                       GAME.BATTLE_LOADING_RANKED_INFO: Offset(15, 98304)}),
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
     SETTINGS_SECTIONS.AIM_4: Section(masks={}, offsets={'zoomIndicator': Offset(0, 255)}),
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
                                           'event': 7}, offsets={}),
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
                                                  'event': 7}, offsets={}),
     SETTINGS_SECTIONS.FALLOUT_CAROUSEL_FILTER_1: Section(masks={'ussr': 0,
                                                   'germany': 1,
                                                   'usa': 2,
                                                   'china': 3,
                                                   'france': 4,
                                                   'uk': 5,
                                                   'japan': 6,
                                                   'czech': 7,
                                                   'sweden': 8,
                                                   'poland': 9,
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
     SETTINGS_SECTIONS.FALLOUT_CAROUSEL_FILTER_2: Section(masks={'premium': 0,
                                                   'elite': 1,
                                                   'rented': 2,
                                                   'igr': 3,
                                                   'gameMode': 4,
                                                   'favorite': 5,
                                                   'bonus': 6,
                                                   'event': 7}, offsets={}),
     SETTINGS_SECTIONS.GUI_START_BEHAVIOR: Section(masks={'isFreeXPInfoDialogShowed': 0,
                                            'isRankedWelcomeViewShowed': 1,
                                            'isRankedWelcomeViewStarted': 2,
                                            'isEpicRandomCheckboxClicked': 3}, offsets={}),
     SETTINGS_SECTIONS.EULA_VERSION: Section(masks={}, offsets={'version': Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.MARKS_ON_GUN: Section(masks={}, offsets={GAME.SHOW_MARKS_ON_GUN: Offset(0, 4294967295L)}),
     SETTINGS_SECTIONS.CONTACTS: Section(masks={CONTACTS.SHOW_OFFLINE_USERS: 0,
                                  CONTACTS.SHOW_OTHERS_CATEGORY: 1}, offsets={}),
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
     SETTINGS_SECTIONS.ONCE_ONLY_HINTS: Section(masks={'FalloutQuestsTab': 0,
                                         'CustomizationSlotsHint': 1,
                                         'ShopTradeInHint': 2,
                                         'VehCompareConfigHint': 3,
                                         'HoldSheetHint': 4}, offsets={}),
     SETTINGS_SECTIONS.DAMAGE_INDICATOR: Section(masks={DAMAGE_INDICATOR.TYPE: 0,
                                          DAMAGE_INDICATOR.PRESETS: 1,
                                          DAMAGE_INDICATOR.DAMAGE_VALUE: 2,
                                          DAMAGE_INDICATOR.VEHICLE_INFO: 3,
                                          DAMAGE_INDICATOR.ANIMATION: 4,
                                          DAMAGE_INDICATOR.DYNAMIC_INDICATOR: 5}, offsets={}),
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
                                       BATTLE_EVENTS.ENEMY_ASSIST_STUN: 17}, offsets={}),
     SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_1: Section(masks={'hasNew': 15}, offsets={'item_1': Offset(0, 36863),
                                                        'item_2': Offset(16, 2415853568L)}),
     SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_2: Section(masks={}, offsets={'item_3': Offset(0, 36863),
                                                        'item_4': Offset(16, 2415853568L)}),
     SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_3: Section(masks={}, offsets={'item_5': Offset(0, 36863),
                                                        'item_6': Offset(16, 2415853568L)}),
     SETTINGS_SECTIONS.UI_STORAGE: Section(masks={PM_TUTOR_FIELDS.ONE_FAL_SHOWN: 7,
                                    PM_TUTOR_FIELDS.FOUR_FAL_SHOWN: 8}, offsets={PM_TUTOR_FIELDS.FIRST_ENTRY_STATE: Offset(0, 3),
                                    PM_TUTOR_FIELDS.INITIAL_FAL_COUNT: Offset(2, 124)})}
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

    def __init__(self, core):
        self._core = weakref.proxy(core)

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

    def getAimSetting(self, section, key, default=None):
        number = self.AIM_MAPPING[key]
        storageKey = 'AIM_%(section)s_%(number)d' % {'section': section.upper(),
         'number': number}
        settingsKey = 'AIM_%(number)d' % {'number': number}
        storedValue = self.settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[settingsKey].masks
        offsets = self.SECTIONS[settingsKey].offsets
        return self._extractValue(key, storedValue, default, masks, offsets) if storedValue is not None else default

    def getOnceOnlyHintsSetting(self, key, default=None):
        return self.getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, key, default)

    def getOnceOnlyHintsSettings(self):
        return self.getSection(SETTINGS_SECTIONS.ONCE_ONLY_HINTS)

    def setOnceOnlyHintsSettings(self, settings):
        self.setSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, settings)

    def getEncyclopediaRecommendations(self):
        return self.getSections([SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_1, SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_2, SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_3], {})

    def setEncyclopediaRecommendationsSections(self, ids):
        self.setSections([SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_1, SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_2, SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_3], ids)

    def getUIStorage(self, defaults=None):
        return self.getSection(SETTINGS_SECTIONS.UI_STORAGE, defaults)

    def saveInUIStorage(self, fields):
        return self.setSections([SETTINGS_SECTIONS.UI_STORAGE], fields)

    def getPersonalMissionsFirstEntryState(self):
        return self.getUIStorage({PM_TUTOR_FIELDS.FIRST_ENTRY_STATE: 0})[PM_TUTOR_FIELDS.FIRST_ENTRY_STATE]

    def setPersonalMissionsFirstEntryState(self, value):
        return self.saveInUIStorage({PM_TUTOR_FIELDS.FIRST_ENTRY_STATE: value})

    def getHasNewEncyclopediaRecommendations(self):
        return self.getSectionSettings(SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_1, 'hasNew')

    def setHasNewEncyclopediaRecommendations(self, value=True):
        return self.setSectionSettings(SETTINGS_SECTIONS.ENCYCLOPEDIA_RECOMMENDATIONS_1, {'hasNew': value})

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
        storageKey = 'MARKERS_%(section)s' % {'section': section.upper()}
        storedValue = self.settingsCache.getSectionSettings(storageKey, None)
        masks = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].masks
        offsets = self.SECTIONS[SETTINGS_SECTIONS.MARKERS].offsets
        return self._extractValue(key, storedValue, default, masks, offsets) if storedValue is not None else default

    def _buildMarkersSettings(self, settings):
        settingToServer = {}
        for section, options in settings.iteritems():
            storageKey = 'MARKERS_%(section)s' % {'section': section.upper()}
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

    def getSections(self, sections, defaults):
        result = {}
        for section in sections:
            result.update(self.getSection(section, defaults))

        return result

    def setSections(self, sections, settings):
        settingToServer = {}
        for section in sections:
            keys = self.SECTIONS[section].masks.keys() + self.SECTIONS[section].offsets.keys()
            currentSettings = {key:value for key, value in settings.items() if key in keys}
            settingToServer[section] = self._buildSectionSettings(section, currentSettings)

        self.setSettings(settingToServer)

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

    @async
    @process
    def _updateToVersion(self, callback=None):
        currentVersion = self.settingsCache.getVersion()
        data = {'gameData': {},
         'gameExtData': {},
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
         'clear': {}}
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
        if carousel_filter:
            settings[SETTINGS_SECTIONS.CAROUSEL_FILTER_2] = self._buildSectionSettings(SETTINGS_SECTIONS.CAROUSEL_FILTER_2, carousel_filter)
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
        version = data.get(VERSION)
        if version is not None:
            settings[VERSION] = version
        if settings:
            self.setSettings(settings)
        return
