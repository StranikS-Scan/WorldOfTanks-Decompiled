# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_resource_collecting_helper.py
import logging
import typing
from enum import Enum
from BWUtil import AsyncReturn
import CGF
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_LOGGED_SERVER_DAY, LAST_SEEN_COLLECTING_INDEX
from Event import EventManager, Event
from GenericComponents import VSEComponent
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from new_year.newyear_cgf_components.lobby_components import ResourcesPlaceComponent
from new_year.ny_constants import SyncDataKeys, AdditionalCameraObject, NyWidgetTopMenu
from new_year.ny_notifications_helpers import sendNYResourceCollectingAvailableMessage
from ny_common.settings import ResourceCollectingConsts
from shared_utils import first, CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import IFriendServiceController, INewYearController
from uilogging.ny.loggers import NyResourcesLogger
from wg_async import AsyncScope, AsyncEvent, wg_async, wg_await, BrokenPromiseError, delay
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
    _, lastCollectingTime, _ = itemsCache.items.festivity.getResourceCollecting()
    if collectingDescr is None:
        currentCollectingDescr = getCurrentCollectingDescr(itemsCache=itemsCache)
    else:
        currentCollectingDescr = collectingDescr
    if currentCollectingDescr is None:
        return timeTill
    elif lastCollectingTime is None:
        return 0
    else:
        cooldown = currentCollectingDescr.getCollectingCooldown()
        endOfDayCollectTime = time_utils.getDayTimeLeft() + time_utils.ONE_MINUTE
        if isinstance(cooldown, int):
            timeTill = min(endOfDayCollectTime, max(lastCollectingTime + cooldown - time_utils.getServerUTCTime(), 0))
        elif isinstance(cooldown, str) and cooldown == 'endOfGameDay':
            timeTill = endOfDayCollectTime
        return timeTill


@dependency.replace_none_kwargs(itemsCache=IItemsCache, friendService=IFriendServiceController)
def isManualCollectingAvailable(itemsCache=None, friendService=None):
    return getCollectingCooldownTime(itemsCache=itemsCache) == 0 if friendService.friendHangarSpaId is None else friendService.getFriendCollectingCooldownTime() == 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isAutoCollectingAvailable(itemsCache=None):
    currentCollectingDescr = getNextCollectingDescr(itemsCache=itemsCache)
    if currentCollectingDescr is None:
        return False
    else:
        collectingType = currentCollectingDescr.getCollectingByType(ResourceCollectingConsts.AUTO_COLLECTING)
        if collectingType is None:
            return False
        price = collectingType.getPrice()
        if not price:
            return True
        currency = first(price)
        balance = int(itemsCache.items.stats.money.getSignValue(currency))
        return False if price[currency] > balance else True


@dependency.replace_none_kwargs(itemsCache=IItemsCache, friendService=IFriendServiceController)
def getAvgResourcesByCollecting(forceFriend=False, itemsCache=None, friendService=None):
    if friendService.friendHangarSpaId or forceFriend:
        resources = getNYResourceCollectingConfig().getFriendResources()
    else:
        currentCollectingDescr = getNextCollectingDescr(itemsCache=itemsCache)
        if currentCollectingDescr is None:
            return 0
        resources = currentCollectingDescr.getResources()
    return 0 if not resources else int(round(sum(resources.values()) / len(resources)))


