# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/mt_birthday_controller.py
from collections import namedtuple
import json
import logging
import random
import typing
from constants import QUEUE_TYPE
import Event
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.gift_system.constants import GifterResponseState
from gui.prb_control import prbDispatcherProperty
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.gf_header_widget import GFWidgetAliases
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.view_helpers.UsersInfoHelper import BatchUsersInfoHelper
from gui.shared.notifications import NotificationPriorityLevel
from gui.server_events.event_items import Quest
from gui.SystemMessages import SM_TYPE
from helpers import dependency, time_utils, getPercentsFromFloat
from helpers.time_utils import getServerUTCTime, getTimestampFromLocal, utcToLocalDatetime, getDateTimeInLocal, ONE_DAY
from helpers.CallbackDelayer import CallbackDelayer
from messenger.proto.shared_find_criteria import IgnoredFindCriteria
from messenger.storage import storage_getter
from mt_birthday.gui.birthday_helpers import getLootBoxByID
from mt_birthday.gui.game_control.progression_sub_controller import TanksBirthdayProgressionSubController
from mt_birthday.gui.game_control.gift_system_sub_controller import GiftSystemSubController
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController, ILastBattlesPlayersController
from mt_birthday.birthday_constants import BIRTHDAY_BLOGGER_TOKEN, BIRTHDAY_STAMP_CODE, BIRTHDAY_STAMP_CODE_SPECIAL, MT_BIRTHDAY_EVENT_STATE, BirthdayStorageKeys, BIRTHDAY_BLOGGER_LOOTBOX_TAG, isBirthdayQuestGiverQuest, BIRTHDAY_GOLDEN_TICKET_CURRENCY, TAB_ID_TO_ACCOUNT_SETTING, BIRTHDAY_REPLY_GIFT_TOKEN
from mt_birthday.birthday_account_settings import getSettings, setSettings
from mt_birthday_common.constants import BIRTHDAY_BADGE_QUEST
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEventsNotificationsController, IGuiLootBoxesController, ITankAcademyController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from th_async import th_async, await_callback
from BWUtil import AsyncReturn
if typing.TYPE_CHECKING:
    from gui.game_control.events_notifications import EventNotification
    from typing import Optional, Tuple, List, Dict
_logger = logging.getLogger(__name__)
_ENDING_TIME_OFFSET = ONE_DAY * 3
_BirthdaySysMessages = namedtuple('_BirthdaySysMessages', 'keyText, priority, type')
_BIRTHDAY_STATE_TRANSITION_SYS_MESSAGES = {(MT_BIRTHDAY_EVENT_STATE['Active'], MT_BIRTHDAY_EVENT_STATE['Paused']): _BirthdaySysMessages(R.strings.mt_birthday.notification.paused(), NotificationPriorityLevel.HIGH, SM_TYPE.ErrorHeader),
 (MT_BIRTHDAY_EVENT_STATE['Paused'], MT_BIRTHDAY_EVENT_STATE['Active']): _BirthdaySysMessages(R.strings.mt_birthday.notification.resume(), NotificationPriorityLevel.HIGH, SM_TYPE.InformationHeader),
 (MT_BIRTHDAY_EVENT_STATE['Active'], MT_BIRTHDAY_EVENT_STATE['Disabled']): _BirthdaySysMessages(R.strings.mt_birthday.notification.finished(), NotificationPriorityLevel.MEDIUM, SM_TYPE.InformationHeader)}

def birthdayActionsFilter(action):
    return action.eventType == 'MTBirthday'


def birthdayEconomicsFilterFunc(quest):
    return quest.getID() == 'mt_birthday_economics'


def birthdayQuestGiverQuestsFilterFunc(quest):
    return isBirthdayQuestGiverQuest(quest.getID())


def birthdayQuestGiverActiveQuestsFilterFunc(quest):
    return isBirthdayQuestGiverQuest(quest.getID()) and quest.isAvailable().isValid and not quest.isCompleted()


