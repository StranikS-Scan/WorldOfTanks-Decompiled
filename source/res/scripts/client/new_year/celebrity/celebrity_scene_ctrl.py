# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/celebrity/celebrity_scene_ctrl.py
import logging
import typing
from Event import Event, EventManager
from account_helpers.AccountSettings import AccountSettings, NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK, NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from helpers import dependency
from items.components.ny_constants import CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getCelebrityAdditionalTokenQuests, getCelebrityMarathonQuests, getCelebrityQuestByFullID, getCelebrityQuestCount, getCelebrityTokens, iterCelebrityActiveQuestsIDs, getCelebrityAdditionalQuestsConfig
from ny_common.settings import NY_CONFIG_NAME, CelebrityConsts
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICelebritySceneController
if typing.TYPE_CHECKING:
    from typing import Dict, List, Union
    from gui.server_events.event_items import TokenQuest, CelebrityQuest, CelebrityTokenQuest
_logger = logging.getLogger(__name__)

class CelebritySceneController(ICelebritySceneController):
    __slots__ = ('__eventsManager', '__quests', '__isInChallengeView', '__tokens', '__marathonQuests', '__completedDayQuestsMask', '__questsCount', '__completedQuestsCount')
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(CelebritySceneController, self).__init__()
        self.__eventsManager = EventManager()
        self.onQuestsUpdated = Event(self.__eventsManager)
        self.__quests = {}
        self.__tokens = {}
        self.__marathonQuests = {}
        self.__additionalTokenQuests = []
        self.__completedDayQuestsMask = 0
        self.__completedAddQuestsMask = 0
        self.__questsCount = 0
        self.__completedQuestsCount = 0
        self.__completedAddQuestsCount = 0
        self.__isInChallengeView = False

    @property
    def isChallengeVisited(self):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.CELEBRITY_SCREEN_VISITED, False)

    @property
    def isWelcomeAnimationViewed(self):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.CELEBRITY_WELCOME_VIEWED, False)

    @property
    def isInChallengeView(self):
        return self.__isInChallengeView

    @property
    def isChallengeCompleted(self):
        return self.completedQuestsCount == self.questsCount and self.isAllAdditionalQuestsCompleted

    @property
    def isAllAdditionalQuestsCompleted(self):
        completedQuestsCount = 0
        additionalQuestsConfig = getCelebrityAdditionalQuestsConfig()
        for additionalQuestInfo in additionalQuestsConfig.itervalues():
            receivedRewardsTokens = additionalQuestInfo.getDependencies().getTokensDependencies()
            if all((self.__itemsCache.items.tokens.getTokenCount(token) for token in receivedRewardsTokens)):
                completedQuestsCount += 1

        if self.__additionalTokenQuests:
            for q in self.__additionalTokenQuests:
                if q is not None and q.isCompleted():
                    completedQuestsCount += 1

        return completedQuestsCount >= len(additionalQuestsConfig)

    @property
    def isAllMainQuestsCompleted(self):
        return self.completedQuestsCount >= self.questsCount

    @property
    def hasNewCompletedQuests(self):
        completedMask = self.__getCompletedQuestsMask(NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK)
        return bool(completedMask ^ self.__completedDayQuestsMask)

    @property
    def hasNewCompletedAddQuests(self):
        completedMask = self.__getCompletedQuestsMask(NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK)
        return bool(completedMask ^ self.__completedAddQuestsMask)

    @property
    def quests(self):
        return self.__quests

    @property
    def tokens(self):
        return self.__tokens

    @property
    def marathonQuests(self):
        return self.__marathonQuests

    @property
    def completedDayQuestsMask(self):
        return self.__completedDayQuestsMask

    @property
    def completedAddQuestsMask(self):
        return self.__completedAddQuestsMask

    @property
    def questsCount(self):
        return self.__questsCount

    @property
    def completedQuestsCount(self):
        return self.__completedQuestsCount

    @property
    def completedAddQuestsCount(self):
        return self.__completedAddQuestsCount

    def fini(self):
        self.__destroy()
        super(CelebritySceneController, self).fini()

    def onLobbyInited(self, _):
        self.__subscribe()
        self.__updateQuests()

    def onDisconnected(self):
        self.__destroy()

    def onAvatarBecomePlayer(self):
        self.__destroy()

    def onEnterChallenge(self):
        self.__isInChallengeView = True
        self.__saveCompletedQuestsMask()

    def onExitChallenge(self):
        self.__isInChallengeView = False

    def __destroy(self):
        self.__unsubscribe()
        self.__eventsManager.clear()
        self.__quests.clear()
        self.__tokens.clear()
        self.__marathonQuests.clear()
        self.__additionalTokenQuests = []
        self.__isInChallengeView = False

    def __subscribe(self):
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__eventsCache.onQuestConditionUpdated += self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __unsubscribe(self):
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__eventsCache.onQuestConditionUpdated -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onSyncCompleted(self):
        self.__updateQuests()

    def __onServerSettingsChange(self, diff):
        if diff.get(NY_CONFIG_NAME, {}).get(CelebrityConsts.CONFIG_NAME) is None:
            return
        else:
            self.__updateQuests()
            return

    def __updateQuests(self):
        self.__marathonQuests = getCelebrityMarathonQuests()
        self.__additionalTokenQuests = getCelebrityAdditionalTokenQuests()
        self.__tokens = getCelebrityTokens()
        self.__completedDayQuestsMask = 0
        self.__completedAddQuestsMask = 0
        for token in iterCelebrityActiveQuestsIDs():
            quest = getCelebrityQuestByFullID(token)
            if not quest or not quest.isCompleted():
                continue
            self.__quests[token] = quest
            qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(token)
            qNumBit = 1 << qNum - 1
            if qType == CelebrityQuestTokenParts.DAY:
                self.__completedDayQuestsMask |= qNumBit
            if qType == CelebrityQuestTokenParts.ADD:
                self.__completedAddQuestsMask |= qNumBit

        self.__questsCount = getCelebrityQuestCount()
        self.__completedQuestsCount = bin(self.completedDayQuestsMask).count('1')
        self.__completedAddQuestsCount = bin(self.completedAddQuestsMask).count('1')
        if not self.__isInChallengeView:
            self.__saveCompletedQuestsMask()
        self.onQuestsUpdated()

    def __getCompletedQuestsMask(self, maskSettingName):
        completedQuestsMask = AccountSettings.getUIFlag(maskSettingName)
        return completedQuestsMask

    def __saveCompletedQuestsMask(self):
        AccountSettings.setUIFlag(NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK, self.__completedDayQuestsMask)
        AccountSettings.setUIFlag(NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK, self.__completedAddQuestsMask)
