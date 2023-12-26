# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/celebrity/celebrity_controller.py
import logging
import typing
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants, CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import GuestsQuestsTokens, GuestQuestTokenActionType, parseCelebrityTokenActionType, SyncDataKeys
from new_year.ny_notifications_helpers import checkAndNotifyAllDecorationReceived
from skeletons.new_year import ICelebrityController, INewYearController
_logger = logging.getLogger(__name__)

class CelebrityController(ICelebrityController):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(CelebrityController, self).__init__()
        self.__eventsManager = EventManager()
        self.onCelebActionTokenUpdated = Event(self.__eventsManager)
        self.onCelebCompletedTokensUpdated = Event(self.__eventsManager)
        self.onDoActionByCelebActionToken = Event(self.__eventsManager)
        self.onCelebRerollTokenRecieved = Event(self.__eventsManager)

    def fini(self):
        self.__destroy()
        super(CelebrityController, self).fini()

    def onLobbyInited(self, _):
        self.__subscribe()

    def onDisconnected(self):
        self.__destroy()

    def onAvatarBecomePlayer(self):
        self.__destroy()

    def getAllTokens(self, guestNames=None, actionTypes=None):
        allTokens = []
        guestNames = guestNames if guestNames else GuestsQuestsTokens.GUESTS_ALL
        actionTypes = actionTypes if actionTypes else GuestQuestTokenActionType.ALL
        for guestName in guestNames:
            for actionType in actionTypes:
                allTokens.extend(GuestsQuestsConfigHelper.getGuestsActionTokens(guestName, actionType))

        return allTokens

    def getAllReceivedTokens(self, guestNames=None, actionTypes=None):
        receivedTokens = []
        for token in self.getAllTokens(guestNames, actionTypes):
            if self.__nyController.isTokenReceived(token):
                receivedTokens.append(token)

        return receivedTokens

    def getCompletedGuestQuestsCount(self, guestName):
        completedTokenName = GuestsQuestsTokens.getGuestCompletedTokenName(guestName)
        return self.__nyController.getTokenCount(completedTokenName)

    def isGuestQuestsCompletedFully(self, guestNames):
        for guestName in guestNames:
            guestQuests = GuestsQuestsConfigHelper.getNYQuestsByGuest(guestName)
            if guestQuests:
                completedCount = self.getCompletedGuestQuestsCount(guestName)
                if completedCount != len(guestQuests.getQuests()):
                    return False

        return True

    def isGuestQuestCompleted(self, guestQuest):
        questIdx = GuestsQuestsConfigHelper.getQuestIndex(guestQuest)
        guestName = GuestsQuestsConfigHelper.getGuestNameByQuest(guestQuest)
        completedCount = self.getCompletedGuestQuestsCount(guestName)
        return completedCount > questIdx

    def doActionByCelebActionToken(self, tokenID):
        if tokenID is None:
            return
        guestName, actionType, level = parseCelebrityTokenActionType(tokenID)
        if guestName is None:
            return
        elif level is not None and not self.__nyController.isTokenReceived(tokenID):
            return
        elif actionType in (GuestQuestTokenActionType.ANIM, GuestQuestTokenActionType.DECORATION):
            self.onDoActionByCelebActionToken(guestName, actionType, level)
            return
        elif actionType == GuestQuestTokenActionType.STORY:
            self.onDoActionByCelebActionToken(guestName, actionType, level)
            return
        else:
            return

    def __destroy(self):
        self.__unsubscribe()
        self.__eventsManager.clear()

    def __subscribe(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate,
         CurrentNYConstants.PDATA_KEY: self.__onCelebQuestCompleteCheck})

    def __unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onTokensUpdate(self, tokens):
        if any((token in GuestsQuestsTokens.GUEST_DEPENDENCIES for token in tokens)):
            self.onCelebCompletedTokensUpdated()
        if any((token == CelebrityQuestTokenParts.REROLL_TOKEN for token in tokens)):
            self.onCelebRerollTokenRecieved()

    def __onCelebQuestCompleteCheck(self, diff):
        if SyncDataKeys.COMPLETED_GUEST_QUESTS in diff:
            completedGuestQuests = diff.get(SyncDataKeys.COMPLETED_GUEST_QUESTS)
            for guestName, questIndex in completedGuestQuests.iteritems():
                self.__handleGuestQuestComplete(guestName, questIndex)

    def __handleGuestQuestComplete(self, guestName, questIndex):
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(guestName)
        quest = questsHolder.getQuestByQuestIndex(questIndex)
        if quest is None:
            return
        else:
            actionQuestToken = GuestsQuestsConfigHelper.getQuestActionToken(quest)
            guestName, actionType, __ = parseCelebrityTokenActionType(actionQuestToken)
            self.onCelebActionTokenUpdated(actionQuestToken)
            if actionType == GuestQuestTokenActionType.DECORATION:
                checkAndNotifyAllDecorationReceived()
            return
