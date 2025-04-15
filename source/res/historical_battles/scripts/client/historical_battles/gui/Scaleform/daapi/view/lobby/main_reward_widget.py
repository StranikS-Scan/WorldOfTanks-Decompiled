# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/main_reward_widget.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from helpers import dependency
from gui.impl.lobby.hangar_selectable_view import HangarSelectableView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.gen.view_models.views.lobby.stage_model import StageModel
from historical_battles.gui.impl.gen.view_models.views.lobby.main_reward_widget_model import MainRewardWidgetModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class MainRewardWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return MainRewardWidgetView(R.views.historical_battles.lobby.MainRewardWidget())


class MainRewardWidgetView(HangarSelectableView):
    __gameEventController = dependency.descriptor(IGameEventController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hbProgressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = MainRewardWidgetModel()
        super(MainRewardWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MainRewardWidgetView, self).getViewModel()

    def _getEvents(self):
        return ((self.__hbProgressionController.onProgressPointsUpdated, self.__updateModel),
         (self.__gameEventController.frontDataUpdated, self.__onFrontDataUpdated),
         (self.__gameEventController.onFrontTimeStatusUpdated, self.__onFrontTimeStatusUpdated),
         (self.__eventsCache.onSyncCompleted, self.__updateModel))

    def __fillStages(self, model):
        fronts = self.__gameEventController.frontController.getFronts()
        stagesModel = model.getStages()
        stagesModel.clear()
        for frontId, front in fronts.iteritems():
            stageModel = StageModel()
            stageData = self.__hbProgressionController.getCurrentStageDataForFront(frontId)
            total = self.__hbProgressionController.getMaxProgressionLevelForFront(frontId)
            stageModel.setFrontType(front.getName())
            stageModel.setTotalLevel(total)
            stageModel.setCurrentLevel(stageData.get('currentStage'))
            stageModel.setTotalLevelProgress(stageData.get('stageMaxPoints'))
            stageModel.setCurrentLevelProgress(stageData.get('stagePoints'))
            self.__setDate(frontId, stageModel)
            stagesModel.addViewModel(stageModel)

        stagesModel.invalidate()

    def __setDate(self, frontId, model):
        delta = self.__gameEventController.getTimeLeftToStartFront(frontId)
        model.setDate(delta)

    def __setCurrentFront(self, model):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        model.setCurrentFrontType(currentFront.getName())

    def _onLoading(self, *args, **kwargs):
        super(MainRewardWidgetView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__setCurrentFront(model)
            self.__fillStages(model)

    def __onFrontDataUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__setCurrentFront(model)

    def __onFrontTimeStatusUpdated(self, frontId):
        self.__updateModel()

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        super(MainRewardWidgetView, self)._finalize()

    @staticmethod
    def __onClick():
        pass
