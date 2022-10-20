# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_results/style.py
from constants import FINISH_REASON
from gui.battle_results.components import base
from gui.impl import backport
from gui.impl.gen import R

class MetersToKillometersItem(base.StatsItem):

    def _convert(self, value, reusable):
        converted = backport.getFractionalFormat(value / 1000.0)
        if not value:
            converted = '0,00'
        return converted


def makeStatValue(field, value):
    return {'label': backport.text(R.strings.battle_results.team.stats.dyn('labels_{}'.format(field))()),
     'value': str(value)}


def makeRegularFinishResultLabel(finishReason, teamResult):
    return backport.text(R.strings.battle_results.finish.reason.dyn('c_{}{}'.format(finishReason, teamResult))()) if finishReason in (FINISH_REASON.EXTERMINATION,
     FINISH_REASON.EVENT_DAMAGE_TIMEOUT,
     FINISH_REASON.EVENT_EXTERMINATION,
     FINISH_REASON.EVENT_2_BASES_CAPTURED) else backport.text(R.strings.battle_results.finish.reason.dyn('c_{}'.format(finishReason))())
