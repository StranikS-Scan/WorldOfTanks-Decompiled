# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_main_widget_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_level_info import NyLevelInfo
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_main_widget_tooltip_model import NyMainWidgetTooltipModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from new_year.ny_level_helper import NewYearAtmospherePresenter
from uilogging.ny.loggers import NyMainWidgetTooltipLogger

class NyMainWidgetTooltip(View):
    __uiLogger = NyMainWidgetTooltipLogger()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMainWidgetTooltip())
        settings.model = NyMainWidgetTooltipModel()
        super(NyMainWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMainWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevel()
        currentPoints, toPoints = NewYearAtmospherePresenter.getLevelProgress()
        with self.viewModel.transaction() as model:
            model.setCurrentLevel(level)
            model.setCurrentPoints(currentPoints)
            model.setToPoints(toPoints)
            model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            self.__updateLevels(model)
        self.__uiLogger.start()

    def __updateLevels(self, model):
        levels = model.getLevels()
        levels.clear()
        atmosphereLimits = NewYearAtmospherePresenter.getAtmosphereLevelLimits()
        maxLevel = len(atmosphereLimits)
        for level, limit in enumerate(atmosphereLimits):
            levelInfo = NyLevelInfo()
            nextLevel = level + 1
            finalPoints = atmosphereLimits[nextLevel] - 1 if nextLevel < maxLevel else limit
            levelInfo.setLevel(nextLevel)
            levelInfo.setInitialPoints(limit)
            levelInfo.setFinalPoints(finalPoints)
            levels.addViewModel(levelInfo)

        levels.invalidate()

    def _finalize(self):
        self.__uiLogger.stop(NewYearNavigation.getCurrentObject() is None)
        return
