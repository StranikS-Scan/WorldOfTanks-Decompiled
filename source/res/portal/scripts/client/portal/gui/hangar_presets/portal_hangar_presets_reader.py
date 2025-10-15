# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/hangar_presets/portal_hangar_presets_reader.py
from gui.hangar_presets import DefaultPresetReader

class PortalHangarPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'portal/gui/portal_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False
