# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/__init__.py
from constants import QUEUE_TYPE
from fun_random.gui.hangar_presets.fun_hangar_presets_reader import FunRandomPresetsReader
from fun_random.gui.hangar_presets.fun_hangar_presets_getter import FunRandomPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter

def registerFunRandomHangarPresets():
    registerHangarPresetsReader(FunRandomPresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.FUN_RANDOM, FunRandomPresetsGetter)
