# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/hangar_presets/fort_rush_presets_reader.py
from __future__ import absolute_import
from gui.hangar_presets.obsolete.hangar_presets_reader import DefaultPresetReader

class FortRushPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'fort_rush/gui/configs/fort_rush_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
