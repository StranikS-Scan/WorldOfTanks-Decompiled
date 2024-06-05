# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/epic.py
from constants import ARENA_BONUS_TYPE
from frontline.gui.frontline_helpers import FLBattleTypeDescription
from gui.battle_results.components import base
from gui.impl import backport
from gui.impl.gen import R

class BattleModificationItem(base.StatsItem):
    __slots__ = ()
    arenaBonusTypes = [ARENA_BONUS_TYPE.EPIC_BATTLE, ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING]

    def _convert(self, record, reusable):
        return FLBattleTypeDescription.getBattleTypeIconPath(record['personal']['avatar'].get('reservesModifier'), 'c_18x18') if reusable.common.arenaBonusType in self.arenaBonusTypes else ''


class StrBattleModificationItem(BattleModificationItem):

    def _convert(self, record, reusable):
        return backport.text(R.strings.fl_common.battleType.postBattle.title(), name=FLBattleTypeDescription.getTitle(record['personal']['avatar'].get('reservesModifier'))) if reusable.common.arenaBonusType in self.arenaBonusTypes else ''
