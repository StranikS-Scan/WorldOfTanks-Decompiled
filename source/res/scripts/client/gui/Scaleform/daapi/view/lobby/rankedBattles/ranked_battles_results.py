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
    __slots__ = ('__rankedResultsVO', '__rankInfo', '__questsProgress')

    def __init__(self, ctx=None):
        super(RankedBattlesResults, self).__init__()
        self.__rankedResultsVO = ctx['rankedResultsVO']
        self.__rankInfo = ctx['rankInfo']
        self.__questsProgress = ctx['questsProgress']

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

    def __close(self):
        self.rankedController.showRankedAwardWindow(self.__rankInfo, self.__questsProgress)
        self.destroy()
