# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/hangar_presets/__init__.py
from constants import QUEUE_TYPE
from battle_royale.gui.hangar_presets.battle_royale_presets_reader import BattleRoyalePresetsReader
from battle_royale.gui.hangar_presets.battle_royale_presets_getter import BattleRoyalePresetsGetter, BattleRoyaleTournamentPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter

def registerBattleRoyaleHangarPresets():
    registerHangarPresetsReader(BattleRoyalePresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.BATTLE_ROYALE, BattleRoyalePresetsGetter)
    registerHangarPresetGetter(QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT, BattleRoyaleTournamentPresetsGetter)
