# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_results.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ENABLE_RANKED_ANIMATIONS
from gui.Scaleform.daapi.view.meta.RankedBattlesBattleResultsMeta import RankedBattlesBattleResultsMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesResults(RankedBattlesBattleResultsMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__rankedResultsVO', '__rankInfo', '__questsProgress', '__showRankedWidget__currentRanks', '__currentRankID', '__lastRankID', '__lastMaxRankID')

    def __init__(self, ctx=None):
        super(RankedBattlesResults, self).__init__()
        self.__rankedResultsVO = ctx['rankedResultsVO']
        self.__rankInfo = ctx['rankInfo']
        self.__questsProgress = ctx['questsProgress']
        self.__showRankedWidget = self.__rankedResultsVO.get('showWidgetAnimation', True)
        if self.__showRankedWidget:
            prevAccProgress = (self.__rankInfo.prevAccRank, self.__rankInfo.prevAccStep)
            accProgress = (self.__rankInfo.accRank, self.__rankInfo.accStep)
            maxProgress = max(accProgress, prevAccProgress)
            prevShields = self.__rankInfo.prevShields
            shields = self.__rankInfo.shields
            isBonusBattle = self.__rankInfo.isBonusBattle
            self.__currentRanks = self.rankedController.getRanksChainExt(accProgress, prevAccProgress, maxProgress, shields, prevShields, isBonusBattle)
            self.__currentRankID, _ = accProgress
            self.__lastRankID, _ = prevAccProgress
            self.__lastMaxRankID, _ = maxProgress

    def onWidgetUpdate(self):
        self.__updateRankedWidget()

    def onClose(self):
        self.__close()

    def animationCheckBoxSelected(self, value):
        AccountSettings.setSettings(ENABLE_RANKED_ANIMATIONS, value)

    @property
    def rankedWidget(self):
        return self.getComponent(RANKEDBATTLES_ALIASES.RANKED_BATTLE_RESULTS_WIDGET)

    def _populate(self):
        super(RankedBattlesResults, self)._populate()
        self.as_setDataS(self.__rankedResultsVO)

    def __updateRankedWidget(self):
        if self.rankedWidget is not None:
            self.rankedWidget.update(self.__lastRankID, self.__lastMaxRankID, self.__currentRankID, self.__currentRanks)
        return

    def __close(self):
        if not self.__showRankedWidget:
            self.rankedController.showRankedAwardWindow(self.__rankInfo, self.__questsProgress)
        self.destroy()
