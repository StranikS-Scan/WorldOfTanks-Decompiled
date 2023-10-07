# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_battle_result_service.py
from gui.battle_results.service import BattleResultsService
from halloween_common.halloween_constants import ARENA_BONUS_TYPE

class HalloweenBattleResultService(BattleResultsService):

    def _isShowImmediately(self, arenaBonusType):
        return arenaBonusType not in (ARENA_BONUS_TYPE.HALLOWEEN_BATTLES, ARENA_BONUS_TYPE.HALLOWEEN_BATTLES_WHEEL)
