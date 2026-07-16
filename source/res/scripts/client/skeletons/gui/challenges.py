# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/challenges.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Optional, Iterator, List, Dict, Union
    from Event import Event
    from gui.challenges.challenge_item import ChallengeItem
    from challenges_common import ChallengesConfig

class IChallengesController(IGameController):
    onChallengesSettingsChanged = None
    onActiveChallengeChanged = None
    onChallengesClientUpdated = None

    @property
    def systemConfig(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def activeChallengeID(self):
        raise NotImplementedError

    def getChallenge(self, challengeId):
        raise NotImplementedError

    def iterChallenges(self):
        raise NotImplementedError

    def availableChallenges(self):
        raise NotImplementedError

    def isChallengeCompleted(self, challenge):
        raise NotImplementedError

    def challengesAvailableForCompletions(self):
        raise NotImplementedError

    def getSortedChallenges(self):
        raise NotImplementedError

    def getNearestChallengeFinishTime(self, challenges):
        raise NotImplementedError

    def getTimeToNearestChallengeEnd(self, challenges=None):
        raise NotImplementedError

    def getTimeToUpdateAvailableChallenges(self):
        raise NotImplementedError

    def getSoonEndingChallenges(self):
        raise NotImplementedError

    def getChallengeProgress(self, challengeID):
        raise NotImplementedError

    def isEnoughMoneyForRestart(self, challenge):
        raise NotImplementedError

    def activateChallenge(self, challengeID):
        raise NotImplementedError

    def restartChallenge(self, challengeID, isFree):
        raise NotImplementedError

    def surrenderChallenge(self, challengeID):
        raise NotImplementedError
