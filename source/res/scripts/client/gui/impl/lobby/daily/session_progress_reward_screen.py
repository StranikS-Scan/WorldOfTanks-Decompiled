# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/session_progress_reward_screen.py
from copy import copy
import AnimationSequence
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.session_progress_reward_screen_model import SessionProgressRewardScreenModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.daily.tooltips.session_progress_rewards_compensation_tooltip import SessionProgressRewardsCompensationTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses
from gui.session_progress_rewards.session_progress_rewards_bonus_packers import getSessionProgressRewardsBonusPacker
from gui.shared.bonuses_sorter import bonusesSortKeyFunc
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import dependency, isPlayerAccount
from shared_utils import findFirst
from skeletons.gui.shared.utils import IHangarSpace
_MAX_REWARDS = 3

class SessionProgressRewardScreen(ViewImpl):
    __slots__ = ('__tooltipData', '__rawBonuses', '__mainVehicleCd', '__isWorldDrawOptimizationActive', '__isWorldDrawDisabled')
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, layoutID, bonuses):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SessionProgressRewardScreenModel()
        self.__tooltipData = {}
        self.__rawBonuses = copy(bonuses)
        self.__mainVehicleCd = None
        self.__isWorldDrawOptimizationActive = False
        self.__isWorldDrawDisabled = False
        super(SessionProgressRewardScreen, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(SessionProgressRewardScreen, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SessionProgressRewardScreen, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.daily.tooltips.SessionProgressRewardsCompensationTooltip():
            tooltipData = self.getTooltipData(event)
            if tooltipData:
                return SessionProgressRewardsCompensationTooltip(*tooltipData.specialArgs)
        return super(SessionProgressRewardScreen, self).createToolTipContent(event=event, contentID=contentID)

    def getTooltipData(self, event):
        index = event.getArgument('tooltipId')
        return self.__tooltipData.get(index, None)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onShowInHangar, self.__onShowInHangar), (self.__hangarSpace.onSpaceCreate, self.__onHangarSpaceCreate))

    def _onLoading(self, *args, **kwargs):
        super(SessionProgressRewardScreen, self)._onLoading(*args, **kwargs)
        rewards = []
        for bonusType, bonusValue in self.__rawBonuses.items():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            rewards.extend(bonus)

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        rewards = rewards[:_MAX_REWARDS]
        vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', rewards)
        if vehicleBonus:
            vehicles = vehicleBonus.getVehicles()
            if vehicles:
                vehicle, _ = vehicles[0]
                self.__mainVehicleCd = vehicle.intCD
        if len(rewards) == _MAX_REWARDS:
            rewards[0], rewards[1] = rewards[1], rewards[0]
        with self.viewModel.transaction() as model:
            rewardsList = model.getRewards()
            rewardsList.clear()
            packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getSessionProgressRewardsBonusPacker())
            rewardsList.invalidate()
        self.__isWorldDrawOptimizationActive = True
        self.__disableWorldDraw()

    def _onLoaded(self, *args, **kwargs):
        super(SessionProgressRewardScreen, self)._onLoaded(*args, **kwargs)
        if self.__isWorldDrawOptimizationActive:
            self.__disableWorldDraw()

    def _finalize(self):
        self.__isWorldDrawOptimizationActive = False
        self.__enableWorldDraw()
        super(SessionProgressRewardScreen, self)._finalize()

    def __onClose(self):
        self.destroyWindow()

    def __onShowInHangar(self):
        if self.__mainVehicleCd is not None:
            self.destroyWindow()
            selectVehicleInHangar(self.__mainVehicleCd)
        return

    def __onHangarSpaceCreate(self):
        if self.__isWorldDrawOptimizationActive:
            self.__disableWorldDraw()

    def __canToggleWorldDraw(self):
        return isPlayerAccount() and self.__hangarSpace.spaceInited

    def __disableWorldDraw(self):
        if not self.__canToggleWorldDraw():
            return
        BigWorld.worldDrawEnabled(False)
        AnimationSequence.setEnableAnimationSequenceUpdate(False)
        self.__isWorldDrawDisabled = True

    def __enableWorldDraw(self):
        if not self.__isWorldDrawDisabled:
            return
        self.__isWorldDrawDisabled = False
        AnimationSequence.setEnableAnimationSequenceUpdate(True)
        if self.__canToggleWorldDraw():
            BigWorld.worldDrawEnabled(True)


class SessionProgressRewardScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses=None, parent=None):
        super(SessionProgressRewardScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SessionProgressRewardScreen(R.views.lobby.daily.SessionProgressRewardScreen(), bonuses or {}), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
