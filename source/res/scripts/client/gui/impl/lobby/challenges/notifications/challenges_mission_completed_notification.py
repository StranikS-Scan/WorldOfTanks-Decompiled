# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/notifications/challenges_mission_completed_notification.py
from __future__ import absolute_import
from gui.challenges.challenges_award_manager import AwardsManager
from gui.challenges.challenges_bonuses_packers import getChallengesBonusPacker
from gui.challenges.challenges_decorators import createTooltipContentDecorator
from gui.impl.gen.view_models.views.lobby.challenges.notifications.challenges_mission_completed_model import ChallengesMissionCompletedModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.gf_notifications import NotificationBase
from gui.server_events.events_dispatcher import showChallenges

class ChallengesMissionCompletedNotification(NotificationBase):

    def __init__(self, resId, *args, **kwargs):
        super(ChallengesMissionCompletedNotification, self).__init__(resId, ChallengesMissionCompletedModel(), *args, **kwargs)
        self.__tooltipItems = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengesMissionCompletedNotification, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(ChallengesMissionCompletedNotification, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def _getEvents(self):
        events = super(ChallengesMissionCompletedNotification, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _update(self):
        data = self._getPayload()
        with self.viewModel as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setMissionID(data.get('missionID', ''))
            self.__setRewards(data.get('rewards', ''), tx)

    def __onClick(self):
        showChallenges()

    def __setRewards(self, rewardsData, model):
        rewards = AwardsManager.composeVisibleBonuses(rewardsData, reverse=True)
        if not rewards:
            return
        packBonusModelAndTooltipData(rewards, model.getRewards(), self.__tooltipItems, getChallengesBonusPacker())
