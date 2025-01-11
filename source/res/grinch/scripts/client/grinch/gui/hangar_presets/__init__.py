# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/hangar_presets/__init__.py
from grinch_common.grinch_constants import QUEUE_TYPE
from grinch.gui.hangar_presets.grinch_hangar_presets_reader import GrinchPresetsReader
from grinch.gui.hangar_presets.grinch_hangar_presets_getter import GrinchPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter

def registerGrinchHangarPresets():
    registerHangarPresetsReader(GrinchPresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.GRINCH, GrinchPresetsGetter)
