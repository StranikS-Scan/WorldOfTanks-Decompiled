# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/tooltips/widget_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.server_events.events_helpers import EventInfoModel
from helpers import dependency
from skeletons.gui.game_control import IWinbackController
from winback.gui.impl.gen.view_models.views.lobby.tooltips.widget_tooltip_view_model import WidgetTooltipViewModel, WinbackState

class WidgetTooltipView(ViewImpl):
    __winbackController = dependency.descriptor(IWinbackController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.winback.lobby.tooltips.WidgetTooltipView())
        settings.flags = ViewFlags.VIEW
        settings.model = WidgetTooltipViewModel()
        super(WidgetTooltipView, self).__init__(settings)

    def _onLoading(self):
        super(WidgetTooltipView, self)._onLoading()
        self.__updateModel()

    @property
    def viewModel(self):
        return super(WidgetTooltipView, self).getViewModel()

    def __updateModel(self):
        isEnabled = self.__winbackController.isProgressionEnabled()
        isInProgress = isEnabled and not self.__winbackController.winbackProgression.isFinished
        state = WinbackState.DISABLE
        if isEnabled:
            state = WinbackState.IN_PROGRESS if isInProgress else WinbackState.COMPLETE
            availableQuests = self.__winbackController.winbackProgression.questContainer.getAvailableQuests()
            allQuestsCompleted = all((q.isCompleted() for q in availableQuests.itervalues()))
            self.viewModel.setIsTimerDisplayed(allQuestsCompleted)
            newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
            self.viewModel.setCurrentTimerDate(newCountdownVal)
        self.viewModel.setState(state)
        self.viewModel.setProgressionName(self.__winbackController.progressionName)
