# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/stats_params_getters.py
import typing
from gui.battle_results.pbs_helpers.common import isPersonalBattleResult
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo

def isNotPersonalBattleResult(summarizeInfo, battleResults):
    return not isPersonalBattleResult(summarizeInfo, battleResults)


def hasStunEfficiency(summarizeInfo, _):
    return summarizeInfo.stunNum > 0


def getStatsParamValue(summarizeInfo, fields, _):
    return (getattr(summarizeInfo, field) for field in fields)


def getMileageValue(summarizeInfo, fields, _):
    return (getattr(summarizeInfo, field) / 1000.0 for field in fields)
