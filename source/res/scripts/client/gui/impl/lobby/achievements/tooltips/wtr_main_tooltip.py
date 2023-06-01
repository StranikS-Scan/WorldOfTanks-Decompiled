# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/tooltips/wtr_main_tooltip.py
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.achievements.rank_model import RankModel
from gui.impl.gen.view_models.views.lobby.achievements.tooltips.wtr_main_tooltip_view_model import WtrMainTooltipViewModel
from gui.impl.lobby.achievements.profile_utils import getNormalizedValue
from achievements20.WTRStageChecker import WTRStageChecker
from gui.impl.gen import R
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class WTRMainTooltip(ViewImpl):
    __slots__ = ('__userId',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, userId):
        settings = ViewSettings(R.views.lobby.achievements.tooltips.WTRMainTooltip(), model=WtrMainTooltipViewModel())
        self.__userId = userId
        super(WTRMainTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTRMainTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WTRMainTooltip, self)._onLoading(*args, **kwargs)
        randomStats = self.__itemsCache.items.getAccountDossier(self.__userId).getRandomStats()
        achievements20GeneralConfig = self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        accountWtr = getNormalizedValue(self.__itemsCache.items.getWTR(self.__userId))
        stages = achievements20GeneralConfig.getStagesOfWTR()
        currentStage = WTRStageChecker(stages).getStage(accountWtr)
        battlesLeftCount = achievements20GeneralConfig.getRequiredCountOfBattles() - randomStats.getBattlesCount()
        with self.viewModel.transaction() as model:
            model.setRequiredNumberOfBattles(0 if battlesLeftCount < 0 else battlesLeftCount)
            if currentStage:
                model.setRank(currentStage[0])
                model.setSubRank(currentStage[1])
                model.setCurrentPoints(accountWtr)
            self.__fillRanks(model, stages)

    def __fillRanks(self, model, stages):
        ranks = model.getRanks()
        ranks.clear()
        for rank, subRanks in enumerate(stages):
            for subRank, countOfPoints in enumerate(subRanks):
                rankModel = RankModel()
                rankModel.setRank(rank + 1)
                rankModel.setSubRank(subRank + 1)
                rankModel.setCountOfPoints(countOfPoints)
                ranks.addViewModel(rankModel)
