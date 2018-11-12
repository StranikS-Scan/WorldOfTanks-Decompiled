# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/ingame_rank_panel.py
from gui.Scaleform.daapi.view.meta.EpicInGameRankMeta import EpicInGameRankMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_MAX_IN_GAME_RANK = 5

class InGameRankPanel(EpicInGameRankMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(InGameRankPanel, self)._populate()
        self.__rankThresholds = []
        self.__currentRank = 0
        self.__currentExp = 0
        self.__waitingForLevelUp = False
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerXPUpdated += self.__onPlayerXPUpdated
            self.__rankThresholds = playerDataComp.getTresholdForRanks()
            self.__currentExp = playerDataComp.playerXP
            self.__setCurrentRank()
        return

    def _dispose(self):
        super(InGameRankPanel, self)._dispose()
        playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerXPUpdated -= self.__onPlayerXPUpdated
        return

    def levelUpAnimationComplete(self):
        self.__waitingForLevelUp = False
        self.__setCurrentRank()

    def __setCurrentRank(self):
        self.__currentRank = self.__getRank(self.__currentExp)
        self.as_setRankS({'rank': self.__currentRank,
         'isMaxRank': self.__currentRank == _MAX_IN_GAME_RANK,
         'previousProgress': 0,
         'newProgress': self.__getThresholdPercentage(self.__currentExp),
         'rankText': str(self.__currentRank)})

    def __getThresholdPercentage(self, expValue):
        activeRank = self.__getRank(expValue)
        result = 0
        if activeRank != _MAX_IN_GAME_RANK:
            normalizedExpValue = expValue - self.__rankThresholds[activeRank]
            nextRankLevelCap = self.__rankThresholds[activeRank + 1] - self.__rankThresholds[activeRank]
            result = float(normalizedExpValue) / float(nextRankLevelCap)
        return round(max(0.0, result - 0.005), 2)

    def __getRank(self, progressValue):
        result = -1
        for rankThreshold in self.__rankThresholds:
            if progressValue >= rankThreshold:
                result = result + 1
            break

        return result

    def __onPlayerXPUpdated(self, exp):
        oldExp = self.__currentExp
        self.__currentExp = exp
        newRank = self.__getRank(exp)
        if newRank == self.__currentRank and not self.__waitingForLevelUp:
            self.as_updateProgressS(self.__getThresholdPercentage(oldExp), self.__getThresholdPercentage(self.__currentExp))
        elif newRank != self.__currentRank and not self.__waitingForLevelUp:
            self.__waitingForLevelUp = True
            self.as_triggerLevelUpS(self.__getThresholdPercentage(oldExp))
