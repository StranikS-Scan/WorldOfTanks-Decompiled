# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/progression_widget.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.hangar_selectable_view import HangarSelectableView
from helpers import dependency
from historical_battles.gui.shared.event_dispatcher import showHBProgressionView
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.lobby.tooltips.hb_progression_widget_tooltip import HbProgressionWidgetTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.gen.view_models.views.lobby.progression_widget_model import ProgressionWidgetModel
_logger = logging.getLogger(__name__)

class ProgressionWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return ProgressionWidgetView(R.views.historical_battles.lobby.ProgressionWidget())


class ProgressionWidgetView(HangarSelectableView):
    __gameEventController = dependency.descriptor(IGameEventController)
    __hbProgressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ProgressionWidgetModel()
        super(ProgressionWidgetView, self).__init__(settings)
        self.__tooltipEnabled = True

    @property
    def viewModel(self):
        return super(ProgressionWidgetView, self).getViewModel()

    def _getEvents(self):
        return ((self.__hbProgressionController.onProgressPointsUpdated, self.__updateModel), (self.__gameEventController.frontDataUpdated, self.__onFrontDataUpdated))

    def createToolTipContent(self, event, contentID):
        if not self.__tooltipEnabled:
            return None
        elif event.contentID == R.views.historical_battles.lobby.tooltips.ProgressionWidgetTooltip():
            return HbProgressionWidgetTooltip()
        else:
            return HbCoinTooltip() if event.contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip() else super(ProgressionWidgetView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ProgressionWidgetView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            currPoints = self.__hbProgressionController.getCurPoints()
            stageData = self.__hbProgressionController.getCurrentStageData()
            model.setPoints(currPoints)
            model.setLevel(stageData.get('currentStage'))
            model.setProgressionCurrent(stageData.get('stagePoints'))
            model.setProgressionTotal(stageData.get('stageMaxPoints'))

    def __onFrontDataUpdated(self, *_):
        self.__updateModel()

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        super(ProgressionWidgetView, self)._finalize()

    def __onClick(self):
        showHBProgressionView()
