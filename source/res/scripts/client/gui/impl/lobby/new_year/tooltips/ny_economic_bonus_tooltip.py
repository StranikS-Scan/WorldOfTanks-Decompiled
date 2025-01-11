# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_economic_bonus_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_economic_bonus_model import NyEconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_economic_bonus_tooltip_model import NyEconomicBonusTooltipModel
from gui.impl.pub import ViewImpl
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_bonuses import EconomicBonusHelper, getBonusTokensDependencies, toPrettyCumulativeBonusValue, toPrettySingleBonusValue
from new_year.ny_constants import GuestsQuestsTokens

class NyEconomicBonusTooltip(ViewImpl):

    def __init__(self, isMaxBonus, index, guestName):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip())
        settings.model = NyEconomicBonusTooltipModel()
        super(NyEconomicBonusTooltip, self).__init__(settings)
        self.__isMaxBonus = isMaxBonus
        self.__index = index
        self.__guestName = guestName

    @property
    def viewModel(self):
        return super(NyEconomicBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyEconomicBonusTooltip, self)._onLoading()
        dependenciesTokens = getBonusTokensDependencies()
        totalQuests = len(GuestsQuestsConfigHelper.getQuestsWithRewards(dependenciesTokens))
        with self.viewModel.transaction() as model:
            self.__updateEconomicBonus(model)
            model.setIsMaxBonus(self.__isMaxBonus)
            model.setTotalQuestsQuantity(totalQuests)

    def __updateEconomicBonus(self, model):
        if self.__isMaxBonus:
            bonusesData = EconomicBonusHelper.getMaxBonuses()
            prittyFn = toPrettyCumulativeBonusValue
        elif self.__index >= -1:
            dependency = GuestsQuestsTokens.getGuestCompletedTokenName(self.__guestName)
            bonusesData = EconomicBonusHelper.getBonusesDataByToken(dependency, self.__index)
            prittyFn = toPrettySingleBonusValue
        else:
            bonusesData = EconomicBonusHelper.getBonusesDataInventory()
            prittyFn = toPrettyCumulativeBonusValue
        eBonuses = model.getEconomicBonuses()
        for bName, value in bonusesData.iteritems():
            bonus = NyEconomicBonusModel()
            bonus.setBonusName(bName)
            bonus.setBonusValue(prittyFn(value))
            eBonuses.addViewModel(bonus)

        eBonuses.invalidate()
