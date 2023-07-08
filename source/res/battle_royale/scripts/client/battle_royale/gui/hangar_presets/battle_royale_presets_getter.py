# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/hangar_presets/battle_royale_presets_getter.py
from constants import QUEUE_TYPE
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter

class BattleRoyalePresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.BATTLE_ROYALE


class BattleRoyaleTournamentPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT
