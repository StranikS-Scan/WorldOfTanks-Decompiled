# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/obsolete/__init__.py
from gui.hangar_presets.obsolete.hangar_presets_reader import DefaultPresetReader, SpecBattlePresetReader
from gui.shared.system_factory import registerHangarPresetsReader
registerHangarPresetsReader(DefaultPresetReader)
registerHangarPresetsReader(SpecBattlePresetReader)
