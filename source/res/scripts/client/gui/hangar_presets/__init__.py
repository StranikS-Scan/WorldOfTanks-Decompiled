# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/__init__.py
from constants import QUEUE_TYPE
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter, Comp7PresetsGetter, MapboxPresetsGetter, WtEventPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter
registerHangarPresetsReader(DefaultPresetReader)
registerHangarPresetGetter(QUEUE_TYPE.RANDOMS, DefaultPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.MAPBOX, MapboxPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.COMP7, Comp7PresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.EVENT_BATTLES, WtEventPresetsGetter)
