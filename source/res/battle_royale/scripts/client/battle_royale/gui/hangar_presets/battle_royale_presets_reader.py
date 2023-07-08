# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/hangar_presets/battle_royale_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader

class BattleRoyalePresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'battle_royale/gui/configs/battle_royale_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
