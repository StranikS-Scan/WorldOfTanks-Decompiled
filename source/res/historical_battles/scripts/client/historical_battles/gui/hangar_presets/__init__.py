# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/hangar_presets/__init__.py
from historical_battles_common.hb_constants_extension import QUEUE_TYPE
from historical_battles.gui.hangar_presets.historical_battles_presets_reader import HistoricalBattlesPresetsReader
from historical_battles.gui.hangar_presets.historical_battles_presets_getter import HBOffencePresetsGetter
from historical_battles.gui.hangar_presets.historical_battles_presets_getter import HBDefencePresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter

def registerHistoricalBattlesHangarPresets():
    registerHangarPresetsReader(HistoricalBattlesPresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.HB_OFFENCE, HBOffencePresetsGetter)
    registerHangarPresetGetter(QUEUE_TYPE.HB_DEFENCE, HBDefencePresetsGetter)
