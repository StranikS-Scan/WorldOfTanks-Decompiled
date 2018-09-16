# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/ingame_rank_panel.py
from gui.Scaleform.daapi.view.meta.EpicInGameRankMeta import EpicInGameRankMeta
from helpers import dependency
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import i18n
from skeletons.gui.battle_session import IBattleSessionProvider

class InGameRankPanel(EpicInGameRankMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(InGameRankPanel, self)._populate()
        self.as_setRankTextsS([i18n.makeString(EPIC_BATTLE.RANK_RANK0),
         i18n.makeString(EPIC_BATTLE.RANK_RANK1),
         i18n.makeString(EPIC_BATTLE.RANK_RANK2),
         i18n.makeString(EPIC_BATTLE.RANK_RANK3),
         i18n.makeString(EPIC_BATTLE.RANK_RANK4),
         i18n.makeString(EPIC_BATTLE.RANK_RANK5)])
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is not None:
            self.as_initRankS(playerDataComp.playerXP)
            playerDataComp.onPlayerXPUpdated += self.__onPlayerXPUpdated
            exp = playerDataComp.getTresholdForRanks()
            self.as_setRankExperienceLevelsS(exp)
        return

    def _dispose(self):
        super(InGameRankPanel, self)._dispose()
        playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerXPUpdated -= self.__onPlayerXPUpdated
        return

    def __onPlayerXPUpdated(self, exp):
        self.as_updatePlayerExperienceS(exp)
