# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/epic.py
from frontline.gui.frontline_helpers import FLBattleTypeDescription
from constants import ARENA_BONUS_TYPE
from gui.battle_results.components import base
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class BattleModificationItem(base.StatsItem):
    __slots__ = ()
    battleTypeDescription = FLBattleTypeDescription()
    epicMetaCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    arenaBonusTypes = [ARENA_BONUS_TYPE.EPIC_BATTLE, ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING]

    def _convert(self, record, reusable):
        return self.battleTypeDescription.getBattleTypeIconPath('c_18x18') if reusable.common.arenaBonusType in self.arenaBonusTypes else ''


class StrBattleModificationItem(BattleModificationItem):

    def _convert(self, record, reusable):
        epicGameMode = R.strings.fl_common.battleType.postBattle
        return backport.text(epicGameMode.title(), name=self.battleTypeDescription.getTitle()) if reusable.common.arenaBonusType in self.arenaBonusTypes else ''
