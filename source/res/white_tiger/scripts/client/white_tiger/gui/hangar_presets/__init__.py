# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/hangar_presets/__init__.py
from white_tiger_common.wt_constants import QUEUE_TYPE
from white_tiger.gui.hangar_presets.white_tiger_presets_reader import WhiteTigerPresetsReader
from white_tiger.gui.hangar_presets.white_tiger_presets_getter import WhiteTigerPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter

def registerWhiteTigerHangarPresets():
    registerHangarPresetsReader(WhiteTigerPresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.WHITE_TIGER, WhiteTigerPresetsGetter)
