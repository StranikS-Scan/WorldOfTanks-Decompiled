# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/stage_reward_view.py
from __future__ import absolute_import
import typing
import WWISE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from last_stand.gui.impl.gen.view_models.views.lobby.stage_reward_view_model import StageRewardViewModel
from last_stand.gui.impl.lobby.base_view import BaseView
from last_stand.gui.impl.lobby.ls_helpers import fillRewards
from last_stand.gui.impl.lobby.tooltips.booster_tooltip import BoosterTooltipView
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import RewardState, REWARD_WINDOW_ENTER, REWARD_WINDOW_EXIT
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from helpers import dependency
from ids_generators import SequenceIDGenerator
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, View
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class StageRewardView(BaseView):
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsDifficultyMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)
    _MAX_BONUSES_IN_VIEW = 12

    def __init__(self, resourceID, isReward):
        settings = ViewSettings(R.views.last_stand.mono.lobby.stage_reward_view())
        settings.model = StageRewardViewModel()
        super(StageRewardView, self).__init__(settings)
        self.__idGen = SequenceIDGenerator()
        self.__resourceID = resourceID
        self.__isReward = isReward
        self.__bonusCache = {}

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(StageRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.booster_tooltip():
            boosterName = event.getArgument('boosterName', '')
            return BoosterTooltipView(boosterName)
        return super(StageRewardView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(StageRewardView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(StageRewardView, self)._onLoading(*args, **kwargs)
        self.__fillViewModel()

    def _getEvents(self):
        return [(self.viewModel.onClose, self.__onClose)]

    def _initialize(self, *args, **kwargs):
        super(StageRewardView, self)._initialize()
        playSound(REWARD_WINDOW_ENTER)
        WWISE.WW_setState(RewardState.GROUP, RewardState.GENERAL_ON)

    def _finalize(self):
        playSound(REWARD_WINDOW_EXIT)
        WWISE.WW_setState(RewardState.GROUP, RewardState.GENERAL_OFF)
        super(StageRewardView, self)._finalize()

    def __onClose(self):
        self.destroyWindow()

    def __fillViewModel(self):
        with self.viewModel.transaction() as tx:
            resource = self.lsDifficultyMissionsCtrl.getMission(self.__resourceID) if self.__isReward else self.lsArtifactsCtrl.getArtefact(self.__resourceID)
            bonuses = []
            artefactNumber = -1
            if self.__isReward and resource:
                bonuses = resource.bonusRewards
            elif not self.__isReward and resource:
                artefactNumber = self.lsArtifactsCtrl.getIndex(resource.artefactID)
                bonuses = resource.bonusRewards
                tx.setIsLastArtefact(self.lsArtifactsCtrl.isFinalArtefact(resource))
            tx.setArtefactNumber(artefactNumber)
            tx.setIsQuestReward(self.__isReward)
            self.__bonusCache = fillRewards(bonuses, tx.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen)


class StageRewardWindow(LobbyNotificationWindow):

    def __init__(self, resourceID, isReward=False, parent=None):
        super(StageRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=StageRewardView(resourceID, isReward), parent=parent)
        self.__args = (resourceID, isReward)

    def isParamsEqual(self, *args):
        return self.__args == args