class TanksBirthdayController(ITanksBirthdayController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lastBattlesPlayers = dependency.descriptor(ILastBattlesPlayersController)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiController = dependency.descriptor(IGuiLootBoxesController)
    __tankAcademyController = dependency.descriptor(ITankAcademyController)

    def __init__(self):
        super(TanksBirthdayController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEventSettingsUpdated = Event.Event(self.__eManager)
        self.onNewGiftsReceived = Event.Event(self.__eManager)
        self.onLootboxSeen = Event.Event(self.__eManager)
        self.onQuestsUpdated = Event.Event(self.__eManager)
        self.__eventState = None
        self.__endDate = None
        self.__startDate = None
        self.__goldWagonURL = ''
        self.__ticketExchangeURL = ''
        self.__bannedPlayersIDs = set()
        self.__phrasesIDs = []
        self.__progression = TanksBirthdayProgressionSubController(self.__eManager)
        self.__giftSystem = GiftSystemSubController()
        self.__userInfoHelper = BatchUsersInfoHelper()
        self.__bloggerGiftArenas = set()
        self.__unseenGifts = {}
        self.__giftNotificationSeenCount = 0
        self.__callbackDelayer = CallbackDelayer()
        self.__hangarWidgetAlias = None
        self.__addWidgetHandler()
        return

    def fini(self):
        self.__stop()
        self.__removeWidgetHandler()

    def onDisconnected(self):
        self.__giftNotificationSeenCount = 0
        self.__unseenGifts.clear()
        self.__stop()

    def onConnected(self):
        self.__bannedPlayersIDs = set()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def __stop(self):
        self.__eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        self.__eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self.__guiController.onStorageVisited -= self.__onLootBoxStorageVisited
        self.onEventSettingsUpdated.clear()
        self.__userInfoHelper.clearInvalidData()
        self.__userInfoHelper.clear()
        self.__progression.stop()
        self.__giftSystem.stop()
        self.__callbackDelayer.destroy()

    @property
    def progression(self):
        return self.__progression

    @property
    def giftSystem(self):
        return self.__giftSystem

    @property
    def userInfoHelper(self):
        return self.__userInfoHelper

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def isPlayerBlocked(self, spaID):
        return spaID == 0 or self.isAlreadyReceivedGift(spaID) or self.isBannedPlayer(spaID) or self.isPlayerInBlackList(spaID)

    def getHangarWidgetAlias(self):
        return self.__hangarWidgetAlias

    def isPlayerInBlackList(self, spaID):
        return spaID in {player.getID() for player in self.usersStorage.getList(IgnoredFindCriteria())}

    def isEnabled(self):
        currentTime = getServerUTCTime()
        return self.__eventState == MT_BIRTHDAY_EVENT_STATE['Active'] and self.__startDate <= currentTime < self.__endDate

    def isPaused(self):
        return self.__eventState == MT_BIRTHDAY_EVENT_STATE['Paused']

    def isDisabled(self):
        currentTime = getServerUTCTime()
        return self.__eventState == MT_BIRTHDAY_EVENT_STATE['Disabled'] or currentTime >= self.__endDate

    def isFinished(self):
        currentTime = getServerUTCTime()
        return self.__eventState == MT_BIRTHDAY_EVENT_STATE['Disabled'] and currentTime >= self.__endDate

    def isEnding(self):
        currentTime = getServerUTCTime()
        return self.isEnabled() and currentTime >= self.__endDate - _ENDING_TIME_OFFSET

    def isBlogger(self):
        return bool(self.__itemsCache.items.tokens.getToken(BIRTHDAY_BLOGGER_TOKEN) or self.getSpecialStampCount())

    def getStartTime(self):
        return self.__startDate

    def getExpiryTime(self):
        return self.__endDate

    def onLobbyInited(self, event):
        self.__processAction()
        self.__notificationsCtrl.onEventNotificationsChanged += self.__processAction
        self.__eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self.__progression.start()
        self.__giftSystem.start()
        self.__guiController.onStorageVisited += self.__onLootBoxStorageVisited

    def isValidBattleType(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.RANDOMS) if self.prbDispatcher is not None else False

    def onAccountBecomeNonPlayer(self):
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__processAction

    def getBadgeQuestRequiredReplyTokens(self):
        questData = first(self.__eventsCache.getHiddenQuests(filterFunc=lambda quest: quest.getID() == BIRTHDAY_BADGE_QUEST).values())
        return 0 if not questData else first((t.getNeededCount() for t in questData.accountReqs.getTokens() if t.getID() == BIRTHDAY_REPLY_GIFT_TOKEN), default=0)

    @th_async
    def getLastFightsPlayers(self):
        result = yield self.__lastBattlesPlayers.getLastFightsPlayers()
        raise AsyncReturn(result)

    def addLastFightsPlayerID(self, playerID):
        self.__lastBattlesPlayers.addLastFightsPlayerID(playerID)

    def addLastFightsPlayersIDs(self, playersIDs):
        self.__lastBattlesPlayers.addLastFightsPlayersIDs(playersIDs)

    def isGiftSystemEventActive(self):
        return self.isEnabled() and self.__giftSystem.isGiftEventActive()

    def getBannedPlayersIDs(self):
        return self.__bannedPlayersIDs

    def addBannedPlayersID(self, playerID):
        self.__bannedPlayersIDs.add(playerID)

    def isBannedPlayer(self, spaID):
        return spaID in self.getBannedPlayersIDs()

    def isAlreadyReceivedGift(self, playerID):
        return self.__giftSystem.isAlreadyReceivedGift(playerID)

    def getMagicPercent(self):
        return self.__giftSystem.getMagicPercent() or 0

    def getStampCount(self):
        return self.__giftSystem.getSimpleStampCount()

    def getPhrasesIds(self):
        return self.__phrasesIDs

    def setPhrasesIds(self, phrasesIds):
        self.__phrasesIDs = phrasesIds

    def getGoldenTicketsCount(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(BIRTHDAY_GOLDEN_TICKET_CURRENCY, 0)

    def getMaxSelectedPlayers(self):
        return self.__giftSystem.getAllowMultipleSendCount()

    def getSpecialStampCount(self):
        return self.__giftSystem.getSpecialStampCount()

    def getCooldownGiftTime(self):
        return getTimestampFromLocal(utcToLocalDatetime(getDateTimeInLocal(self.__giftSystem.getExpirationTime())).timetuple()) if self.__giftSystem.getExpirationTime() else 0

    def getLocalEndDate(self):
        return getTimestampFromLocal(getDateTimeInLocal(self.getExpiryTime()).timetuple())

    def getWaitResponsePlayers(self):
        return self.__giftSystem.getWaitResponsePlayers()

    def shufflePhrases(self):
        phrasesKeys = R.strings.player_phrases.player.keys()
        phrases = [ int(x.split('_')[-1]) for x in phrasesKeys ]
        random.shuffle(phrases)
        self.__phrasesIDs = phrases

    def shuffleLastPhrases(self, last=5):
        phrases = self.__phrasesIDs[last:]
        random.shuffle(phrases)
        self.__phrasesIDs[last:] = phrases

    def getNextPhraseID(self):
        phrase = self.__phrasesIDs.pop(0)
        self.__phrasesIDs.append(phrase)
        self.shuffleLastPhrases()
        return phrase

    @staticmethod
    def getRandomBloggerPhraseID(currPhraseID=None):
        phrasesKeys = R.strings.player_phrases.blogger.keys()
        if currPhraseID is not None:
            phrases = [ x for x in phrasesKeys if int(x.split('_')[-1]) != currPhraseID ]
        else:
            phrases = [ x for x in phrasesKeys ]
        chosenPhrase = random.choice(phrases)
        return int(chosenPhrase.split('_')[-1])

    def isFirstBloggerAfterBattleGift(self, arenaUniqueID):
        return arenaUniqueID not in self.__bloggerGiftArenas and self.isBlogger()

    def onBloggerGiftSent(self, arenaUniqueID):
        self.__bloggerGiftArenas.add(arenaUniqueID)

    def getStampForSending(self, arenaUniqueID):
        return BIRTHDAY_STAMP_CODE_SPECIAL if self.isBlogger() and self.getSpecialStampCount() and self.isFirstBloggerAfterBattleGift(arenaUniqueID) else BIRTHDAY_STAMP_CODE

    def getEconomicBonusTypes(self):
        quest = first(self.getBattleQuests().values(), None)
        if not quest:
            return []
        else:
            bonusTypes = quest.preBattleCond.getConditions().find('bonusTypes').getValue()
            return bonusTypes

    def getEconomyBonusValue(self):
        quest = first(self.getBattleQuests().values(), None)
        if not quest:
            return 0
        else:
            economyValue = quest.getRawBonuses().get('xpFactor', 0)
            return getPercentsFromFloat(economyValue)

    def getBattleQuests(self):
        return self.__eventsCache.getHiddenQuests(birthdayEconomicsFilterFunc)

    def getQuestGiverBattleQuests(self):
        allQuests = self.__eventsCache.getHiddenQuests(birthdayQuestGiverQuestsFilterFunc)
        quests = [ v for k, v in allQuests.iteritems() if k.split(':')[1] == 'quests' ]
        challenges = [ v for k, v in allQuests.iteritems() if k.split(':')[1] == 'challenges' ]
        return (quests, challenges)

    def hasActiveQuestGiverQuest(self):
        return len(self.__eventsCache.getHiddenQuests(birthdayQuestGiverActiveQuestsFilterFunc)) > 0

    def getMaxProgressionLevel(self):
        return len(self.__progression.getSimpleLevels())

    def getUnseenGiftsCount(self):
        return sum((v for k, v in self.__unseenGifts.iteritems() if not k[1]))

    def getUnseenGiftId(self):
        return first((k[0] for k in self.__unseenGifts if not k[1]))

    def pushNewGiftReceived(self, giftId, count):
        if self.isEnabled():
            lootbox = getLootBoxByID(giftId)
            isSpecialGift = lootbox is not None and lootbox.isTagExist(BIRTHDAY_BLOGGER_LOOTBOX_TAG)
            self.__unseenGifts.setdefault((giftId, isSpecialGift), 0)
            self.__unseenGifts[(giftId, isSpecialGift)] += count
            if not isSpecialGift:
                setSettings(BirthdayStorageKeys.GIFT_RECEIVED, True)
            self.onNewGiftsReceived(giftId, count, isSpecialGift)
        return

    def seenGiftNotification(self, count):
        self.__giftNotificationSeenCount = count

    def getNewGiftForNotification(self):
        return self.getUnseenGiftsCount() - self.__giftNotificationSeenCount

    def getGoldWagonURL(self):
        return self.__goldWagonURL

    def getTicketExchangeURL(self):
        return self.__ticketExchangeURL

    def isGoldWagonEnabled(self):
        return bool(self.getGoldWagonURL())

    def isTicketExchangeEnabled(self):
        return bool(self.getTicketExchangeURL())

    @th_async
    def sendGifts(self, stampType, receiversIDs, messageIdx, arenaUniqueID=None):
        result = yield await_callback(self.__giftSystem.sendGifts)(stampType, receiversIDs, messageIdx)
        if result and result.state == GifterResponseState.WEB_SUCCESS:
            for declinedReceiver in result.declinedReceivers:
                self.addBannedPlayersID(declinedReceiver)

            if arenaUniqueID is not None and result.entitlementCode == BIRTHDAY_STAMP_CODE_SPECIAL and result.receiverIDs != result.declinedReceivers:
                self.onBloggerGiftSent(arenaUniqueID)
        raise AsyncReturn(result)
        return

    def __onLootBoxStorageVisited(self):
        self.__unseenGifts.clear()
        self.onLootboxSeen()

    def __processAction(self, *args, **kwargs):
        actionData = self.__notificationsCtrl.getEventsNotifications(filterFunc=birthdayActionsFilter)
        prevState = self.__eventState
        if actionData:
            action = json.loads(actionData[0].data)
            state = action['eventState'] if action['eventState'] in MT_BIRTHDAY_EVENT_STATE else MT_BIRTHDAY_EVENT_STATE['Disabled']
            self.__eventState = state
            self.__goldWagonURL = action['goldWagonURL'] if action['goldWagonURL'] else ''
            self.__ticketExchangeURL = action['ticketExchangeURL'] if action['ticketExchangeURL'] else ''
            if time_utils.getTimestampByStrDate(action['startDate']) > time_utils.getTimestampByStrDate(action['endDate']):
                _logger.error('Wrong birthday time date range')
            else:
                self.__startDate = time_utils.getTimestampByStrDate(action['startDate'])
                self.__endDate = time_utils.getTimestampByStrDate(action['endDate'])
                currentTime = getServerUTCTime()
                if currentTime < self.__endDate:
                    self.__callbackDelayer.delayCallback(self.__endDate - currentTime, self.__onEndDate)
        else:
            self.__eventState = MT_BIRTHDAY_EVENT_STATE['Disabled']
        self.__sendStateSysMessage(prevState)
        self.onEventSettingsUpdated()

    def __onEndDate(self):
        self.__updateHangarHeaderEnabled()
        endDateMsg = _BIRTHDAY_STATE_TRANSITION_SYS_MESSAGES.get((MT_BIRTHDAY_EVENT_STATE['Active'], MT_BIRTHDAY_EVENT_STATE['Disabled']))
        self.__pushBirthdayMessage(endDateMsg)

    def __updateHangarHeaderEnabled(self):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.SET_HANGAR_HEADER_ENABLED), scope=EVENT_BUS_SCOPE.LOBBY)

    def __sendStateSysMessage(self, prevState):
        if self.isEnabled() and not self.isWelcomeMessageSent():
            msg = _BirthdaySysMessages(R.strings.mt_birthday.notification.start(), NotificationPriorityLevel.MEDIUM, SM_TYPE.InformationHeader)
            setSettings(BirthdayStorageKeys.BIRTHDAY_WELCOME_NOTIFICATION, True)
        else:
            msg = _BIRTHDAY_STATE_TRANSITION_SYS_MESSAGES.get((prevState, self.__eventState))
        if msg:
            self.__pushBirthdayMessage(msg)

    def isWelcomeMessageSent(self):
        return getSettings(BirthdayStorageKeys.BIRTHDAY_WELCOME_NOTIFICATION)

    def getAccountSettingsTipPathByTabId(self, tabId=None):
        return TAB_ID_TO_ACCOUNT_SETTING.get(tabId, '') if tabId is not None else BirthdayStorageKeys.BIRTHDAY_GENERAL_TIPS_SEEN

    def isGeneralTipCompleted(self):
        return getSettings(BirthdayStorageKeys.BIRTHDAY_GENERAL_TIPS_SEEN)

    def isTabTipsCompleted(self, tabId=None):
        accountSettingsPath = self.getAccountSettingsTipPathByTabId(tabId)
        return getSettings(accountSettingsPath) if accountSettingsPath else True

    def __pushBirthdayMessage(self, message):
        SystemMessages.pushMessage(text=backport.text(message.keyText), priority=message.priority, type=message.type, messageData={'header': backport.text(R.strings.mt_birthday.notification.header())})

    def __onQuestsUpdated(self, *args):
        self.onQuestsUpdated()

    def __addWidgetHandler(self):
        self.__hangarWidgetAlias = GFWidgetAliases(flashLinkage=HANGAR_ALIASES.GF_HEADER_WIDGET, registerAlias=HANGAR_ALIASES.BIRTHDAY_HEADER_ENTRY_POINT)
        HangarHeader.addExternalWidgetHandler(self.__hangarWidgetAlias, self.__widgetHandler)

    def __widgetHandler(self, _):
        return not self.isDisabled() and self.isValidBattleType() and not self.__tankAcademyController.isActive()

    def __removeWidgetHandler(self):
        HangarHeader.removeExternalWidgetHandler(self.__hangarWidgetAlias)
        self.__hangarWidgetAlias = None
        return
