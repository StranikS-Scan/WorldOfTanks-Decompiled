# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_gui_config.py
from collections import namedtuple
import typing
if typing.TYPE_CHECKING:
    from gui.hangar_presets.hangar_presets_reader import IPresetReader
_HANGAR_GUI_CONFIG = None
HangarGuiSettings = namedtuple('HangarGuiSettings', ('presets', 'modes'))
HangarGuiPreset = namedtuple('HangarGuiPreset', ('visibleComponents', 'hiddenComponents'))
PresetSettings = namedtuple('PresetSettings', ('type', 'layout', 'isChangeable'))

def _updateConfig(fullConfig, config):
    presets = {}
    presetsForQueueTypes = {}
    for c in [fullConfig, config]:
        presets.update(c.presets)
        presetsForQueueTypes.update(c.modes)

    return HangarGuiSettings(presets, presetsForQueueTypes)


def getHangarGuiConfig(readers):
    global _HANGAR_GUI_CONFIG
    if _HANGAR_GUI_CONFIG is None:
        fullConfig = HangarGuiSettings({}, {})
        for reader in readers:
            config = reader.readConfig(fullConfig)
            fullConfig = _updateConfig(fullConfig, config)

        _HANGAR_GUI_CONFIG = fullConfig
    return _HANGAR_GUI_CONFIG
