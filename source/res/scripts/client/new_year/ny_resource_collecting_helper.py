# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_resource_collecting_helper.py
import logging
from functools import partial
import typing
from enum import Enum
import BigWorld
from BWUtil import AsyncReturn
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_LOGGED_SERVER_DAY
from constants import SECONDS_IN_DAY
from Event import EventManager, Event
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from new_year.ny_constants import NYObjects, SyncDataKeys
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import IFriendServiceController
from skeletons.account_helpers.settings_core import ISettingsCore
from wg_async import AsyncScope, AsyncEvent, wg_async, wg_await, BrokenPromiseError
if typing.TYPE_CHECKING:
    from typing import Optional
    from ny_common.ResourceCollectingConfig import ResourceCollectingConfig, CollectingDescriptor
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYResourceCollectingConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearResourceCollectingConfig()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCollectingCooldownTime(collectingDescr=None, itemsCache=None):
    timeTill = -1
    lastCollectingDay, lastCollectingTime, __ = itemsCache.items.festivity.getResourceCollecting()
    if collectingDescr is None:
        currentCollectingDescr = getCollectingDescr()
    else:
        currentCollectingDescr = collectingDescr
    if currentCollectingDescr is None:
        return timeTill
    else:
        todayDay = time_utils.getServerGameDay() if BigWorld.player() else 0
        if lastCollectingTime is None or todayDay > lastCollectingDay:
            return 0
        cooldown = currentCollectingDescr.getCollectingCooldown()
        endOfDayCollectTime = time_utils.getDayTimeLeft() + time_utils.ONE_MINUTE
        if isinstance(cooldown, int):
            timeTill = min(endOfDayCollectTime, max(lastCollectingTime + cooldown - time_utils.getServerUTCTime(), 0))
        elif isinstance(cooldown, str) and cooldown == 'endOfGameDay':
            timeTill = endOfDayCollectTime
        return timeTill


@dependency.replace_none_kwargs(itemsCache=IItemsCache, friendService=IFriendServiceController)
def isCollectingAvailable(itemsCache=None, friendService=None, forceFriend=None):
    return getCollectingCooldownTime(itemsCache=itemsCache) == 0 if forceFriend is None and not friendService.isInFriendHangar or forceFriend is False else friendService.getFriendCollectingCooldownTime() == 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyCtx=ILobbyContext)
def isExtraCollectingAvailable(collectingDescr=None, itemsCache=None, lobbyCtx=None):
    return getSkippedDays(collectingDescr=collectingDescr, itemsCache=itemsCache, lobbyCtx=lobbyCtx) > 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyCtx=ILobbyContext)
def getSkippedDays(collectingDescr=None, itemsCache=None, lobbyCtx=None):
    lastCollectingDay, _, __ = itemsCache.items.festivity.getResourceCollecting()
    if lastCollectingDay is None:
        lastCollectingDay = (lobbyCtx.getServerSettings().getNewYearGeneralConfig().getEventStartTime() - time_utils.getStartOfNewGameDayOffset()) / SECONDS_IN_DAY - 1
    todayDay = time_utils.getServerGameDay()
    if collectingDescr is None:
        collectingDescr = getCollectingDescr()
    return collectingDescr.getSkippedDaysAmount(lastCollectingDay, todayDay)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, friendService=IFriendServiceController)
def getAvgResourcesByCollecting(forceFriend=None, itemsCache=None, friendService=None, forceExtraCollect=None):
    if forceFriend is None and friendService.isInFriendHangar or forceFriend:
        resources = getNYResourceCollectingConfig().getFriendResources()
    else:
        currentCollectingDescr = getNextCollectingDescr(itemsCache=itemsCache)
        if currentCollectingDescr is None:
            return 0
        if forceExtraCollect is None:
            forceExtraCollect = isExtraCollectingAvailable()
        resources = currentCollectingDescr.getResources(forceExtraCollect)
    return 0 if not resources else int(round(sum(resources.values()) / len(resources)))


def getPossibleResourcesByCollectingFromFriend():
    return sum(getNYResourceCollectingConfig().getFriendResources().itervalues())