def getResourceCollectingByIndex(resourceType, index, config=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    collectingDescr = config.getCollectingDescriptorByIndex(index)
    if collectingDescr is None:
        return 0
    else:
        resources = collectingDescr.getResources()
        return 0 if not resources else resources.get(resourceType, 0)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getAutoCollectingResourcesPrice(itemsCache=None):
    currentCollectingDescr = getNextCollectingDescr(itemsCache=itemsCache)
    if currentCollectingDescr is None:
        return 0
    else:
        collectingType = currentCollectingDescr.getCollectingByType(ResourceCollectingConsts.AUTO_COLLECTING)
        if collectingType is None:
            return 0
        price = collectingType.getPrice()
        return 0 if not price else first(price.itervalues())


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCurrentCollectingDescr(config=None, itemsCache=None):
    if config is None:
        config = getNYResourceCollectingConfig()
    _, __, activeIdx = itemsCache.items.festivity.getResourceCollecting()
    return config.getNextCollectingDescriptor(activeIdx) if activeIdx is None else config.getCollectingDescriptorByIndex(activeIdx)


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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCollectingStats(itemsCache=None):
    return itemsCache.items.festivity.getAutoCollectingStats()


@dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
def _send3dSceneTrigger(state, hangarSpace=None):
    resourcesPlaceQueury = CGF.Query(hangarSpace.spaceID, (VSEComponent, ResourcesPlaceComponent, CGF.GameObject))
    for vseComponent, _, __ in resourcesPlaceQueury:
        vseComponent.context.onTriggerEvent(state)


def setResources3DSceneFull():
    _send3dSceneTrigger('ny_craft_state_full')


def setResources3DSceneEmpty():
    _send3dSceneTrigger('ny_craft_state_empty')


class AnimStoppingReasons(CONST_CONTAINER):
    CLEAR = 1
    CHANGE_OBJECT = 2


class ResourceCollectingHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __RESOURCE_ORDER = (Resource.IRON,
     Resource.EMERALD,
     Resource.CRYSTAL,
     Resource.AMBER)
    __VFX_TRIGGER_TEMPLATE = 'ny_craft_state_{}_collected'

    class CollectingStates(Enum):
        AUTO_ENABLED = 0
        COLLECTING_AVAILABLE = 1
        DEFAULT = 3

    class InitTypes(Enum):
        SPACE_CREATED = 0
        ENTER_FRIEND = 1
        EXIT_FRIEND = 2

    def __init__(self):
        self.__eventManager = EventManager()
        self.onCollectingUpdateLock = Event(self.__eventManager)
        self.onCollectingUpdateResource = Event(self.__eventManager)
        self.onStartCollectingAnim = Event(self.__eventManager)
        self.onStartCollectingAvailableAnim = Event(self.__eventManager)
        self.onCancelCollectingAnim = Event(self.__eventManager)
        self.__resourceMarkers = {}
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = None
        self.__isCollectingAnimPlaying = False
        self.__isResourcesCurrentObj = False
        self.__menuResourcesLocked = False
        self.__currentState = self.CollectingStates.DEFAULT
        return

    def onLobbyInited(self):
        self.__event.clear()
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        NewYearNavigation.onSwitchView += self.__onSwitchView
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreate
        g_eventBus.addListener(NyResourcesEvent.RESOURCE_COLLECTED, self.__onResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(NyResourcesEvent.FRIEND_RESOURCE_COLLECTED, self.__onFriendResourceCollected, EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        self.__eventManager.clear()
        if self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CLEAR)
        self.__isCollectingAnimPlaying = False
        self.__isResourcesCurrentObj = False
        self.__menuResourcesLocked = False
        self.__currentState = self.CollectingStates.DEFAULT
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        NewYearNavigation.onSwitchView -= self.__onSwitchView
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        g_eventBus.removeListener(NyResourcesEvent.RESOURCE_COLLECTED, self.__onResourceCollected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(NyResourcesEvent.FRIEND_RESOURCE_COLLECTED, self.__onFriendResourceCollected, EVENT_BUS_SCOPE.LOBBY)

    def setIsCollectingAvailable(self, enable, friendSwitching=None):
        if friendSwitching is None and self.__currentState == self.CollectingStates.AUTO_ENABLED:
            return
        else:
            state = self.CollectingStates.COLLECTING_AVAILABLE if enable else self.CollectingStates.DEFAULT
            if friendSwitching is None:
                isInit = None
            elif friendSwitching:
                isInit = self.InitTypes.ENTER_FRIEND
            else:
                isInit = self.InitTypes.EXIT_FRIEND
            self.__switchState(state, isInit=isInit)
            return

    @decorators.adisp_process('updating')
    def manualCollect(self, callback):
        from new_year.ny_processor import ManualCollectingResourcesProcessor
        self.__sendMenuResourcesLock(True)
        result = yield ManualCollectingResourcesProcessor().request()
        if result.success:
            self.__switchState(self.CollectingStates.DEFAULT)
        else:
            self.__sendMenuResourcesLock(False)
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @decorators.adisp_process('updating')
    def activateAutoCollecting(self, parent, callback):
        from new_year.ny_processor import AutoCollectingResourcesProcessor
        self.__sendMenuResourcesLock(True)
        result = yield AutoCollectingResourcesProcessor(True, parent).request()
        logger = NyResourcesLogger()
        if result.success:
            logger.logAutoCollectionConfirmedClick('confirmed')
            self.__switchState(self.CollectingStates.AUTO_ENABLED)
        else:
            logger.logAutoCollectionConfirmedClick('canceled')
            self.__sendMenuResourcesLock(False)
        callback(result.success)

    @decorators.adisp_process('updating')
    def disableAutoCollecting(self, parent, callback):
        from new_year.ny_processor import AutoCollectingResourcesProcessor
        result = yield AutoCollectingResourcesProcessor(False, parent).request()
        if result.success:
            self.__switchState(self.CollectingStates.DEFAULT)
        callback(result.success)

    def onDataUpdated(self, keys):
        if SyncDataKeys.AUTO_COLLECTING_STATS in keys:
            self.__updateCollectingStats()

    def __updateCollectingStats(self):
        stats = getCollectingStats()
        if not stats:
            self.__switchState(self.CollectingStates.DEFAULT)
            return
        self.__startAnim(isAuto=True)

    def __switchState(self, state, isInit=None):
        states = self.CollectingStates
        if isInit is not None:
            self.__currentState = states.DEFAULT
        elif self.__currentState == state:
            return
        if self.__currentState == states.AUTO_ENABLED and state == states.COLLECTING_AVAILABLE:
            return
        else:
            if self.__currentState == states.DEFAULT and state == states.COLLECTING_AVAILABLE:
                lastLoggedDay = AccountSettings.getSettings(LAST_LOGGED_SERVER_DAY)
                currentServerDay = time_utils.getServerGameDay()
                if lastLoggedDay != currentServerDay:
                    AccountSettings.setSettings(LAST_LOGGED_SERVER_DAY, currentServerDay)
                    AccountSettings.setSettings(LAST_SEEN_COLLECTING_INDEX, -1)
                _, __, activeIdx = self.__itemsCache.items.festivity.getResourceCollecting()
                if activeIdx is None:
                    activeIdx = -1
                activeIdx += 1
                lastSeenColectingIndex = AccountSettings.getSettings(LAST_SEEN_COLLECTING_INDEX)
                if lastSeenColectingIndex != activeIdx:
                    AccountSettings.setSettings(LAST_SEEN_COLLECTING_INDEX, activeIdx)
                    sendNYResourceCollectingAvailableMessage(resourcesCount=getAvgResourcesByCollecting())
                setResources3DSceneFull()
                if isInit is None:
                    self.onStartCollectingAvailableAnim()
            if self.__currentState == states.COLLECTING_AVAILABLE:
                self.__startAnim()
            if state == states.DEFAULT and not self.__isCollectingAnimPlaying:
                setResources3DSceneEmpty()
            if isInit is not None and state == states.AUTO_ENABLED:
                setResources3DSceneEmpty()
            self.__currentState = state
            return

    def __getCurrentState(self):
        isAutoCollectingActivated, _, _ = self.__itemsCache.items.festivity.getResourceCollecting()
        if isAutoCollectingActivated:
            return self.CollectingStates.AUTO_ENABLED
        return self.CollectingStates.COLLECTING_AVAILABLE if isManualCollectingAvailable() else self.CollectingStates.DEFAULT

    def __onSpaceCreate(self):
        if not self.__nyController.isEnabled():
            return
        setResources3DSceneEmpty()
        self.__switchState(self.__getCurrentState(), isInit=self.InitTypes.SPACE_CREATED)

    def __onResourceCollected(self, event):
        if not self.__isCollectingAnimPlaying:
            return
        self.__releaseAsync(event.ctx.get('resource'))

    def __onFriendResourceCollected(self, _):
        self.__startAnim()

    def __onObjectStateChanged(self):
        self.__isResourcesCurrentObj = NewYearNavigation.getCurrentObject() == AdditionalCameraObject.RESOURCES
        if not self.__isResourcesCurrentObj and self.__isCollectingAnimPlaying:
            self.__releaseAsync(AnimStoppingReasons.CHANGE_OBJECT)

    def __onSwitchView(self, ctx):
        if self.__isCollectingAnimPlaying and ctx.menuName == NyWidgetTopMenu.FRIENDS:
            self.__releaseAsync(AnimStoppingReasons.CHANGE_OBJECT)

    @wg_async
    def __startAnim(self, isAuto=False):
        if not self.__isResourcesCurrentObj:
            return
        elif self.__isCollectingAnimPlaying:
            return
        else:
            self.__isCollectingAnimPlaying = True
            self.__sendMenuResourcesLock(True)
            if isAuto:
                self.onStartCollectingAvailableAnim()
                yield wg_await(delay(0.2))
            waitAnim = True
            result = None
            for resourceName in self.__RESOURCE_ORDER:
                self.onStartCollectingAnim(resourceName, waitAnim)
                _send3dSceneTrigger(self.__VFX_TRIGGER_TEMPLATE.format(resourceName.value))
                if waitAnim:
                    result = yield wg_await(self.__wait())
                if AnimStoppingReasons.hasValue(result):
                    if result is AnimStoppingReasons.CLEAR:
                        break
                    elif result is AnimStoppingReasons.CHANGE_OBJECT:
                        waitAnim = False
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
