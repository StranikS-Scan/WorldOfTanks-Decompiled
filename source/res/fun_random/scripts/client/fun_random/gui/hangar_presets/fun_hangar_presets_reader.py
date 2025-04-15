# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/fun_hangar_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultSubPresetReader
from gui.hangar_presets.hangar_gui_config import HangarGuiSettings
from fun_random.gui.shared.fun_system_factory import collectPresetConfigs

class FunRandomPresetsReader(DefaultSubPresetReader):
    _CONFIG_PATH = ''

    @classmethod
    def readConfig(cls, fullConfig):
        config = HangarGuiSettings({}, {})
        for configPath in collectPresetConfigs():
            subModeConfig = cls._readGuiHangarConfig(configPath, fullConfig)
            config.presets.update(subModeConfig.presets)
            for bonusType in subModeConfig.modes.keys():
                if bonusType not in config.modes:
                    config.modes[bonusType] = {}
                config.modes.get(bonusType, {}).update(subModeConfig.modes[bonusType])

        return config
