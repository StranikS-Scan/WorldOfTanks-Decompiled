# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_qualification_rewards.py
from collections import OrderedDict
from frameworks.wulf import ViewFlags, ViewSettings
from helpers import dependency
from shared_utils import first
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_qualification_rewards_view_model import RankedQualificationRewardsViewModel
from gui.impl.gen.view_models.views.lobby.ranked.ranked_qualification_rewards_battle_bonus_model import RankedQualificationRewardsBattleBonusModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.ranked_battles.constants import ZERO_RANK_ID
from skeletons.gui.game_control import IRankedBattlesController

class RankedQualificationRewardsView(ViewImpl):
    __slots__ = ('__quests', '__totalBattles', '__currentBattles', '__tooltipItems')
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.ranked.QualificationRewardsView())
        settings.flags = flags
        settings.model = RankedQualificationRewardsViewModel()
        self.__updateData()
        super(RankedQualificationRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedQualificationRewardsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(RankedQualificationRewardsView, self)._initialize(*args, **kwargs)
        self.__rankedController.onUpdated += self.__update

    def _finalize(self):
        self.__tooltipItems = None
        self.__rankedController.onUpdated -= self.__update
        super(RankedQualificationRewardsView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(RankedQualificationRewardsView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RankedQualificationRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def __update(self):
        self.__updateData()
        self.__updateViewModel()

    def __updateData(self):
        self.__tooltipItems = {}
        divisionID = self.__rankedController.getDivision(ZERO_RANK_ID).getID()
        stats = self.__rankedController.getStatsComposer()
        self.__quests = OrderedDict(sorted(self.__rankedController.getQualificationQuests().items()))
        self.__totalBattles = self.__rankedController.getTotalQualificationBattles()
        self.__currentBattles = stats.divisionsStats.get(divisionID, {}).get('battles', 0)
        self.__quests[self.__totalBattles] = first(self.__rankedController.getQuestsForRank(ZERO_RANK_ID + 1).values())

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setCurrentProgress(self.__currentBattles)
            tx.setTotalProgress(self.__totalBattles)
            battleBonuses = tx.getBattleBonuses()
            battleBonuses.clear()
            with battleBonuses.transaction() as bbtx:
                for battle in self.__quests:
                    battleBonus = RankedQualificationRewardsBattleBonusModel()
                    battleBonus.setBattlesCount(battle)
                    bonusesModel = battleBonus.getBonuses()
                    packBonusModelAndTooltipData(self.__quests[battle].getBonuses(), bonusesModel, self.__tooltipItems)
                    bbtx.addViewModel(battleBonus)


class RankedQualificationRewards(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = RankedQualificationRewardsView(flags=ViewFlags.COMPONENT)
        return self.__view
