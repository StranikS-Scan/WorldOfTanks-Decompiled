# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/hangar_presets/hw_presets_reader.py
from __future__ import absolute_import
from gui.hangar_presets.obsolete.hangar_presets_reader import DefaultPresetReader

class HalloweenPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'halloween/gui/configs/hw_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
