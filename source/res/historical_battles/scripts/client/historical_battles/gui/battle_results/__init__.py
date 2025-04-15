# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/__init__.py


def initBattleResults():
    from historical_battles.gui.battle_results.composer import HistoryBattleStatsComposer
    from battle_results.extension_utils import initBattleResultsConfigFromExtension
    from historical_battles_common.battle_results import historical_battles
    from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
    for bonusType in ARENA_BONUS_TYPE.HB_RANGE:
        initBattleResultsConfigFromExtension(bonusType, historical_battles)

    from historical_battles.gui.battle_results import reusable
