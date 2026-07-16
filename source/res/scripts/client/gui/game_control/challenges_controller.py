# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/challenges_controller.py
from __future__ import absolute_import
from adisp import adisp_process
from future.utils import viewvalues
from challenges_common import ChallengeTokenPrefixes, ChallengeTokenType, isChallengeToken, CHALLENGES_PDATA_KEY
from constants import Configs
from Event import Event, EventManager
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from gui.challenges.challenges_award_manager import AwardsManager
from gui.challenges.challenges_decorators import checkIsEnabled
from gui.challenges.challenges_helpers import TIME_BEFORE_END_OF_EXPIRATION
from gui.challenges.challenge_item import ChallengeItem
from gui.shared.gui_items.processors.challenges import ActivateChallengeProcessor, RestartChallengeProcessor, SurrenderChallengeProcessor
from gui.shared.money import Money
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.SystemMessages import pushMessagesFromResult
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.shared import IItemsCache

class ChallengesController(IChallengesController, Notifiable, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ChallengesController, self).__init__()
        self.__em = EventManager()
        self.__challenges = {}
        self.__challengesProgress = {}
        self.__activeChallengeID = 0
        self.onChallengesSettingsChanged = Event(self.__em)
        self.onActiveChallengeChanged = Event(self.__em)
        self.onChallengesClientUpdated = Event(self.__em)

    @property
    def systemConfig(self):
        return self.__lobbyContext.getServerSettings().challengesConfig

    @property
    def isEnabled(self):
        return self.systemConfig.isEnabled

    @property
    def activeChallengeID(self):
        return self.__activeChallengeID

    @property
    def challenges(self):
        if not self.__challenges:
            self.__challenges = {challengeItem.challengeID:challengeItem for challengeItem in self.iterChallenges()}
        return self.__challenges

    def init(self):
        AwardsManager.init()
        self.addNotificators(SimpleNotifier(self.getTimeToUpdateAvailableChallenges, self.__challengesStartUpdate), SimpleNotifier(self.getTimeToNearestChallengeEnd, self.__challengesFinishUpdate), SimpleNotifier(self.getTimeToRemindChallengeEnd, self.__challengesFinishUpdate))

    def onLobbyInited(self, _):
        self.startNotification()
        self._subscribe()
        self.__updateChallengesProgress(self.__itemsCache.items.tokens.getTokens())

    def onAccountBecomeNonPlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__challengesProgress.clear()
        self.__stop()

    def fini(self):
        self.clearNotification()
        AwardsManager.finalize()
        self.__em.clear()

    @checkIsEnabled()
    def getChallenge(self, challengeId):
        return self.challenges.get(challengeId) if challengeId in self.systemConfig.enabledChallengesIDs else None

    @checkIsEnabled(default=iter(()))
    def iterChallenges(self):
        for challengeId in self.systemConfig.enabledChallengesIDs:
            yield ChallengeItem(self.systemConfig.getChallengeConfig(challengeId))

    def availableChallenges(self):
        return [ ch for ch in viewvalues(self.challenges) if ch.isAvailable or ch.challengeID == self.__activeChallengeID ]

    def isChallengeCompleted(self, challenge):
        return self.getChallengeProgress(challenge.challengeID).get('wins') >= challenge.allowedCompletions

    def challengesAvailableForCompletions(self):
        return [ ch for ch in viewvalues(self.challenges) if not self.isChallengeCompleted(ch) and (ch.isAvailable or ch.challengeID == self.__activeChallengeID) ]

    def getSortedChallenges(self):
        return sorted(self.availableChallenges(), key=lambda ch: (ch.difficulty.value, ch.priority))

    def getNearestChallengeFinishTime(self, challenges):
        return min((challenge.finishTime + time_utils.ONE_MINUTE for challenge in challenges)) if challenges else 0

    def getTimeToNearestChallengeEnd(self, challenges=None):
        availableChallenges = challenges if challenges is not None else self.availableChallenges()
        return max(self.getNearestChallengeFinishTime(availableChallenges) - time_utils.getServerUTCTime(), 0)

    def getTimeToUpdateAvailableChallenges(self):
        currentTime = time_utils.getServerUTCTime()
        futureChallenges = [ ch for ch in viewvalues(self.challenges) if ch.startTime > currentTime ]
        nearestStart = min((ch.startTime for ch in futureChallenges)) if futureChallenges else 0
        return max(nearestStart - currentTime, 0)

    def getTimeToRemindChallengeEnd(self):
        return max(self.getTimeToNearestChallengeEnd() - TIME_BEFORE_END_OF_EXPIRATION, 0)

    def getSoonEndingChallenges(self):
        return sorted(self.availableChallenges(), key=lambda ch: (ch.finishTime, ch.difficulty.value, ch.priority))

    def getChallengeProgress(self, challengeID):
        return self.__challengesProgress.get(challengeID) or {}

    def isEnoughMoneyForRestart(self, challenge):
        restartPrice = Money(**challenge.restartPrice)
        return not self.__itemsCache.items.stats.money.getShortage(restartPrice).isDefined()

    @adisp_process
    def activateChallenge(self, challengeID):
        result = yield ActivateChallengeProcessor(challengeID).request()
        pushMessagesFromResult(result)

    @adisp_process
    def restartChallenge(self, challengeID, isFree):
        result = yield RestartChallengeProcessor(challengeID, isFree).request()
        pushMessagesFromResult(result)

    @adisp_process
    def surrenderChallenge(self, challengeID):
        result = yield SurrenderChallengeProcessor(challengeID).request()
        pushMessagesFromResult(result)

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensUpdated), (CHALLENGES_PDATA_KEY, self.__onChallengesClientUpdated))

    def __stop(self):
        self.stopNotification()
        self._unsubscribe()
        self.__activeChallengeID = 0
        self.__challenges.clear()

    @serverSettingsChangeListener(Configs.CHALLENGES_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__challenges = {challengeItem.challengeID:challengeItem for challengeItem in self.iterChallenges()}
        self.startNotification()
        self.__updateChallengesProgress(self.__itemsCache.items.tokens.getTokens())
        self.onChallengesSettingsChanged()

    def __onTokensUpdated(self, diff):
        if any((token.startswith(ChallengeTokenPrefixes.ACTIVE) for token in diff)):
            self.__updateChallengesProgress(diff)
            self.onActiveChallengeChanged()
            return
        token = findFirst(isChallengeToken, diff)
        if token:
            challengeID = int(token.split(':')[-1])
            self.__updateTokensInfo(challengeID, diff)
            self.onChallengesClientUpdated()

    def __onChallengesClientUpdated(self, _):
        self.onChallengesClientUpdated()

    def __challengesStartUpdate(self):
        self.__updateChallengesProgress(self.__itemsCache.items.tokens.getTokens())
        self.onChallengesSettingsChanged()

    def __challengesFinishUpdate(self):
        self.onChallengesSettingsChanged()

    def __updateChallengesProgress(self, tokensData):
        progress = {}
        if self.__activeChallengeID and self.__activeChallengeID not in self.challenges:
            self.__activeChallengeID = 0
        for challenge in viewvalues(self.challenges):
            activeToken = challenge.getTokenID(ChallengeTokenType.ACTIVE)
            if activeToken in tokensData:
                self.__activeChallengeID = 0 if not self.__getCount(activeToken, tokensData) else challenge.challengeID
            progress[challenge.challengeID] = self.__updateChallengeData(challenge, self.__itemsCache.items.tokens.getTokens())

        self.__challengesProgress = progress

    def __updateChallengeData(self, challenge, data):
        result = {}
        result['attempts'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.ATTEMPT), data)
        result['quests'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.QUEST), data)
        result['wins'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.WIN), data)
        return result

    def __getCount(self, tokenKey, tokens):
        _, count = tokens.get(tokenKey) or (0, 0)
        return count

    def __updateTokensInfo(self, challengeID, diff):
        progress = self.__challengesProgress.get(challengeID) or {}
        challenge = self.getChallenge(challengeID)
        if challenge.getTokenID(ChallengeTokenType.ATTEMPT) in diff:
            progress['attempts'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.ATTEMPT), diff)
        if challenge.getTokenID(ChallengeTokenType.QUEST) in diff:
            progress['quests'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.QUEST), diff)
        if challenge.getTokenID(ChallengeTokenType.WIN) in diff:
            progress['wins'] = self.__getCount(challenge.getTokenID(ChallengeTokenType.WIN), diff)
