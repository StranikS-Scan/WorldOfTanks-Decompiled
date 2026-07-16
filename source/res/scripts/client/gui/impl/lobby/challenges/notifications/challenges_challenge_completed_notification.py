# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/notifications/challenges_challenge_completed_notification.py
from __future__ import absolute_import
from gui.challenges.challenges_award_manager import AwardsManager
from gui.challenges.challenges_bonuses_packers import getChallengesBonusPacker
from gui.challenges.challenges_decorators import createTooltipContentDecorator
from gui.impl.gen.view_models.views.lobby.challenges.notifications.challenges_challenge_completed_model import ChallengesChallengeCompletedModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.gf_notifications import NotificationBase
from gui.server_events.events_dispatcher import showChallenges
from helpers import dependency
from skeletons.gui.challenges import IChallengesController

class ChallengesChallengeCompletedNotification(NotificationBase):
    __challenges = dependency.descriptor(IChallengesController)

    def __init__(self, resId, *args, **kwargs):
        super(ChallengesChallengeCompletedNotification, self).__init__(resId, ChallengesChallengeCompletedModel(), *args, **kwargs)
        self.__tooltipItems = {}
        self.__challenge = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengesChallengeCompletedNotification, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(ChallengesChallengeCompletedNotification, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def _getEvents(self):
        events = super(ChallengesChallengeCompletedNotification, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),
         (self.__challenges.onChallengesSettingsChanged, self.__onChallengesChanged),
         (self.__challenges.onActiveChallengeChanged, self.__onChallengesChanged),
         (self.__challenges.onChallengesClientUpdated, self.__onChallengesChanged))

    def _update(self):
        data = self._getPayload()
        self.__challenge = data.get('challenge', None)
        with self.viewModel as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setChallengeName(self.__challenge.name)
            tx.setAnyMissionsLeft(self.__challenges.isChallengeCompleted(self.__challenge))
            self.__setRewards(data.get('rewards', ''), tx)
        return

    def __onClick(self):
        if not self.__challenges.availableChallenges():
            self.destroyWindow()
            return
        else:
            challengeID = self.__challenge.challengeID if not self.__challenges.isChallengeCompleted(self.__challenge) else None
            showChallenges(challengeID=challengeID)
            return

    def __setRewards(self, rewardsData, model):
        rewards = AwardsManager.composeVisibleBonuses(rewardsData, reverse=True)
        if not rewards:
            return
        packBonusModelAndTooltipData(rewards, model.getRewards(), self.__tooltipItems, getChallengesBonusPacker())

    def __onChallengesChanged(self):
        self.viewModel.setAnyMissionsLeft(self.__challenges.isChallengeCompleted(self.__challenge))
