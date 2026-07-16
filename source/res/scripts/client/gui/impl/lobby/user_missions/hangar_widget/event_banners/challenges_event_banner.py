# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/challenges_event_banner.py
from __future__ import absolute_import
from account_helpers.AccountSettings import ChallengesMissions
from challenges_common import ChallengeTokenType
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.challenges.challenges_helpers import TIME_BEFORE_END_OF_EXPIRATION, getSettings, setSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.impl.lobby.user_missions.tooltips.challenges_banner_tooltip import ChallengesBannerTooltip
from gui.server_events.events_dispatcher import showChallenges
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(challenges=IChallengesController, itemsCache=IItemsCache)
def isChallengesBannerAvailable(challenges=None, itemsCache=None):
    notCompletedChallenges = [ ch for ch in challenges.availableChallenges() if not itemsCache.items.tokens.getTokenCount(ch.getTokenID(ChallengeTokenType.WIN)) >= ch.allowedCompletions ]
    return challenges.isEnabled and bool(notCompletedChallenges)


class ChallengesEventBanner(BaseEventBanner):
    NAME = HANGAR_ALIASES.CHALLENGES_EVENT_BANNER
    __eventsService = dependency.descriptor(IEventsService)
    __challenges = dependency.descriptor(IChallengesController)

    def __init__(self):
        super(ChallengesEventBanner, self).__init__()
        self.__state = EventBannerState.IN_PROGRESS
        self.__playAppearAnim = False

    @property
    def bannerState(self):
        return self.__state

    @property
    def borderColor(self):
        pass

    @property
    def inProgressDescription(self):
        description = R.strings.hangar_event_banners.event.ChallengesEventBanner.inProgress.description
        return backport.text(description.activeChallenge()) if self.__challenges.activeChallengeID else backport.text(description())

    @property
    def eventEndDate(self):
        activeChallengeID = self.__challenges.activeChallengeID
        return self.__challenges.getChallenge(activeChallengeID).finishTime + time_utils.ONE_MINUTE if activeChallengeID else self.__challenges.getNearestChallengeFinishTime(self.__challenges.challengesAvailableForCompletions())

    @property
    def showTimerBeforeEventEnd(self):
        return TIME_BEFORE_END_OF_EXPIRATION

    @property
    def timerValue(self):
        return self.__challenges.getChallenge(self.__challenges.activeChallengeID).expireTime if self.__challenges.activeChallengeID else self.__challenges.getTimeToNearestChallengeEnd(self.__challenges.challengesAvailableForCompletions())

    @property
    def playAppearAnim(self):
        return self.__playAppearAnim

    def onAppearAnimationPlayed(self):
        setSettings(ChallengesMissions.CHALLENGES_BUNDLE_ANIMATION_SHOWN, self.__playAppearAnim)

    def createToolTipContent(self, event):
        return ChallengesBannerTooltip()

    def prepare(self):
        self.__state = self.__getState()
        self.__playAppearAnim = not getSettings(ChallengesMissions.CHALLENGES_BUNDLE_ANIMATION_SHOWN, False)

    def onClick(self):
        if self.__challenges.isEnabled:
            challengeID = None
            if 0 < self.timerValue <= self.showTimerBeforeEventEnd:
                challenge = findFirst(lambda c: not self.__challenges.isChallengeCompleted(c), self.__challenges.getSoonEndingChallenges())
                challengeID = challenge.challengeID if challenge is not None else challengeID
            showChallenges(challengeID=self.__challenges.activeChallengeID if self.__challenges.activeChallengeID else challengeID)
        return

    def onAppear(self):
        if self._isVisible:
            return
        super(ChallengesEventBanner, self).onAppear()
        self.__challenges.onChallengesSettingsChanged += self.__onUpdate
        self.__challenges.onActiveChallengeChanged += self.__onUpdate
        self.__challenges.onChallengesClientUpdated += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(ChallengesEventBanner, self).onDisappear()
        self.__challenges.onChallengesSettingsChanged -= self.__onUpdate
        self.__challenges.onActiveChallengeChanged -= self.__onUpdate
        self.__challenges.onChallengesClientUpdated -= self.__onUpdate

    def __onUpdate(self, *_):
        if isChallengesBannerAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()

    def __getState(self):
        if not self.__challenges.isEnabled:
            return EventBannerState.INACTIVE
        return EventBannerState.INTRO if not getSettings(ChallengesMissions.CHALLENGES_BUNDLE_SHOWN, False) else EventBannerState.IN_PROGRESS
