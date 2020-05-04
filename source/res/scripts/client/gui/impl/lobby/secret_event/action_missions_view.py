# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_missions_view.py
import logging
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_missions_model import ActionMissionsModel
from gui.impl.gen.view_models.views.lobby.secret_event.mission_model import MissionModel
from gui.impl.lobby.secret_event import RewardListMixin, ProgressMixin
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class ActionMissionsView(ActionViewWithMenu, RewardListMixin, ProgressMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ActionMissionsModel()
        super(ActionMissionsView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = RewardListMixin.createToolTip(self, event)
            if window is None:
                tankId = event.getArgument('tankId', None)
                specialArgs = [int(tankId)] if tankId is not None else []
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=event.getArgument('tooltipId'), specialArgs=specialArgs), self.getParentWindow())
                window.load()
            if window:
                return window
        return super(ActionMissionsView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(ActionMissionsView, self)._initialize()
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted

    def _onLoading(self, *args, **kwargs):
        super(ActionMissionsView, self)._onLoading()
        self.__fillViewModel()

    def _finalize(self):
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        super(ActionMissionsView, self)._finalize()

    def __fillViewModel(self):
        vm = self.viewModel
        vm.setCurrentView(ActionMenuModel.MISSION)
        heroTank = self.gameEventController.getHeroTank()
        vm.prizeTank.setTankId(heroTank.getVehicleCD())
        vm.prizeTank.setTankName(heroTank.getInventoryItem().shortUserName)
        self.__fillMissions()

    def _createOrUpdateMission(self, data, mission=None):
        if mission is None:
            mission = MissionModel()
        mission.setIsCompleted(data.isCompleted)
        mission.setIsAvailable(data.isAvailable)
        mission.setStage(data.level)
        mission.setMaxProgress(data.maxProgress)
        mission.setProgress(data.currentProgress)
        return mission

    def __fillMissions(self):
        self.viewModel.missionList.clearItems()
        for idx, progressionData in enumerate(self.getAllProgressionData(self.gameEventController.getCurrentFront())):
            mission = self._createOrUpdateMission(progressionData)
            self.fillStubRewardList(mission.rewardList, self.getRewards(progressionData.gameEventItem, idx), progressionData.isCompleted, idx)
            self.viewModel.missionList.addViewModel(mission)

        self.viewModel.missionList.invalidate()

    def __onSyncCompleted(self, *_):
        self.__fillMissions()
