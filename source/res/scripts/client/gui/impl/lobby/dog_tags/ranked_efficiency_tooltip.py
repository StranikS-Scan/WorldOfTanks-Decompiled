# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/ranked_efficiency_tooltip.py
import typing
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.ranked_efficiency_tooltip_model import RankedEfficiencyTooltipModel
from gui.impl.gen.view_models.views.lobby.dog_tags.ranked_season_efficiency_model import RankedSeasonEfficiencyModel
from gui.impl.pub import ViewImpl
from gui.ranked_battles.constants import RankedDossierKeys, SeasonResultTokenPatterns
from gui.ranked_battles.constants import SEASON_IDS_RB_2020
from helpers import dependency
from dog_tags_common.config.common import ComponentViewType
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
EFFICIENCY_DIGITS = 2

class RankedEfficiencyTooltip(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.dog_tags.RankedEfficiencyTooltip(), model=RankedEfficiencyTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(RankedEfficiencyTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedEfficiencyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RankedEfficiencyTooltip, self)._onLoading(*args, **kwargs)
        if self.__rankedController.hasAnySeason():
            with self.viewModel.transaction() as model:
                items = model.getItems()
                self.__addPassedSeasons(items)
                items.invalidate()

    def __addPassedSeasons(self, itemsArr):
        seasons = SEASON_IDS_RB_2020
        playerDogTag = BigWorld.player().dogTags.getDisplayableDT()
        engraving = playerDogTag.getComponentByType(ComponentViewType.ENGRAVING)
        currentEngravingValue = round(engraving.value, EFFICIENCY_DIGITS)
        for seasonID in seasons:
            efficiency = 0
            if self.__checkInLeague(seasonID):
                efficiency = self.__getPassedSeasonEfficiency(seasonID, seasons.index(seasonID) + 1)
                if efficiency == currentEngravingValue:
                    efficiencyState = RankedSeasonEfficiencyModel.EFFICIENCY_BEST
                else:
                    efficiencyState = RankedSeasonEfficiencyModel.EFFICIENCY_DEFAULT
            else:
                efficiencyState = RankedSeasonEfficiencyModel.EFFICIENCY_OUT_OF_LEAGUE
            itemsArr.addViewModel(self.__getSeasonModel(efficiency, RankedSeasonEfficiencyModel.PERIOD_PAST, efficiencyState))

    def __addCurrentSeason(self, itemsArr):
        currentSeason = self.__rankedController.getCurrentSeason()
        if currentSeason:
            itemsArr.addViewModel(self.__getSeasonModel(0, RankedSeasonEfficiencyModel.PERIOD_CURRENT, RankedSeasonEfficiencyModel.WAITING_AWARDS))

    def __addFutureSeasons(self, itemsArr):
        expectedSeasons = self.__rankedController.getExpectedSeasons()
        counter = expectedSeasons - len(itemsArr)
        while counter > 0:
            itemsArr.addViewModel(self.__getSeasonModel(0, RankedSeasonEfficiencyModel.PERIOD_FUTURE))
            counter -= 1

    def __checkInLeague(self, seasonID):
        tokens = self.__itemsCache.items.tokens.getTokens()
        leagueTokenPatterns = (SeasonResultTokenPatterns.RANKED_OFF_GOLD_LEAGUE_TOKEN, SeasonResultTokenPatterns.RANKED_OFF_SILVER_LEAGUE_TOKEN, SeasonResultTokenPatterns.RANKED_OFF_BRONZE_LEAGUE_TOKEN)
        for pattern in leagueTokenPatterns:
            token = tokens.get(pattern.format(seasonID))
            if token:
                _, count = token
                return count > 0

        return False

    def __getPassedSeasonEfficiency(self, seasonID, seasonNumber):
        accountDossier = self.__itemsCache.items.getAccountDossier()
        seasonKey = RankedDossierKeys.SEASON % seasonNumber
        stats = accountDossier.getSeasonRanked15x15Stats(seasonKey, seasonID)
        stepsEfficiency = stats.getStepsEfficiency()
        return round(stepsEfficiency * 100, EFFICIENCY_DIGITS) if stepsEfficiency is not None else 0

    def __getSeasonModel(self, efficiency, state, efficiencyState=RankedSeasonEfficiencyModel.EFFICIENCY_OUT_OF_LEAGUE):
        model = RankedSeasonEfficiencyModel()
        model.setValue(efficiency)
        model.setPeriodState(state)
        model.setEfficiencyState(efficiencyState)
        return model
