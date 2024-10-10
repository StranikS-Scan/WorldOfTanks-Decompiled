# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/hangar_presets/white_tiger_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader

class WhiteTigerPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'white_tiger/gui/configs/white_tiger_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
