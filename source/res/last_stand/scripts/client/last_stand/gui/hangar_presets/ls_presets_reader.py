# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/hangar_presets/ls_presets_reader.py
from __future__ import absolute_import
from gui.hangar_presets.obsolete.hangar_presets_reader import DefaultPresetReader

class LSPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'last_stand/gui/configs/ls_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
