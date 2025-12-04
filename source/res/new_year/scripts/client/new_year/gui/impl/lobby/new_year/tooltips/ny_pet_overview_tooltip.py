# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_pet_overview_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_pet_overview_tooltip_model import NyPetOverviewTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import IndicatorType
from new_year.gui.impl.lobby.new_year.pet.ny_pet_indicators_block import NyPetIndicatorsBlock
from new_year.ny_constants import PERCENT
from new_year.skeletons.new_year import ITamagotchiDataProvider, INewYearController

class NyPetOverviewTooltip(ViewImpl):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyPetOverviewTooltip())
        settings.model = NyPetOverviewTooltipModel()
        super(NyPetOverviewTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        self.__updateModel()
        super(NyPetOverviewTooltip, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self._dataProvider.onSimulationEnd, self.__onSimulationEnd),
         (self._dataProvider.onBonusUpdated, self.__onBonusUpdated),
         (self._dataProvider.onGiftCountUpdated, self.__onGiftCountUpdated),
         (self._dataProvider.onSeasonEnded, self.__onSeasonEnded))

    def __updateModel(self):
        with self.getViewModel().transaction() as tx:
            tx.setIsLeaderboard(not self._dataProvider.isLeaderboardFinished and self._dataProvider.playerInfo.leaderboardPoint > 0)
            tx.setMailsAmount(self._dataProvider.playerInfo.giftCount)
            self.__fillBonus(tx)
            self.__fillIndicators(tx)

    def __fillBonus(self, tx):
        maxBonus = self._nyController.getMaxBonusValue() * PERCENT
        constBonus = self._nyController.getActiveSettingBonusValue() * PERCENT
        dynamicBonus = self._dataProvider.getDeb()
        tx.setCurrentBonus(constBonus + dynamicBonus)
        tx.setMinBonus(constBonus)
        tx.setMaxBonus(maxBonus)

    def __fillIndicators(self, tx):
        indicators = tx.getIndicators()
        indicators.clear()
        for indicatorName, points in self._dataProvider.playerInfo.indicators.iteritems():
            vm = NyPetIndicatorModel()
            NyPetIndicatorsBlock.applyIndicatorData(indicatorName, vm, points)
            vm.setType(IndicatorType(indicatorName))
            indicators.addViewModel(vm)

        indicators.invalidate()

    def __onSimulationEnd(self):
        self.__updateModel()

    def __onBonusUpdated(self):
        with self.getViewModel().transaction() as tx:
            self.__fillBonus(tx)

    def __onGiftCountUpdated(self):
        with self.getViewModel().transaction() as tx:
            tx.setMailsAmount(self._dataProvider.playerInfo.giftCount)

    def __onSeasonEnded(self, _):
        if self._dataProvider.isLeaderboardFinished:
            with self.getViewModel().transaction() as tx:
                tx.setIsLeaderboard(False)
