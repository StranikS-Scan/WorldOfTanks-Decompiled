# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/uilogging/story_mode/loggers.py
import typing
from gui.game_loading import loading as gameLoading
from helpers import dependency
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import Features, LogActions, LogWindows, LogButtons, LogBattleResultStats
from story_mode_common.story_mode_constants import EXTENSION_NAME
from uilogging.base.logger import MetricsLogger
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.types import ItemType, ItemStateType, InfoType
    from story_mode.gui.impl.lobby.consts import EntryPointStates

class BaseMetricsLogger(MetricsLogger):
    __slots__ = ('_item',)
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, item):
        feature = Features.ONBOARDING if self._storyModeCtrl.isOnboarding else Features.STORY_MODE
        super(BaseMetricsLogger, self).__init__(feature)
        self._item = item


class WindowLogger(BaseMetricsLogger):
    __slots__ = ('_isOpened',)

    def __init__(self, item):
        super(WindowLogger, self).__init__(item)
        self._isOpened = False

    def logOpen(self, state=None, info=None):
        self.log(action=LogActions.OPEN, item=self._item, itemState=state, info=info)
        self._isOpened = True

    def logClose(self, state=None):
        self.log(action=LogActions.CLOSE, item=self._item, itemState=state)
        self._isOpened = False

    def logButtonShown(self, button, once=False, state=None):
        if self._isOpened:
            if once:
                self.logOnce(action=LogActions.SHOW, item=button, parentScreen=self._item, itemState=state)
            else:
                self.log(action=LogActions.SHOW, item=button, parentScreen=self._item, itemState=state)

    def logClick(self, button, state=None):
        if self._isOpened:
            self.log(action=LogActions.CLICK, item=button, itemState=state, parentScreen=self._item)


class WindowBehindGameLoadingLogger(WindowLogger):
    __slots__ = ()

    @noexcept
    def logGameLoadingClose(self):
        if self._isOpened and gameLoading.getLoader().isLoading:
            self.log(action=LogActions.GAME_LOADING_CLOSE, item=self._item)


class MissionWindowLogger(WindowLogger):
    __slots__ = ()

    @noexcept
    def logOpen(self, missionId=None, info=None):
        super(MissionWindowLogger, self).logOpen(state=None if missionId is None else str(missionId), info=info)
        return


class PostBattleWindowLogger(MissionWindowLogger):
    __slots__ = ()

    def __init__(self):
        super(PostBattleWindowLogger, self).__init__(LogWindows.POST_BATTLE)

    @noexcept
    def logOpen(self, missionId=None, win=False):
        result = LogBattleResultStats.WIN if win else LogBattleResultStats.LOST
        super(PostBattleWindowLogger, self).logOpen(missionId=missionId, info=result)


class SelectMissionWindow(MissionWindowLogger):
    __slots__ = ()

    def __init__(self):
        super(SelectMissionWindow, self).__init__(LogWindows.MISSION_SELECTION)

    @noexcept
    def logMissionSelectClick(self, missionId):
        self.logClick(LogButtons.SELECT, state=str(missionId))

    @noexcept
    def logAutoSelect(self, missionId):
        if self._isOpened:
            self.log(LogActions.AUTO_SELECT, item=self._item, itemState=str(missionId))

    @noexcept
    def logTooltipShown(self, missionId):
        self.log(LogActions.TOOLTIP_SHOWN, item=self._item, itemState=str(missionId))

    @noexcept
    def logTabChanged(self, missionId):
        self.logClick(LogButtons.TAB_SECTION, state=str(missionId))


class SelectorCardLogger(BaseMetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(SelectorCardLogger, self).__init__(LogWindows.MODE_SELECTOR_CARD)

    def logSelfClick(self):
        self.log(action=LogActions.CLICK, item=self._item)

    def logInfoClick(self):
        self.log(action=LogActions.CLICK, item=LogButtons.INFO, parentScreen=self._item)


class BaseVideoLogger(WindowLogger):
    __slots__ = ()

    def logVideoStarted(self, missionId):
        if self._isOpened:
            self.log(LogActions.PLAY, item=self._item, itemState=str(missionId))


class IntroVideoLogger(BaseVideoLogger):
    __slots__ = ()

    def __init__(self):
        super(IntroVideoLogger, self).__init__(LogWindows.INTRO_VIDEO)


class OutroVideoLogger(BaseVideoLogger):
    __slots__ = ()

    def __init__(self):
        super(OutroVideoLogger, self).__init__(LogWindows.OUTRO_VIDEO)


class EntryPointLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(EntryPointLogger, self).__init__(EXTENSION_NAME)

    def logClick(self, state):
        self.log(LogActions.CLICK, LogWindows.ENTRY_POINT_EVENT, itemState=state.name.lower())


class NewbieEntryPointLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(NewbieEntryPointLogger, self).__init__(EXTENSION_NAME)

    def logClick(self, state):
        self.log(LogActions.CLICK, LogWindows.ENTRY_POINT, itemState=state.name.lower())


class NewbieAdvertisingViewLogger(WindowLogger):
    __slots__ = ()

    def __init__(self):
        super(NewbieAdvertisingViewLogger, self).__init__(LogWindows.NEWBIE_ADVERTISING)


class EventWelcomeViewLogger(WindowLogger):
    __slots__ = ()

    def __init__(self):
        super(EventWelcomeViewLogger, self).__init__(LogWindows.EVENT_WELCOME)


class TasksCompletedWarningLogger(WindowLogger):
    __slots__ = ()

    def __init__(self):
        super(TasksCompletedWarningLogger, self).__init__(LogWindows.COMPLETED_TASKS_WARNING)