def getResourceCollectings(resourceType, isExtraCollect=None, config=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    collectingDescr = config.getCollectingDescriptorByIndex(0)
    if collectingDescr is None:
        return 0
    else:
        if isExtraCollect is None:
            isExtraCollect = isExtraCollectingAvailable()
        resources = collectingDescr.getResources(isExtraCollect)
        return 0 if not resources else resources.get(resourceType, 0)


def getCollectingDescr(config=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    return config.getNextCollectingDescriptor(None)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getNextCollectingDescr(config=None, itemsCache=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    _, __, activeIdx = itemsCache.items.festivity.getResourceCollecting()
    return config.getNextCollectingDescriptor(activeIdx)


def getFirstCollectingDescr(config=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    return config.getNextCollectingDescriptor(None)


def getFirstCollectingCooldownTime():
    collectingDescr = getFirstCollectingDescr()
    if collectingDescr is None:
        return 0
    else:
        cooldown = collectingDescr.getCollectingCooldown()
        if isinstance(cooldown, str) and cooldown == 'endOfGameDay':
            cooldown = time_utils.getDayTimeLeft()
        return cooldown


class AnimStoppingReasons(CONST_CONTAINER):
    CLEAR = 1
    CHANGE_OBJECT = 2


class ResourceCollectingHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __friendService = dependency.descriptor(IFriendServiceController)
    __RESOURCE_ORDER = (Resource.IRON,
     Resource.EMERALD,
     Resource.CRYSTAL,
     Resource.AMBER)
    __VFX_TRIGGER_TEMPLATE = 'ny_craft_state_{}_collected'

    class CollectingStates(Enum):
        COLLECTING_AVAILABLE = 1
        DEFAULT = 3

    def __init__(self):
        self.__eventManager = EventManager()
        self.onCollectingUpdateLock = Event(self.__eventManager)
        self.onCollectingUpdateResource = Event(self.__eventManager)
        self.onStartCollectingAnim = Event(self.__eventManager)
        self.onSwitchCollectingState = Event(self.__eventManager)
        self.onStartCollectingAvailableAnim = Event(self.__eventManager)
        self.onCancelCollectingAnim = Event(self.__eventManager)
        self.onResources3DStateUpdate = Event(self.__eventManager)
        self.__resourceMarkers = {}
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = None
        self.__isCollectingAnimPlaying = False
        self.__isResourcesCurrentObj = False
        self.__menuResourcesLocked = False
        self.__currentState = self.CollectingStates.DEFAULT
        self.__callbackDelayer = CallbackDelayer()
        return

    def onLobbyInited(self):
        self.__event.clear()
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        self.__friendService.onFriendHangarEnter += self.__onFriendHangarEnter
        self.__friendService.onFriendHangarExit += self.__onFriendHangarExit
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreate
        g_eventBus.addListener(NyResourcesEvent.RESOURCE_COLLECTED, self.__onResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(NyResourcesEvent.FRIEND_RESOURCE_COLLECTED, self.__onFriendResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_playerEvents.onClientUpdated += self.__onClientUpdated

    def clear(self):
        self.__callbackDelayer.clearCallbacks()
        self.__eventManager.clear()
        if self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CLEAR)
        self.__isCollectingAnimPlaying = False
        self.__isResourcesCurrentObj = False
        self.__menuResourcesLocked = False
        self.__currentState = self.CollectingStates.DEFAULT
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        self.__friendService.onFriendHangarEnter -= self.__onFriendHangarEnter
        self.__friendService.onFriendHangarExit -= self.__onFriendHangarExit
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        g_eventBus.removeListener(NyResourcesEvent.RESOURCE_COLLECTED, self.__onResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(NyResourcesEvent.FRIEND_RESOURCE_COLLECTED, self.__onFriendResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_playerEvents.onClientUpdated -= self.__onClientUpdated

    def getInitial3DState(self):
        return 'ny_craft_state_full' if isCollectingAvailable() else 'ny_craft_state_empty'

    def setIsCollectingAvailable(self, enable):
        if self.__callbackDelayer.hasDelayedCallback(self.setIsCollectingAvailable):
            self.__callbackDelayer.stopCallback(self.setIsCollectingAvailable)
        if self.__isCollectingAnimPlaying:
            self.__callbackDelayer.delayCallback(1.0, partial(self.setIsCollectingAvailable, enable))
            return
        state = self.CollectingStates.COLLECTING_AVAILABLE if enable else self.CollectingStates.DEFAULT
        self.__switchState(state)

    @decorators.adisp_process('updating')
    def collect(self, callback):
        from new_year.ny_processor import CollectingResourcesProcessor
        self.__sendMenuResourcesLock(True)
        result = yield CollectingResourcesProcessor().request()
        if result.success:
            self.__switchState(self.CollectingStates.DEFAULT)
        else:
            self.__sendMenuResourcesLock(False)
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    def __switchState(self, state, isInit=False):
        states = self.CollectingStates
        if self.__currentState == state:
            return
        self.onSwitchCollectingState(isInit)
        if self.__currentState == states.DEFAULT and state == states.COLLECTING_AVAILABLE:
            lastLoggedDay = AccountSettings.getSettings(LAST_LOGGED_SERVER_DAY)
            currentServerDay = time_utils.getServerGameDay()
            if lastLoggedDay != currentServerDay:
                AccountSettings.setSettings(LAST_LOGGED_SERVER_DAY, currentServerDay)
            if isInit:
                self.onResources3DStateUpdate('ny_craft_state_full')
            else:
                self.onStartCollectingAvailableAnim()
        if self.__currentState == states.COLLECTING_AVAILABLE and state != states.COLLECTING_AVAILABLE:
            self.__startAnim()
        self.__currentState = state

    def __getCurrentState(self):
        return self.CollectingStates.COLLECTING_AVAILABLE if isCollectingAvailable() else self.CollectingStates.DEFAULT

    def __onSpaceCreate(self):
        self.__switchState(self.__getCurrentState(), isInit=True)
        self.__handleTimers()

    def __onResourceCollected(self, event):
        if not self.__isCollectingAnimPlaying:
            return
        self.__releaseAsync(event.ctx.get('resource'))

    def __onFriendResourceCollected(self, _):
        self.__startAnim()

    def __onObjectStateChanged(self):
        self.__isResourcesCurrentObj = NewYearNavigation.getCurrentObject() == NYObjects.RESOURCES
        if not self.__isResourcesCurrentObj and self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CHANGE_OBJECT)

    def __onFriendHangarEnter(self, *_):
        if self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CHANGE_OBJECT)
        if isCollectingAvailable():
            self.onResources3DStateUpdate('ny_craft_state_full')
        else:
            self.onResources3DStateUpdate('ny_craft_state_empty')

    def __onFriendHangarExit(self, *_):
        if self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CHANGE_OBJECT)
        if isCollectingAvailable():
            self.onResources3DStateUpdate('ny_craft_state_full')
        else:
            self.onResources3DStateUpdate('ny_craft_state_empty')

    def __onClientUpdated(self, diff, _):
        festivityKey = self.__itemsCache.items.festivity.dataKey
        if festivityKey in diff:
            keys = diff[festivityKey].keys()
            if SyncDataKeys.RESOURCE_COLLECTING in keys:
                self.__switchState(self.__getCurrentState())
                self.__handleTimers()

    def __handleTimers(self, friendSwitching=False):
        tillTime = getCollectingCooldownTime()
        if not friendSwitching:
            if tillTime > 0.0:
                timedSet = partial(self.setIsCollectingAvailable, True)
                self.__callbackDelayer.delayCallback(tillTime, timedSet)
        updateFriend3DScene = partial(self.onResources3DStateUpdate, 'ny_craft_state_full')
        update3DScene = partial(self.onResources3DStateUpdate, 'ny_craft_state_full')
        if self.__friendService.isInFriendHangar:
            if self.__callbackDelayer.hasDelayedCallback(update3DScene):
                self.__callbackDelayer.stopCallback(update3DScene)
            tillTime = self.__friendService.getFriendCollectingCooldownTime()
            if tillTime > 0.0:
                self.__callbackDelayer.delayCallback(tillTime, updateFriend3DScene)
        else:
            if self.__callbackDelayer.hasDelayedCallback(updateFriend3DScene):
                self.__callbackDelayer.stopCallback(updateFriend3DScene)
            if tillTime > 0.0:
                self.__callbackDelayer.delayCallback(tillTime, update3DScene)

    @wg_async
    def __startAnim(self):
        if not self.__isResourcesCurrentObj:
            return
        elif self.__isCollectingAnimPlaying:
            return
        else:
            self.__isCollectingAnimPlaying = True
            self.__sendMenuResourcesLock(True)
            waitAnim = True
            result = None
            for resourceName in self.__RESOURCE_ORDER:
                self.onStartCollectingAnim(resourceName, waitAnim)
                self.onResources3DStateUpdate(self.__VFX_TRIGGER_TEMPLATE.format(resourceName.value))
                if waitAnim:
                    result = yield wg_await(self.__wait())
                if AnimStoppingReasons.hasValue(result):
                    if result is AnimStoppingReasons.CLEAR:
                        break
                    elif result is AnimStoppingReasons.CHANGE_OBJECT:
                        waitAnim = False
                        self.__isCollectingAnimPlaying = False
                        self.__sendMenuResourcesLock(False)
                        self.onCancelCollectingAnim()
                self.onCollectingUpdateResource(resourceName.value)

            self.__isCollectingAnimPlaying = False
            self.__sendMenuResourcesLock(False)
            return

    @wg_async
    def __wait(self):
        if self.__event.is_set():
            self.__event.clear()
        try:
            yield wg_await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(self.__result)

    def __releaseAsync(self, result):
        self.__result = result
        self.__event.set()

    def __sendMenuResourcesLock(self, lock):
        if self.__menuResourcesLocked == lock:
            return
        self.__menuResourcesLocked = lock
        self.onCollectingUpdateLock(lock)
