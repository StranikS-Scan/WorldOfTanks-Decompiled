# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/entry_point_presenter.py
from comp7_light.gui.impl.gen.view_models.views.lobby.entry_point_model import EntryPointModel, ProgressionState
from comp7_light.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import State
from comp7_light.gui.impl.lobby.comp7_light_helpers.account_settings import setUmgProgressionPointsSeen, getPrevUmgProgressionPointsSeen, markUmgEntryPointSeen, getUmgEntryPointSeen
from comp7_light.gui.impl.lobby.tooltips.leaderboard_reward_tooltip import LeaderboardRewardTooltipView
from comp7_light.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7LightOverlapCtrlMixin
from comp7_light.gui.shared.event_dispatcher import showComp7LightProgressionView
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin

class EntryPointPresenter(TooltipPositionerMixin, Comp7LightOverlapCtrlMixin, ViewComponent[EntryPointModel], IGlobalListener):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionController)

    def __init__(self):
        super(EntryPointPresenter, self).__init__(model=EntryPointModel)

    @property
    def viewModel(self):
        return super(EntryPointPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.startGlobalListening()
        self.initOverlapCtrl()
        self._updateViewModel()
        super(EntryPointPresenter, self)._onLoading(args, kwargs)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7_light.mono.lobby.leaderboard_reward_tooltip_view():
            isInProgress = self.__comp7LightProgressionController.isEnabled and not self.__comp7LightProgressionController.isFinished
            return LeaderboardRewardTooltipView(State.INPROGRESS if isInProgress else State.COMPLETED)
        return super(EntryPointPresenter, self).createToolTipContent(event, contentID)

    def _updateViewModel(self):
        self.queueUpdate()

    def _rawUpdate(self):
        super(EntryPointPresenter, self)._rawUpdate()
        data = self.__comp7LightProgressionController.getProgressionData()
        currentStage = 0
        isInProgress = self.__comp7LightProgressionController.isEnabled and not self.__comp7LightProgressionController.isFinished
        if isInProgress:
            currentStage = self.__comp7LightProgressionController.getCurrentStageData().get('currentStage')
        with self.viewModel.transaction() as model:
            model.setCurrentStage(currentStage)
            model.setCurProgressPoints(data['curPoints'])
            model.setPrevProgressPoints(getPrevUmgProgressionPointsSeen())
            model.setIsEntryPointAnimationSeen(getUmgEntryPointSeen())
            model.setPointsForLevel(data['pointsForLevel'])
            model.setState(ProgressionState.INPROGRESS if isInProgress else ProgressionState.COMPLETED)

    def _getEvents(self):
        return super(EntryPointPresenter, self)._getEvents() + ((self.viewModel.onOpenProgression, self.__onOpenProgression),
         (self.viewModel.onAnimationEnd, self.__onAnimationEnd),
         (self.viewModel.onEntryPointAnimationSeen, self.__onEntryPointAnimationSeen),
         (self.__comp7LightProgressionController.onProgressPointsUpdated, self._updateViewModel),
         (self.__comp7LightProgressionController.onSettingsChanged, self._updateViewModel))

    def __onAnimationEnd(self):
        setUmgProgressionPointsSeen(self.__comp7LightProgressionController.getProgressionData()['curPoints'])

    def __onEntryPointAnimationSeen(self):
        markUmgEntryPointSeen()
        self.viewModel.setIsEntryPointAnimationSeen(True)

    def _finalize(self):
        super(EntryPointPresenter, self)._finalize()
        self.stopGlobalListening()

    @staticmethod
    def __onOpenProgression():
        showComp7LightProgressionView()
