# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_trigger_hints.py
import typing
from enum import IntEnum
import Event
from constants import SECONDS_IN_DAY
from frameworks.wulf.view.array import fillStringsArray
from helpers import dependency, time_utils
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import SyncDataKeys, NYObjects, GuestsQuestsTokens, NyWidgetTopMenu, NyTabBarChallengeView
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, INewYearTriggerHintsController, ICelebrityController, ICelebritySceneController, IFriendServiceController
if typing.TYPE_CHECKING:
    from ny_common.ObjectsConfig import ObjectsConfig
ZERO_LEVEL = 0

class TriggerHintsStates(IntEnum):
    RESOURCES = 0
    DECORATION_ZONES = 1
    GUESTA = 2
    TOURNAMENT = 3
    NONE = 4


checkKeys = {SyncDataKeys.COMPLETED_GUEST_QUESTS, SyncDataKeys.RESOURCE_COLLECTING, SyncDataKeys.OBJECTS_LEVELS}

class NewYearTriggerHintsController(INewYearTriggerHintsController):
    __nyController = dependency.descriptor(INewYearController)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __friendService = dependency.descriptor(IFriendServiceController)
    onStateChanged = Event.Event()

    def __init__(self):
        super(NewYearTriggerHintsController, self).__init__()
        self.__state = None
        self.__isHintSkipped = False
        return

    def onLobbyInited(self, event):
        self.__initialize()

    def onDisconnected(self):
        self.__clear()

    @property
    def triggerHintsState(self):
        return self.__state

    def checkForGuestARequirements(self, withoutResourceCheck=False):
        guestACompletedCount = self.__celebrityController.getCompletedGuestQuestsCount(GuestsQuestsTokens.GUEST_A)
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(GuestsQuestsTokens.GUEST_A)
        quests = questsHolder.getQuests()
        currency, price = GuestsQuestsConfigHelper.getQuestPrice(quests[0])
        resourceBalance = self.__nyController.currencies.getResouceBalance(currency)
        return guestACompletedCount == 0 and (withoutResourceCheck or price <= resourceBalance)

    def checkForTournamentRequirements(self, withoutHintSkippedCheck=False):
        return self.__celebritySceneController.completedQuestsCount == 0 and (withoutHintSkippedCheck or not self.__isHintSkipped)

    def hide(self):
        self.__isHintSkipped = True
        self.__updateState()

    def setActiveSidebarTabs(self, model, menuName, tabName):
        activeTabs = {NyWidgetTopMenu.GLADE: self.__gladeSidebarTriggerHints,
         NyWidgetTopMenu.CHALLENGE: self.__challengeSidebarTriggerHints}
        tabsList = activeTabs.get(menuName, lambda : [])()
        if tabName in tabsList:
            tabsList = []
        triggerHintTabsArray = model.triggerHintTabs.getActiveTabs()
        fillStringsArray(tabsList, triggerHintTabsArray)

    def getActiveMenuTabs(self, tabName):
        tabsList = []
        if self.triggerHintsState == TriggerHintsStates.DECORATION_ZONES:
            tabsList = [NyWidgetTopMenu.GLADE]
        elif self.triggerHintsState == TriggerHintsStates.GUESTA or self.triggerHintsState == TriggerHintsStates.TOURNAMENT:
            tabsList = [NyWidgetTopMenu.CHALLENGE]
        return [] if tabName in tabsList else tabsList

    def __initialize(self):
        if not self.__checkAnyRequirements():
            return
        self.__nyController.onStateChanged += self.__updateState
        self.__nyController.onDataUpdated += self.__onDataUpdated
        self.__nyController.currencies.onBalanceUpdated += self.__updateState
        self.__friendService.onFriendHangarEnter += self.__onFriendHangarEnter
        self.__friendService.onFriendHangarExit += self.__onFriendHangarExit
        self.__updateState()

    def __clear(self, withFriends=True):
        self.__nyController.onStateChanged -= self.__updateState
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        self.__nyController.currencies.onBalanceUpdated -= self.__updateState
        self.__isHintSkipped = False
        self.__state = None
        if withFriends:
            self.__friendService.onFriendHangarEnter -= self.__onFriendHangarEnter
            self.__friendService.onFriendHangarExit -= self.__onFriendHangarExit
        return

    def __onDataUpdated(self, keys, _):
        if checkKeys.intersection(set(keys)):
            self.__updateState()

    def __onFriendHangarEnter(self, *_):
        self.__state = TriggerHintsStates.NONE
        self.onStateChanged()
        self.__clear(False)

    def __onFriendHangarExit(self, *_):
        self.__initialize()

    def __gladeSidebarTriggerHints(self):
        if self.triggerHintsState == TriggerHintsStates.RESOURCES:
            return [NYObjects.RESOURCES]
        return list(NYObjects.UPGRADABLE_GROUP) if self.triggerHintsState == TriggerHintsStates.DECORATION_ZONES else []

    def __challengeSidebarTriggerHints(self):
        if self.triggerHintsState == TriggerHintsStates.GUESTA:
            return [NyTabBarChallengeView.GUEST_A]
        return [NyTabBarChallengeView.TOURNAMENT] if self.triggerHintsState == TriggerHintsStates.TOURNAMENT else []

    def __checkIsEnoughToBuy(self, nextLevelDescr):
        levelPrice = nextLevelDescr.getLevelPrice()
        return all((self.__nyController.currencies.getResouceBalance(currency) >= count for currency, count in levelPrice.iteritems()))

    @dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyCtx=ILobbyContext)
    def __checkForResourcesRequirements(self, itemsCache=None, lobbyCtx=None):
        lastCollectingDay, _, __ = itemsCache.items.festivity.getResourceCollecting()
        eventStartTime = lobbyCtx.getServerSettings().getNewYearGeneralConfig().getEventStartTime()
        startOfDayOffset = time_utils.getStartOfNewGameDayOffset()
        eventStartDay = (eventStartTime - startOfDayOffset) / SECONDS_IN_DAY - 1
        return lastCollectingDay is None or lastCollectingDay < eventStartDay

    def __checkForDecorationZonesRequirements(self, withoutResourceCheck=False):
        objectsConfig = self.__nyController.customizationObjects.getConfig()
        decorationsCurrentLevels = [ self.__nyController.customizationObjects.getLevel(i) for i in NYObjects.UPGRADABLE_GROUP ]
        firObject = objectsConfig.getObjectByID(NYObjects.TREE).getNextLevel(ZERO_LEVEL)
        fairObject = objectsConfig.getObjectByID(NYObjects.FIELD_KITCHEN).getNextLevel(ZERO_LEVEL)
        installationObject = objectsConfig.getObjectByID(NYObjects.SCULPTURE).getNextLevel(ZERO_LEVEL)
        return max(decorationsCurrentLevels) == ZERO_LEVEL and (withoutResourceCheck or any((self.__checkIsEnoughToBuy(obj) for obj in [firObject, fairObject, installationObject])))

    def __checkAnyRequirements(self):
        return self.__checkForResourcesRequirements() or self.__checkForDecorationZonesRequirements(True) or self.checkForGuestARequirements(True) or self.checkForTournamentRequirements(True)

    def __updateState(self):
        lastState = self.__state
        if self.__checkForResourcesRequirements():
            self.__state = TriggerHintsStates.RESOURCES
        elif self.__checkForDecorationZonesRequirements():
            self.__state = TriggerHintsStates.DECORATION_ZONES
            if self.__isHintSkipped:
                self.__isHintSkipped = False
        elif self.checkForGuestARequirements():
            self.__state = TriggerHintsStates.GUESTA
            if self.__isHintSkipped:
                self.__isHintSkipped = False
        elif self.checkForTournamentRequirements():
            self.__state = TriggerHintsStates.TOURNAMENT
        else:
            self.__state = TriggerHintsStates.NONE
        if lastState != self.__state:
            self.onStateChanged()
        if not self.__checkAnyRequirements():
            self.__clear()
