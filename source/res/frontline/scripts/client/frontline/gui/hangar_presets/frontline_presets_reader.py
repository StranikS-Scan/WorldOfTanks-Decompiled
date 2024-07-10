# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/hangar_presets/frontline_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader

class FrontlinePresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'frontline/gui/configs/frontline_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
