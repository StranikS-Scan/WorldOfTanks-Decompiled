# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/GraphicsPresets.py
# Compiled at: 2011-11-18 17:41:31
import BigWorld
import ResMgr
from MemoryCriticalController import g_critMemHandler
from debug_utils import LOG_ERROR
from gui import SystemMessages
from helpers import i18n
graphicsPresetsResource = 'system/data/graphics_settings_presets.xml'

class GraphicsPresets:
    CUSTOM_PRESET_KEY = 'CUSTOM'
    GRAPHICS_QUALITY_SETTINGS = {'SKY_LIGHT_MAP': (True,
                       False,
                       False,
                       True),
     'MRT_DEPTH': (True,
                   False,
                   True,
                   True),
     'TEXTURE_QUALITY': (False,
                         True,
                         True,
                         True),
     'TEXTURE_COMPRESSION': (False,
                             True,
                             True,
                             True),
     'TEXTURE_FILTERING': (False,
                           False,
                           True,
                           True),
     'SHADOWS_QUALITY': (False,
                         False,
                         True,
                         True),
     'WG_SHADOWS_QUALITY': (False,
                            False,
                            True,
                            True),
     'SPEEDTREE_QUALITY': (False,
                           False,
                           True,
                           True),
     'WATER_QUALITY': (False,
                       False,
                       True,
                       True),
     'WATER_SIMULATION': (False,
                          False,
                          True,
                          True),
     'FAR_PLANE': (False,
                   False,
                   True,
                   True),
     'FLORA_DENSITY': (False,
                       False,
                       True,
                       True),
     'OBJECT_LOD': (False,
                    False,
                    True,
                    True),
     'POST_PROCESSING': (False,
                         False,
                         True,
                         True),
     'VEHICLE_DUST_ENABLED': (False,
                              False,
                              True,
                              True),
     'SNIPER_MODE_GRASS_ENABLED': (False,
                                   False,
                                   True,
                                   True),
     'SNIPER_MODE_EFFECTS_QUALITY': (False,
                                     False,
                                     True,
                                     True),
     'EFFECTS_QUALITY': (False,
                         False,
                         True,
                         True),
     'VEHICLE_TRACES_ENABLED': (False,
                                False,
                                True,
                                True),
     'SNIPER_MODE_SWINGING_ENABLED': (False,
                                      False,
                                      True,
                                      False)}

    def __init__(self):
        section = ResMgr.openSection(graphicsPresetsResource)
        self.__presets = {}
        self.__presetsKeys = []
        for group in section.values():
            presetKey = group.asString
            self.__presetsKeys.append(presetKey)
            self.__presets[presetKey] = {}
            for setting in group.values():
                label = setting.readString('label')
                if label:
                    self.__presets[presetKey][label] = setting.readInt('activeOption')

        self.__presetsKeys.append(GraphicsPresets.CUSTOM_PRESET_KEY)
        self.setSelectedPreset()

    def setSelectedPreset(self):
        self.selectedPresetKey = GraphicsPresets.CUSTOM_PRESET_KEY
        currentSettingsMap = self.__getCurrentSettingsMap()
        for key, settings in self.__presets.items():
            foundOption = True
            for label, value in settings.items():
                if currentSettingsMap.get(label) != value and GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.get(label, (False,
                 False,
                 False,
                 True))[3]:
                    foundOption = False
                    break

            if foundOption:
                self.selectedPresetKey = key
                break

    def getCurrentSettingsForGUI(self):
        self.setSelectedPreset()
        graphQualitySettings = BigWorld.graphicsSettings()
        qualitySettings = {'quality': {},
         'presets': None}
        for label, index, values, description in graphQualitySettings:
            if GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.get(label, (False,
             False,
             False,
             False))[2]:
                options = [ '#settings:graphicsQuality/' + valueLabel for valueLabel, supportFlag, desc in values ]
                qualitySettings['quality'][label] = {'value': index,
                 'options': options}

        presets = {'current': self.__presetsKeys.index(self.selectedPresetKey),
         'values': []}
        for index, presetKey in enumerate(self.__presetsKeys):
            preset = {'index': index,
             'key': presetKey,
             'settings': {}}
            settings = self.__presets.get(presetKey, {})
            for label, value in settings.items():
                restartNeeded, delayed, visibleInGUI, isInPreset = GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.get(label, (False,
                 False,
                 False,
                 False))
                if visibleInGUI and isInPreset:
                    preset['settings'][label] = value

            presets['values'].append(preset)

        qualitySettings['presets'] = presets
        return qualitySettings

    def __getCurrentSettingsMap(self):
        graphQualitySettings = BigWorld.graphicsSettings()
        qualitySettings = {}
        for label, index, values, description in graphQualitySettings:
            qualitySettings[label] = index

        return qualitySettings

    def applyGraphicsPreset(self, presetName):
        section = ResMgr.openSection(graphicsPresetsResource)
        i = 0
        newPreset = {}
        for group in section.values():
            if presetName == group.asString:
                for key, value in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.items():
                    if value[3] is False:
                        newPreset[key] = 1

                self.applyGraphicsPresets(i, newPreset)
                return True
            i = i + 1

        return False

    def applyGraphicsPresets(self, presetIndex, customSettings):
        newPresetKey = self.__presetsKeys[presetIndex]
        newPreset = {}
        if newPresetKey == self.CUSTOM_PRESET_KEY:
            newPreset = customSettings
        elif newPresetKey != self.selectedPresetKey:
            newPreset = self.__presets[newPresetKey]
        for key, value in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.items():
            if value[3] is False:
                newPreset[key] = customSettings[key]

        notSetOptions = []
        for key, value in newPreset.items():
            try:
                BigWorld.setGraphicsSetting(key, value)
                if key == 'TEXTURE_QUALITY':
                    if g_critMemHandler.originQuality != -1:
                        g_critMemHandler.originQuality = value
            except:
                notSetOptions.append(i18n.makeString('#settings:%s' % key))
                LOG_ERROR("selectGraphicsOptions: unable to set value '%s' for option '%s'" % (value, key))

        if notSetOptions:
            if newPresetKey == self.CUSTOM_PRESET_KEY:
                SystemMessages.pushI18nMessage('#system_messages:graficsOptionsFail', ', '.join(notSetOptions), type=SystemMessages.SM_TYPE.Error)
            else:
                SystemMessages.pushI18nMessage('#system_messages:graficsPresetFail', type=SystemMessages.SM_TYPE.Error)
        self.selectedPresetKey = newPresetKey

    def checkApplyGraphicsPreset(self, presetIndex, customSettings):
        newPresetKey = self.__presetsKeys[presetIndex]
        presetForApply = {}
        if newPresetKey == self.CUSTOM_PRESET_KEY:
            presetForApply = customSettings
        elif newPresetKey != self.selectedPresetKey:
            presetForApply = self.__presets[newPresetKey]
        for key, value in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.items():
            if value[3] is False:
                presetForApply[key] = customSettings[key]

        if not presetForApply:
            return False
        currentPreset = self.__getCurrentSettingsMap()
        delayedSettings = False
        for key, value in presetForApply.items():
            restartNeeded, delayed, visibleInGUI, isInPreset = GraphicsPresets.GRAPHICS_QUALITY_SETTINGS.get(key, (False,
             False,
             False,
             False))
            if value != currentPreset.get(key) or not isInPreset:
                if restartNeeded:
                    return 'restartNeeded'
                if delayed and not delayedSettings:
                    delayedSettings = True

        if delayedSettings:
            return 'hasPendingSettings'
