# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/session_progress_rewards_notification.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.session_progress_rewards_notification_view_model import SessionProgressRewardsNotificationViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.server_events.events_dispatcher import showDailyQuests
from gui.session_progress_rewards.session_progress_rewards_bonus_packers import getSessionProgressRewardsBonusPacker
from helpers import dependency
from skeletons.gui.game_control import ISessionProgressRewardsController

class SessionProgressRewardsNotification(NotificationBase):
    __sessionProgressRewardsController = dependency.descriptor(ISessionProgressRewardsController)
    __slots__ = ('__tooltipData',)

    def __init__(self, resId, *args, **kwargs):
        super(SessionProgressRewardsNotification, self).__init__(resId, SessionProgressRewardsNotificationViewModel(), *args, **kwargs)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(SessionProgressRewardsNotification, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SessionProgressRewardsNotification, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            tooltipIds = [ tooltipId for tooltipId in event.getArgument('tooltipIds', '').split(',') if tooltipId ]
            if not tooltipIds:
                return None
            bonusesByTooltipId = {bonus.getTooltipId():bonus for bonus in self.viewModel.getRewards()}
            bonuses = [ bonusesByTooltipId[tooltipId] for tooltipId in tooltipIds if tooltipId in bonusesByTooltipId ]
            if bonuses:
                return AdditionalRewardsTooltip(bonuses)
            return None
        else:
            return super(SessionProgressRewardsNotification, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(SessionProgressRewardsNotification, self)._onLoading(*args, **kwargs)
        linkageData = self.linkageData.toDict()
        step = linkageData.get('step', 0)
        rewards = self.__sessionProgressRewardsController.getRewardsByStep(step)
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)
            model.setStep(step + 1)
            model.setShowButton(linkageData.get('showButton', False))
            model.setIsDisabled(not self._canNavigate())
            self.__tooltipData.clear()
            rewardsList = model.getRewards()
            rewardsList.clear()
            packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getSessionProgressRewardsBonusPacker())
            rewardsList.invalidate()

    def _getEvents(self):
        return ((self.viewModel.goToProgression, self.__goToProgression),)

    @staticmethod
    def __goToProgression():
        showDailyQuests(DailyTabs.SERIAL)
