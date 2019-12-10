# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_widget_tooltip.py
from frameworks.wulf import ViewFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_widget_tooltip_model import NewYearWidgetTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_multiplier_value import NewYearMultiplierValue
from helpers import int2roman
from new_year.ny_level_helper import NewYearAtmospherePresenter
from items import new_year
from new_year.ny_bonuses import getBonusConfig
from gui.impl import backport
from gui.impl.new_year.new_year_helper import fillBonusFormula

class NewYearWidgetTooltip(View):
    __slots__ = ()

    def __init__(self):
        super(NewYearWidgetTooltip, self).__init__(ViewSettings(R.views.lobby.new_year.tooltips.new_year_widget_tooltip.NewYearWidgetTooltip(), flags=ViewFlags.COMPONENT, model=NewYearWidgetTooltipModel()))

    @property
    def viewModel(self):
        return super(NewYearWidgetTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevel()
        leftLevel = level if level != new_year.CONSTS.MAX_ATMOSPHERE_LVL else level - 1
        currentPoints, nextPoints = NewYearAtmospherePresenter.getLevelProgress()
        fillBonusFormula(self.viewModel.bonusFormula)
        with self.viewModel.transaction() as tx:
            tx.setCurrentLevel(int2roman(leftLevel))
            tx.setNextLevel(int2roman(leftLevel + 1))
            tx.setCurrentPoints(currentPoints)
            tx.setNextPoints(nextPoints)
            self.__createMultipliersTable(tx, level)

    def __createMultipliersTable(self, tx, currentLevel):
        multipliersList = getBonusConfig().getAtmosphereMultipliers()
        rangedMultipliersList = [ (multi, i + 1, i + multipliersList.count(multi)) for i, multi in enumerate(multipliersList) if multi != multipliersList[i - 1] ]
        for multiplierRange in rangedMultipliersList:
            multiplier, fromLevel, toLevel = multiplierRange
            singleLevel = fromLevel == toLevel
            levelInterval = int2roman(fromLevel) if singleLevel else backport.text(R.strings.ny.widgetTooltip.levelsPattern(), lower=int2roman(fromLevel), higher=int2roman(toLevel))
            tableRow = NewYearMultiplierValue()
            tableRow.setMultiplier(multiplier)
            tableRow.setLevels(levelInterval)
            tableRow.setIsEnabled(fromLevel <= currentLevel <= toLevel)
            tx.multipliersTable.addViewModel(tableRow)
