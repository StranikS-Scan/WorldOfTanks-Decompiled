# Embedded file name: scripts/client/gui/GraphicsPresets.py
import BigWorld
import ResMgr
from operator import itemgetter
from MemoryCriticalController import g_critMemHandler
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, GUI_SETTINGS
from helpers import i18n
from account_helpers.settings_core.settings_constants import GRAPHICS
graphicsPresetsResource = 'system/data/graphics_settings_presets.xml'

class GraphicsPresets:
    CUSTOM_PRESET_KEY = 'CUSTOM'
    GRAPHICS_QUALITY_SETTINGS = ('RENDER_PIPELINE',
     'TEXTURE_QUALITY',
     'DECALS_QUALITY',
     'OBJECT_LOD',
     'FAR_PLANE',
     'TERRAIN_QUALITY',
     'SHADOWS_QUALITY',
     'LIGHTING_QUALITY',
     'SPEEDTREE_QUALITY',
     'FLORA_QUALITY',
     'WATER_QUALITY',
     'EFFECTS_QUALITY',
     'POST_PROCESSING_QUALITY',
     'MOTION_BLUR_QUALITY',
     'SNIPER_MODE_EFFECTS_QUALITY',
     'VEHICLE_DUST_ENABLED',
     'SNIPER_MODE_GRASS_ENABLED',
     'VEHICLE_TRACES_ENABLED',
     'SNIPER_MODE_SWINGING_ENABLED',
     'COLOR_GRADING_TECHNIQUE',
     'SEMITRANSPARENT_LEAVES_ENABLED',
     GRAPHICS.DRR_AUTOSCALER_ENABLED)
    GRAPHICS_QUALITY_SETTINGS_PRESETS_EXCLUDE = ('SNIPER_MODE_SWINGING_ENABLED', 'COLOR_GRADING_TECHNIQUE')

    def __init__(self):
        section = ResMgr.openSection(graphicsPresetsResource)
        self.__presets = {}
        self.__presetsKeys = []
        self.__currentSetings = None
        self.__settingsNeedRestart = set()
        self.__settingsDelayed = set()
        for group in section.values():
            presetKey = group.asString
            self.__presetsKeys.append(presetKey)
            self.__presets[presetKey] = {}
            for setting in group.values():
                label = setting.readString('label')
                if label:
                    self.__presets[presetKey][label] = setting.readInt('activeOption')

        self.__presetsKeys.append(GraphicsPresets.CUSTOM_PRESET_KEY)
        self.checkCurrentPreset()
        return

    def checkCurrentPreset(self, needRefresh = False):
        if needRefresh:
            self.__currentSetings = None
        self.selectedPresetKey = GraphicsPresets.CUSTOM_PRESET_KEY
        for key, settings in self.__presets.items():
            foundOption = True
            for label, value in settings.items():
                if self.__currentSettingsMap.get(label) != value and label in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                    LOG_DEBUG('preset %s breaks at %s' % (key, label))
                    foundOption = False
                    break

            if foundOption:
                self.selectedPresetKey = key
                break

        LOG_DEBUG('current preset: %s' % self.selectedPresetKey)
        return

    def settingIsMaxOfSupported(self, label, value):
        graphQualitySettings = BigWorld.graphicsSettings()
        for name, _, optionsList, _, _, _, _ in graphQualitySettings:
            if name == label and len(optionsList) > value:
                _, supportFlag, _, _ = optionsList[value]
                if supportFlag:
                    if value > 0:
                        _, supportFlag_1, _, _ = optionsList[value - 1]
                        return not supportFlag_1
                    else:
                        return True
                return False

        return False

    def settingIsSupported(self, label, value):
        graphQualitySettings = BigWorld.graphicsSettings()
        for name, _, optionsList, _, _, _, _ in graphQualitySettings:
            if name == label and len(optionsList) > value:
                _, supportFlag, _, _ = optionsList[value]
                return supportFlag

        return False

    def getGraphicsPresetsData(self):
        graphQualitySettings = BigWorld.graphicsSettings()
        qualitySettings = {'quality': {},
         'presets': None,
         'qualityOrder': GraphicsPresets.GRAPHICS_QUALITY_SETTINGS}
        for settingName, index, values, _, advanced, _, _ in graphQualitySettings:
            if settingName in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                options = []
                for i, val in enumerate(values):
                    valueLabel, supportFlag, advanced, _ = val
                    options.append({'label': '#settings:graphicsSettingsOptions/' + valueLabel,
                     'data': i,
                     'advanced': advanced,
                     'supported': supportFlag})

                options = sorted(options, key=itemgetter('data'), reverse=True)
                qualitySettings['quality'][settingName] = {'value': index,
                 'options': options}

        presets = {'current': self.__presetsKeys.index(self.selectedPresetKey),
         'values': []}
        for index, presetKey in enumerate(self.__presetsKeys):
            preset = {'index': index,
             'key': presetKey,
             'settings': {}}
            settings = self.__presets.get(presetKey, {})
            isSupported = True
            for settingName, value in settings.items():
                if not self.settingIsSupported(settingName, value):
                    allowedPresetSettings = GUI_SETTINGS.allowedNotSupportedGraphicSettings.get(preset['key'], [])
                    if settingName not in allowedPresetSettings:
                        isSupported = False
                        break
                if settingName in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                    preset['settings'][settingName] = value

            if isSupported:
                presets['values'].append(preset)

        presets['values'] = sorted(presets['values'], key=itemgetter('index'), reverse=True)
        qualitySettings['presets'] = presets
        return qualitySettings

    @property
    def __currentSettingsMap(self):
        if self.__currentSetings is None:
            graphQualitySettings = BigWorld.graphicsSettings()
            self.__currentSetings = {}
            sNeedRestart = []
            sDelayed = []
            for label, index, _, _, _, needsRestart, delayed in graphQualitySettings:
                self.__currentSetings[label] = index
                if needsRestart:
                    sNeedRestart.append(label)
                if delayed:
                    sDelayed.append(label)

            self.__settingsNeedRestart = set(sNeedRestart)
            self.__settingsDelayed = set(sDelayed)
        return self.__currentSetings

    def applyGraphicsPreset(self, presetName):
        if self.__presets.has_key(presetName):
            self.applyGraphicsPresets(self.__presetsKeys.index(presetName), self.__presets[presetName])
            return True
        return False

    def applyGraphicsPresets(self, presetIndex, customSettings):
        newPresetKey = self.__presetsKeys[presetIndex]
        newPreset = {}
        if newPresetKey == self.CUSTOM_PRESET_KEY:
            newPreset = customSettings
        elif newPresetKey != self.selectedPresetKey:
            newPreset = self.__presets[newPresetKey]
        else:
            newPreset = self.__presets[self.selectedPresetKey]
        for key in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS_PRESETS_EXCLUDE:
            if customSettings.has_key(key):
                newPreset[key] = customSettings[key]

        notSetOptions = []
        LOG_DEBUG('Setting preset: %s' % newPresetKey)
        for key in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
            value = newPreset.get(key, None)
            if value is None:
                LOG_ERROR('No value for setting: %s' % key)
                continue
            try:
                while not self.settingIsSupported(key, value) and value < 5:
                    value = value + 1

                LOG_DEBUG('set setting %s = %d' % (key, value))
                BigWorld.setGraphicsSetting(key, value)
                if key == 'TEXTURE_QUALITY':
                    if g_critMemHandler.originTexQuality != -1:
                        g_critMemHandler.originTexQuality = value
                if key == 'FLORA_QUALITY':
                    if g_critMemHandler.originFloraQuality != -1:
                        g_critMemHandler.originFloraQuality = value
                if key == 'TERRAIN_QUALITY':
                    if g_critMemHandler.originTerrainQuality != -1:
                        g_critMemHandler.originTerrainQuality = value
            except:
                notSetOptions.append(i18n.makeString('#settings:%s' % key))
                LOG_ERROR("selectGraphicsOptions: unable to set value '%s' for option '%s'" % (value, key))

        if notSetOptions:
            if newPresetKey == self.CUSTOM_PRESET_KEY:
                SystemMessages.pushI18nMessage('#system_messages:graficsOptionsFail', ', '.join(notSetOptions), type=SystemMessages.SM_TYPE.Error)
            else:
                SystemMessages.pushI18nMessage('#system_messages:graficsPresetFail', type=SystemMessages.SM_TYPE.Error)
        self.__currentSetings = None
        self.checkCurrentPreset()
        return

    def checkApplyGraphicsPreset(self, presetIndex, customSettings):
        newPresetKey = self.__presetsKeys[presetIndex]
        presetForApply = {}
        if newPresetKey == self.CUSTOM_PRESET_KEY:
            presetForApply = customSettings
        elif newPresetKey != self.selectedPresetKey:
            presetForApply = self.__presets[newPresetKey]
        for key in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS_PRESETS_EXCLUDE:
            if customSettings.has_key(key):
                presetForApply[key] = customSettings[key]

        if not presetForApply:
            return False
        delayedSettings = False
        for key, value in presetForApply.items():
            if value != self.__currentSettingsMap.get(key):
                if key in self.__settingsNeedRestart:
                    return 'restartNeeded'
                if key in self.__settingsDelayed:
                    delayedSettings = True

        if delayedSettings:
            return 'hasPendingSettings'
        return 'apply'
