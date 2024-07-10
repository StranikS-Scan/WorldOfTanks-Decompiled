# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_results/__init__.py
from constants import ARENA_BONUS_TYPE
from battle_royale.gui.battle_results.composer import BattleRoyaleStatsComposer

def registerBRBattleResultsComposer():
    from gui.shared.system_factory import registerBattleResultStatsCtrl
    for arenaBonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
        registerBattleResultStatsCtrl(arenaBonusType, BattleRoyaleStatsComposer)
