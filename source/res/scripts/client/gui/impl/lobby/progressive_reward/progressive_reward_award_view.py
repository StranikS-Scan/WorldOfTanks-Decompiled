# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/progressive_reward/progressive_reward_award_view.py
import logging
from frameworks.wulf import ViewFlags
from frameworks.wulf import WindowFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getRewardRendererModelPresenter, getProgressiveRewardBonuses, BLUEPRINTS_CONGRAT_TYPES, fillStepsModel
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.progressive_reward.progressive_reward_award_model import ProgressiveRewardAwardModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.lobby.progressive_reward.progressive_award_sounds import setSoundState, ProgressiveRewardSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.event_dispatcher import showBlueprintView
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class ProgressiveRewardAwardView(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__items', '__rewards', '__currentStep')

    def __init__(self, contentResId, *args, **kwargs):
        super(ProgressiveRewardAwardView, self).__init__(contentResId, ViewFlags.VIEW, ProgressiveRewardAwardModel, *args, **kwargs)
        self.__items = {}
        self.__rewards = {}
        self.__currentStep = 0
        g_techTreeDP.load()

    @property
    def viewModel(self):
        return super(ProgressiveRewardAwardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(ProgressiveRewardAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _initialize(self, rewards, currentStep):
        super(ProgressiveRewardAwardView, self)._initialize()
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onCloseAction += self.__onWindowClose
        self.viewModel.onSpecialActionBtnClick += self.__onSpecialActionButtonClick
        g_clientUpdateManager.addCallbacks({'blueprints': self.__update,
         'serverSettings.blueprints_config': self.__update,
         'serverSettings.progressive_reward_config': self.__update})
        self.__rewards = rewards
        self.__currentStep = currentStep
        self.__update()
        setSoundState(groupName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_AWARD_GROUP, stateName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_AWARD_ENTER)

    def _finalize(self):
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.onSpecialActionBtnClick -= self.__onSpecialActionButtonClick
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__items.clear()
        self.__rewards.clear()
        super(ProgressiveRewardAwardView, self)._finalize()

    def __update(self, _=None):
        self.__setSteps(self.__currentStep)
        self.__setRewards(self.__rewards)

    def __onWindowClose(self, _=None):
        if self.viewModel.getHardReset():
            self.__onDestroy()
        else:
            self.viewModel.setFadeOut(True)

    def __onDestroy(self, _=None):
        setSoundState(groupName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_AWARD_GROUP, stateName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_AWARD_EXIT)
        self.destroyWindow()

    def __setSteps(self, currentStep):
        progressive = self._eventsCache.getProgressiveReward()
        if progressive is None:
            _logger.warning('Progressive config is missing on server!')
            return
        else:
            with self.viewModel.transaction() as tx:
                steps = tx.getSteps()
                steps.clear()
                fillStepsModel(currentStep, progressive.probability, progressive.maxSteps, True, steps)
                steps.invalidate()
                tx.setStepIdx(currentStep)
                tx.setInitialCongratsType(LootCongratsTypes.INIT_CONGRAT_TYPE_PROGRESSIVE_REWARDS)
            return

    def __setRewards(self, rewards):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.getRewards()
            rewardsList.clear()
            bonuses, specialRewardType = getProgressiveRewardBonuses(rewards)
            for index, reward in enumerate(bonuses):
                formatter = getRewardRendererModelPresenter(reward)
                rewardRender = formatter.getModel(reward, index)
                rewardsList.addViewModel(rewardRender)
                compensationReason = reward.get('compensationReason', None)
                ttTarget = compensationReason if compensationReason is not None else reward
                self.__items[index] = TooltipData(tooltip=ttTarget.get('tooltip', None), isSpecial=ttTarget.get('isSpecial', False), specialAlias=ttTarget.get('specialAlias', ''), specialArgs=ttTarget.get('specialArgs', None))

            rewardsList.invalidate()
            tx.setSpecialRewardType(specialRewardType)
        return

    def __onSpecialActionButtonClick(self, responseDict):
        congratsType = responseDict.get('congratsType')
        if congratsType in BLUEPRINTS_CONGRAT_TYPES:
            vehicleCD = _getVehicleCD(responseDict.get('congratsSourceId'))
            if vehicleCD is not None:
                self.__onWindowClose()
                showBlueprintView(vehicleCD)
        return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__items:
            return self.__items[tooltipId]
        else:
            if tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
                vehicleCD = _getVehicleCD(event.getArgument('vehicleCD'))
                if vehicleCD is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(vehicleCD, True))
            elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
                vehicleCD = _getVehicleCD(event.getArgument('vehicleCD'))
                if vehicleCD is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD])
            return


class ProgressiveRewardAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, rewards, currentStep):
        super(ProgressiveRewardAwardWindow, self).__init__(content=ProgressiveRewardAwardView(R.views.progressiveRewardAward(), rewards, currentStep), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return


def _getVehicleCD(value):
    try:
        vehicleCD = int(value)
    except ValueError:
        _logger.warning('Wrong vehicle compact descriptor: %s!', value)
        return None

    return vehicleCD
    return None
