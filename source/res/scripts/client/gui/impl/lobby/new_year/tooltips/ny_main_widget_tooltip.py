# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_main_widget_tooltip.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_LAST_SEEN_LEVEL_INFO
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from helpers import dependency, time_utils
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_main_widget_tooltip_model import NyMainWidgetTooltipModel
from items.components.ny_constants import MAX_ATMOSPHERE_LVL
from new_year.ny_level_helper import NewYearAtmospherePresenter
from gui.impl.new_year.new_year_helper import formatRomanNumber
from skeletons.new_year import INewYearController

class NyMainWidgetTooltip(View):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMainWidgetTooltip())
        settings.model = NyMainWidgetTooltipModel()
        super(NyMainWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMainWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevel()
        leftLevel = level if level != MAX_ATMOSPHERE_LVL else level - 1
        currentPoints, nextPoints = NewYearAtmospherePresenter.getLevelProgress()
        lastState = AccountSettings.getNewYear(NY_LAST_SEEN_LEVEL_INFO)
        delta = lastState['points'] if lastState['level'] == leftLevel else 0
        with self.viewModel.transaction() as tx:
            tx.setCurrentLevel(formatRomanNumber(leftLevel))
            tx.setNextLevel(formatRomanNumber(leftLevel + 1))
            tx.setCurrentPoints(currentPoints)
            tx.setNextPoints(nextPoints)
            tx.setDeltaFromPoints(delta)
            tx.setSecondsLeft(int(time_utils.getTimeDeltaFromNowInLocal(self.__nyController.getFinishTime())))
        AccountSettings.setNewYear(NY_LAST_SEEN_LEVEL_INFO, {'level': leftLevel,
         'points': currentPoints})

    def _finalize(self):
        pass
