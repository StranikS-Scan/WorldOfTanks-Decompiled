# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_main_widget_tooltip.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_LAST_SEEN_LEVEL_INFO
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_multiplier_value import NyMultiplierValue
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_main_widget_tooltip_model import NyMainWidgetTooltipModel
from new_year.ny_level_helper import NewYearAtmospherePresenter
from items import new_year
from new_year.ny_bonuses import getBonusConfig
from gui.impl import backport
from gui.impl.new_year.new_year_helper import fillBonusFormula, formatRomanNumber

class NyMainWidgetTooltip(View):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMainWidgetTooltip())
        settings.model = NyMainWidgetTooltipModel()
        super(NyMainWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMainWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevel()
        leftLevel = level if level != new_year.CONSTS.MAX_ATMOSPHERE_LVL else level - 1
        currentPoints, nextPoints = NewYearAtmospherePresenter.getLevelProgress()
        lastState = AccountSettings.getUIFlag(NY_LAST_SEEN_LEVEL_INFO)
        delta = lastState['points'] if lastState['level'] == leftLevel else 0
        fillBonusFormula(self.viewModel.bonusFormula)
        with self.viewModel.transaction() as tx:
            tx.setCurrentLevel(formatRomanNumber(leftLevel))
            tx.setNextLevel(formatRomanNumber(leftLevel + 1))
            tx.setCurrentPoints(currentPoints)
            tx.setNextPoints(nextPoints)
            tx.setDeltaFromPoints(delta)
            self.__createMultipliersTable(tx, level)
        AccountSettings.setUIFlag(NY_LAST_SEEN_LEVEL_INFO, {'level': leftLevel,
         'points': currentPoints})

    def _finalize(self):
        pass

    def __createMultipliersTable(self, tx, currentLevel):
        multipliersList = getBonusConfig().getAtmosphereMultipliers()
        rangedMultipliersList = [ (multi, i + 1, i + multipliersList.count(multi)) for i, multi in enumerate(multipliersList) if multi != multipliersList[i - 1] ]
        for multiplierRange in rangedMultipliersList:
            multiplier, fromLevel, toLevel = multiplierRange
            singleLevel = fromLevel == toLevel
            levelInterval = formatRomanNumber(fromLevel) if singleLevel else backport.text(R.strings.ny.widgetTooltip.levelsPattern(), lower=formatRomanNumber(fromLevel), higher=formatRomanNumber(toLevel))
            tableRow = NyMultiplierValue()
            tableRow.setMultiplier(int(multiplier))
            tableRow.setLevels(levelInterval)
            tableRow.setIsEnabled(fromLevel <= currentLevel <= toLevel)
            tx.multipliersTable.addViewModel(tableRow)
