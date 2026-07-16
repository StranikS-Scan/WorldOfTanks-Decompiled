# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/awards_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowFlags
from gui.challenges.challenges_decorators import createTooltipContentDecorator
from gui.challenges.challenges_award_manager import AwardsManager
from gui.challenges.challenges_bonuses_packers import getChallengesBonusPacker
from gui.challenges.sounds import CHALLENGE_AWARDS_SOUND_SPACE
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.challenges.awards_view_model import AwardsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui.server_events.events_dispatcher import showChallenges
from helpers import dependency
from skeletons.gui.challenges import IChallengesController
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData

class ChallengesAwardsView(ViewImpl):
    _COMMON_SOUND_SPACE = CHALLENGE_AWARDS_SOUND_SPACE
    __challenges = dependency.descriptor(IChallengesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.challenges.awards_view())
        settings.model = AwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ChallengesAwardsView, self).__init__(settings)
        self.__tooltipItems = {}
        self.__challenge = None
        self.__isCompleted = False
        return

    @property
    def viewModel(self):
        return super(ChallengesAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengesAwardsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(ChallengesAwardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def _onLoading(self, challenge, rewardsData, *args, **kwargs):
        super(ChallengesAwardsView, self)._onLoading(*args, **kwargs)
        self.__challenge = challenge
        challengeProgress = self.__challenges.getChallengeProgress(challenge.challengeID)
        self.__isCompleted = self.__challenge.allowedCompletions == challengeProgress['wins']
        with self.viewModel as model:
            model.setChallengeName(self.__challenge.name)
            model.setMainRewardType(self.__challenge.mainRewardType.value)
            model.setIsCompleted(self.__isCompleted)
            model.setIsAvailable(bool(self.__challenges.challengesAvailableForCompletions()))
            self.__setRewards(rewardsData, model)

    def _finalize(self):
        self.__tooltipItems.clear()
        self.__challenge = None
        super(ChallengesAwardsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onHangar, self.__onHangar), (self.viewModel.onChallenges, self.__onChallenges))

    def __onClose(self):
        self.destroyWindow()

    @args2params(int)
    def __onHangar(self, vehicleCD):
        selectVehicleInHangar(vehicleCD)

    def __onChallenges(self):
        challengeID = self.__challenge.challengeID if not self.__isCompleted else None
        showChallenges(challengeID)
        return

    def __setRewards(self, rewardsData, model):
        rewards = AwardsManager.composeVisibleBonuses(rewardsData, reverse=True)
        if not rewards:
            return
        packBonusModelAndTooltipData(rewards, model.getRewards(), self.__tooltipItems, getChallengesBonusPacker())


class ChallengesAwardsScreen(LobbyNotificationWindow):

    def __init__(self, challenge, rewards):
        super(ChallengesAwardsScreen, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChallengesAwardsView(challenge, rewards))
