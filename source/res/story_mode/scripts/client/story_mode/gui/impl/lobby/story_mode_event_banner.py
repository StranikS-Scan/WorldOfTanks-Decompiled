# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/story_mode_event_banner.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from helpers import dependency
from helpers.time_utils import getTimestampFromUTC, getServerUTCTime, ONE_DAY, ONE_MINUTE
from story_mode.account_settings import setEventEntryPointShown, getEventEntryPointShown, getEventVisited, getNewbieEntryPointAnimationSeenId, setNewbieEntryPointAnimationSeenId
from story_mode.gui.impl.lobby.event_banner_tooltip import EventBannerTooltip
from story_mode.gui.impl.lobby.newbie_banner_tooltip import NewbieBannerTooltip
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import EntryPointLogger, NewbieEntryPointLogger
from story_mode_common.configs.story_mode_settings import settingsSchema
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent

class StoryModeNewbieBanner(BaseEventBanner):
    NAME = 'StoryModeNewbieEntryPoint'
    _controller = dependency.descriptor(IStoryModeController)

    def __init__(self):
        super(StoryModeNewbieBanner, self).__init__()
        self._uiLogger = NewbieEntryPointLogger()

    @property
    def isMode(self):
        return True

    @property
    def borderColor(self):
        pass

    @property
    def bannerState(self):
        return EventBannerState.INTRO if self._controller.isNewNeededForNewbies() else EventBannerState.IN_PROGRESS

    @property
    def playAppearAnim(self):
        newMissionIdForNewbies = self._controller.newMissionIdForNewbies
        if getNewbieEntryPointAnimationSeenId() < newMissionIdForNewbies:
            setNewbieEntryPointAnimationSeenId(newMissionIdForNewbies)
            return True
        return False

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StoryModeNewbieEntryPoint.introDescription())

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StoryModeNewbieEntryPoint.inProgressDescription())

    def createToolTipContent(self, event):
        return NewbieBannerTooltip()

    def onClick(self):
        self._uiLogger.logClick()
        self._controller.switchPrb()


class StoryModeEventBanner(BaseEventBanner):
    NAME = 'StoryModeEventEntryPoint'
    _controller = dependency.descriptor(IStoryModeController)

    def __init__(self):
        super(StoryModeEventBanner, self).__init__()
        self._uiLogger = EntryPointLogger()

    @property
    def isMode(self):
        return True

    @property
    def borderColor(self):
        pass

    @property
    def bannerState(self):
        return EventBannerState.IN_PROGRESS if getEventVisited() else EventBannerState.INTRO

    @property
    def timerValue(self):
        settings = settingsSchema.getModel()
        if settings is not None:
            timeLeft = int(getTimestampFromUTC(settings.entryPoint.eventEndAt.timetuple()) - getServerUTCTime())
            return max(timeLeft, ONE_MINUTE)
        else:
            return 0

    @property
    def showTimerBeforeEventEnd(self):
        return ONE_DAY

    @property
    def playAppearAnim(self):
        if not getEventEntryPointShown():
            setEventEntryPointShown()
            return True
        return False

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StoryModeEventEntryPoint.introDescription())

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StoryModeEventEntryPoint.inProgressDescription())

    def createToolTipContent(self, event):
        return EventBannerTooltip()

    def onClick(self):
        self._uiLogger.logClick()
        self._controller.switchPrb()

    def onAppear(self):
        super(StoryModeEventBanner, self).onAppear()
        self._controller.onSettingsUpdated += self._onSettingsUpdated

    def onDisappear(self):
        self._controller.onSettingsUpdated -= self._onSettingsUpdated
        super(StoryModeEventBanner, self).onDisappear()

    def _onSettingsUpdated(self):
        EventBannersContainer().onBannerUpdate(self)
