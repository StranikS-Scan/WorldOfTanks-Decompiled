# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_presets_reader.py
import ResMgr
from gui.hangar_presets.hangar_gui_config import HangarGuiPreset, HangarGuiSettings, PresetSettings
from soft_exception import SoftException
_ERR_TEMPLATE = "[HangarGUI] {} in the preset '{}'"

class IPresetReader(object):

    @classmethod
    def readConfig(cls, fullConfig):
        raise NotImplementedError

    @staticmethod
    def isDefault():
        raise NotImplementedError


class DefaultPresetReader(IPresetReader):
    _CONFIG_PATH = 'gui/hangar_gui_presets.xml'

    @classmethod
    def readConfig(cls, fullConfig):
        return cls.__readGuiHangarConfig(cls._CONFIG_PATH, fullConfig)

    @staticmethod
    def isDefault():
        return True

    @classmethod
    def _getPreset(cls, presetName, config):
        return presetName

    @classmethod
    def _updateItems(cls, items, queueType, preset):
        items[queueType] = preset

    @classmethod
    def __readComponents(cls, config, presetName):
        shownComponents = {}
        hiddenComponents = {}
        for name, section in config.items():
            if name != 'component':
                raise SoftException(_ERR_TEMPLATE.format('Wrong section', presetName))
            if not section.has_key('name'):
                raise SoftException(_ERR_TEMPLATE.format('Missing component name', presetName))
            name = section['name'].asString
            if not section.has_key('name'):
                raise SoftException(_ERR_TEMPLATE.format('Missing component visibility', presetName))
            isVisible = section['visible'].asBool
            isChangeable = section.readBool('isChangeable')
            componentType = section['type'].asString if section.has_key('type') else None
            layout = section['layout'].asString if section.has_key('layout') else None
            targetComponents = shownComponents if isVisible else hiddenComponents
            targetComponents[name] = PresetSettings(componentType, layout, isChangeable)

        return HangarGuiPreset(shownComponents, hiddenComponents)

    @classmethod
    def __readGuiHangarConfig(cls, configPath, fullConfig):
        config = ResMgr.openSection(configPath)
        if config is None:
            raise SoftException('[HangarGUI] Cannot open or read config {}'.format(configPath))
        presets = {}
        if config.has_key('presets'):
            presets = cls.__readPresets(config['presets'], fullConfig)
        if not config.has_key('queueTypePresets'):
            raise SoftException('[HangarGUI] Missing queueTypePresets section in the config'.format(configPath))
        queueTypePresets = cls.__readPresetsForQueueTypes(config['queueTypePresets'])
        return HangarGuiSettings(presets, queueTypePresets)

    @classmethod
    def __readPresets(cls, config, fullConfig):
        presets = {}
        for name, subSection in config.items():
            if name != 'preset':
                raise SoftException('[HangarGUI] Invalid preset section')
            if not subSection.has_key('name'):
                raise SoftException('[HangarGUI] Missing preset name')
            presetName = subSection['name'].asString
            if not subSection.has_key('components'):
                raise SoftException(_ERR_TEMPLATE.format('Missing components section', presetName))
            components = cls.__readComponents(subSection['components'], presetName)
            if subSection.has_key('basePreset'):
                basePresetName = subSection['basePreset'].asString
                basePreset = presets.get(basePresetName) or fullConfig.presets.get(basePresetName)
                if basePreset is None:
                    raise SoftException(_ERR_TEMPLATE.format('Invalid base preset', presetName))
                components = cls.__updateComponents(basePreset, components)
            presets[presetName] = components

        return presets

    @classmethod
    def __readPresetsForQueueTypes(cls, config):
        items = {}
        for name, subSection in config.items():
            if name != 'item':
                raise SoftException('[HangarGUI] Invalid item section in queueTypePresets section')
            if not subSection.has_key('queueType'):
                raise SoftException('[HangarGUI] Missing queueType in queueTypePresets section')
            queueType = subSection['queueType'].asInt
            if not subSection.has_key('presetName'):
                raise SoftException('[HangarGUI] Missing preset name in queueTypePresets section')
            presetName = subSection['presetName'].asString
            preset = cls._getPreset(presetName, subSection)
            cls._updateItems(items, queueType, preset)

        return items

    @staticmethod
    def __updateComponents(baseComponents, override):
        baseVisibleComponents = baseComponents.visibleComponents.copy()
        baseHiddenComponents = baseComponents.hiddenComponents.copy()
        for compName, compSettings in override.visibleComponents.items():
            if compName in baseHiddenComponents:
                del baseHiddenComponents[compName]
            baseVisibleComponents[compName] = compSettings

        for compName, compSettings in override.hiddenComponents.items():
            if compName in baseVisibleComponents:
                del baseVisibleComponents[compName]
            baseHiddenComponents[compName] = compSettings

        return HangarGuiPreset(baseVisibleComponents, baseHiddenComponents)


class DefaultSubPresetReader(DefaultPresetReader):
    _SUB_TYPES_KEY = 'subTypes'

    @staticmethod
    def isDefault():
        return False

    @classmethod
    def _getPreset(cls, presetName, config):
        if not config.has_key(cls._SUB_TYPES_KEY):
            raise SoftException('Missing {} section for {}'.format(cls._SUB_TYPES_KEY, cls._CONFIG_PATH))
        return {subType:presetName for subType in map(int, config[cls._SUB_TYPES_KEY].asString.split())}

    @classmethod
    def _updateItems(cls, items, queueType, preset):
        presets = items.get(queueType, {})
        if not presets:
            items[queueType] = preset
        else:
            items[queueType].update(preset)


class SpecBattlePresetReader(DefaultSubPresetReader):
    _CONFIG_PATH = 'gui/hangar_gui_spec_presets.xml'
    _SUB_TYPES_KEY = 'guiTypes'
