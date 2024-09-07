# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_widget_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IWinbackController
from winback.gui.impl.lobby.tooltips.widget_tooltip_view import WidgetTooltipView
from winback.gui.impl.gen.view_models.views.lobby.views.winback_widget_view_model import WinbackWidgetViewModel, WinbackState
from winback.gui.shared.event_dispatcher import showProgressionView

class WinbackWidgetView(ViewImpl):
    __winbackController = dependency.descriptor(IWinbackController)
    __slots__ = ()

    def __init__(self, flags=ViewFlags.LOBBY_SUB_VIEW):
        settings = ViewSettings(R.views.winback.lobby.WinbackWidgetView())
        settings.flags = flags
        settings.model = WinbackWidgetViewModel()
        super(WinbackWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackWidgetView, self).getViewModel()

    def _onLoading(self):
        super(WinbackWidgetView, self)._onLoading()
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick), (self.__winbackController.winbackProgression.onProgressPointsUpdated, self.__updateModel), (self.__winbackController.winbackProgression.onSettingsChanged, self.__updateModel))

    def __onClick(self):
        if self.__winbackController.isProgressionEnabled():
            showProgressionView()

    def createToolTipContent(self, event, contentID):
        return WidgetTooltipView() if contentID == R.views.winback.lobby.tooltips.WidgetTooltipView() else super(WinbackWidgetView, self).createToolTipContent(event, contentID)

    def __updateModel(self, *_):
        state = WinbackState.DISABLE
        currentStage = 0
        if self.__winbackController.isProgressionEnabled():
            state = WinbackState.IN_PROGRESS
            if self.__winbackController.winbackProgression.isLastStage:
                state = WinbackState.LAST_STAGE
            elif self.__winbackController.winbackProgression.isFinished:
                state = WinbackState.COMPLETE
            currentStage = self.__winbackController.winbackProgression.getCurrentStage()
        self.viewModel.setState(state)
        self.viewModel.setLevel(currentStage)
        selectableRewardsCount = self.__winbackController.winbackOfferGiftTokenCount()
        self.viewModel.setSelectableRewardsCount(selectableRewardsCount)
        self.viewModel.setProgressionName(self.__winbackController.progressionName)
