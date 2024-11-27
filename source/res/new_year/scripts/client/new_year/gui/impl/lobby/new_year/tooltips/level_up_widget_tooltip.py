# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/level_up_widget_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.level_up_widget_tooltip_model import LevelUpWidgetTooltipModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.pub import ViewImpl

class LevelUpWidgetTooltip(ViewImpl):
    __slots__ = ('__currencyForLevelUpdate', '__customizationZone')

    def __init__(self, customizationZone):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.LevelUpWidgetTooltip())
        settings.model = LevelUpWidgetTooltipModel()
        super(LevelUpWidgetTooltip, self).__init__(settings)
        self.__customizationZone = customizationZone if customizationZone else NewYearNavigation.getCurrentObject()
        self.__currencyForLevelUpdate = NyCurrencyType.MANDARIN

    @property
    def viewModel(self):
        return super(LevelUpWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevelItem(self.__customizationZone)
        currencyCount = NewYearAtmospherePresenter.getLevelPrice(self.__customizationZone, level + 1)
        toysCount = len(NewYearAtmospherePresenter.getNewYearLevelToys(self.__customizationZone, level + 1))
        pointsCount = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(self.__customizationZone, level + 1)
        with self.viewModel.transaction() as model:
            model.setCustomizationZone(self.__customizationZone)
            model.setCurrentLevel(level)
            model.setCurrencyCount(currencyCount)
            model.currency.setValue(self.__currencyForLevelUpdate)
            model.setToysCount(toysCount)
            model.setPointsCount(pointsCount)
