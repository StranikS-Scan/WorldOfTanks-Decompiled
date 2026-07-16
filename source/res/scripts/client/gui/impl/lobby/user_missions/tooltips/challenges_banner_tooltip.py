# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/challenges_banner_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.challenges.challenges_helpers import TIME_BEFORE_END_OF_EXPIRATION
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.tooltips.challenges_banner_tooltip_model import ChallengesBannerTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.events import ChallengeMissionUIDataPacker
from helpers import dependency
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.server_events import IEventsCache

class ChallengesBannerTooltip(ViewImpl):
    __challenges = dependency.descriptor(IChallengesController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.challenges_banner_tooltip())
        settings.model = ChallengesBannerTooltipModel()
        super(ChallengesBannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChallengesBannerTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__challenges.onChallengesSettingsChanged, self.__fillInfo), (self.__challenges.onActiveChallengeChanged, self.__fillInfo), (self.__challenges.onChallengesClientUpdated, self.__fillInfo))

    def _onLoading(self, *args, **kwargs):
        super(ChallengesBannerTooltip, self)._onLoading(*args, **kwargs)
        self.__fillInfo()

    def __fillInfo(self):
        with self.viewModel as model:
            activeChallenge = self.__challenges.getChallenge(self.__challenges.activeChallengeID)
            model.setTime(self.__getTimer(activeChallenge))
            model.setChallengeName('' if activeChallenge is None else activeChallenge.name)
            if activeChallenge is not None:
                progress = self.__challenges.getChallengeProgress(activeChallenge.challengeID)
                missions = progress['quests']
                remainingAttempts = progress['attempts']
                model.setTotalMissions(len(activeChallenge.questsIDs))
                model.setCompletedMissions(missions - 1)
                model.setRemainingAttempts(remainingAttempts if remainingAttempts else activeChallenge.attempts)
                questID = activeChallenge.questsIDs[missions - 1]
                quest = self.__eventsCache.getHiddenQuests(lambda q: q.getID() == questID, makeRelations=False).get(questID)
                if quest is not None:
                    packer = ChallengeMissionUIDataPacker(quest)
                    packer.pack(model.mission)
        return

    def __getTimer(self, challenge):
        availableChallenges = self.__challenges.challengesAvailableForCompletions() or self.__challenges.availableChallenges()
        rest = self.__challenges.getTimeToNearestChallengeEnd(availableChallenges)
        if challenge is not None:
            rest = challenge.expireTime
        return rest if rest <= TIME_BEFORE_END_OF_EXPIRATION else 0
