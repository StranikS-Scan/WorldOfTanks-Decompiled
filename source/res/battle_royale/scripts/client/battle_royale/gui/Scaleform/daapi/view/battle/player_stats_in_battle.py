# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/player_stats_in_battle.py
import logging
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.meta.BattleRoyalePlayerStatsMeta import BattleRoyalePlayerStatsMeta
from gui.Scaleform.locale.BATTLE_ROYALE import BATTLE_ROYALE
from gui.battle_control import avatar_getter
from gui.server_events.battle_royale_formatters import IngameBattleRoyaleResultsViewDataFormatter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class BattleRoyalePlayerStats(BattleRoyalePlayerStatsMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleRoyalePlayerStats, self).__init__()
        self.__isInSquad = False

    def _populate(self):
        super(BattleRoyalePlayerStats, self)._populate()
        deathScreenCtrl = self.__sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen += self.__onShowDeathScreen
            deathScreenCtrl.onHideDeathScreen += self.__onHideDeathScreen
        arena = avatar_getter.getArena()
        if arena:
            self.__isInSquad = arena.bonusType == ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD
        else:
            _logger.warning("Couldn't detect squad mode because arena is not defined!")
        if self.__isInSquad:
            title = BATTLE_ROYALE.PLAYERSTATS_TITLE
        else:
            title = ''
        self.as_setInitDataS(title)

    def _destroy(self):
        deathScreenCtrl = self.__sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen -= self.__onShowDeathScreen
            deathScreenCtrl.onHideDeathScreen -= self.__onHideDeathScreen
        super(BattleRoyalePlayerStats, self)._destroy()

    def __onHideDeathScreen(self):
        self.as_setDataS([])

    def __onShowDeathScreen(self):
        self.as_setDataS(IngameBattleRoyaleResultsViewDataFormatter(self.__sessionProvider, {}).getSummaryStats())
