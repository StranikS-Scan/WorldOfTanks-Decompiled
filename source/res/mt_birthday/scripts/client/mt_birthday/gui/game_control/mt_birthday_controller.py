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
from gui.battle_results import templates
from gui.battle_results.components import base
from gui.prb_control import prbDispatcherProperty
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.postbattle_extra_tab.postbattle_extra_tab import PostbattleExtraTab
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
from mt_birthday.gui.birthday_helpers import addExtraPostBattleTab, deleteExtraTab, getLootBoxByID
from mt_birthday.gui.game_control.progression_sub_controller import TanksBirthdayProgressionSubController
from mt_birthday.gui.game_control.gift_system_sub_controller import GiftSystemSubController
from mt_birthday.gui.impl.lobby.birthday.post_battle_mail_view import PostBattleMailView
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController, ILastBattlesPlayersController
from mt_birthday.birthday_constants import BIRTHDAY_2025_BLOGGER_TOKEN, BIRTHDAY_2025_STAMP_CODE, BIRTHDAY_2025_STAMP_CODE_SPECIAL, BIRTHDAY_2025_GOLDEN_TICKET, MT_BIRTHDAY_EVENT_STATE, BirthdayStorageKeys, BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG, POST_BATTLE_EXTRA_TAB_UI
from mt_birthday.birthday_account_settings import getSettings, setSettings
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEventsNotificationsController, IGuiLootBoxesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from wg_async import wg_async
from BWUtil import AsyncReturn
if typing.TYPE_CHECKING:
    from gui.game_control.events_notifications import EventNotification
    from typing import Optional
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


class TanksBirthdayController(ITanksBirthdayController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lastBattlesPlayers = dependency.descriptor(ILastBattlesPlayersController)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiController = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self):
        super(TanksBirthdayController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEventSettingsUpdated = Event.Event(self.__eManager)
        self.onNewGiftsReceived = Event.Event(self.__eManager)
        self.onLootboxSeen = Event.Event(self.__eManager)
        self.__eventState = None
        self.__endDate = None
        self.__startDate = None
        self.__bannedPlayersIDs = set()
        self.__progression = TanksBirthdayProgressionSubController(self.__eManager)
        self.__giftSystem = GiftSystemSubController()
        self.__userInfoHelper = BatchUsersInfoHelper()
        self.__bloggerGiftArenas = set()
        self.__unseenGifts = {}
        self.__giftNotificationSeenCount = 0
        self.__callbackDelayer = CallbackDelayer()
        return

    def fini(self):
        self.__stop()

    def onDisconnected(self):
        self.__giftNotificationSeenCount = 0
        self.__unseenGifts.clear()
        self.__stop()

    def onConnected(self):
        self.__bannedPlayersIDs = set()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def __stop(self):
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
        return bool(self.__itemsCache.items.tokens.getToken(BIRTHDAY_2025_BLOGGER_TOKEN) or self.getSpecialStampCount())

    def getStartTime(self):
        return self.__startDate

    def getExpiryTime(self):
        return self.__endDate

    def onLobbyInited(self, event):
        self.__processAction()
        self.__notificationsCtrl.onEventNotificationsChanged += self.__processAction
        self.__progression.start()
        self.__giftSystem.start()
        self.__guiController.onStorageVisited += self.__onLootBoxStorageVisited

    def __registerPostBattleTab(self):
        if self.isEnabled():
            if not PostbattleExtraTab.hasInjectionView():
                self.updatePostBattleExtraTab(addExtraPostBattleTab)
                PostbattleExtraTab.overrideInjectionView(PostBattleMailView)
        elif PostbattleExtraTab.isInjectionView(PostBattleMailView):
            self.updatePostBattleExtraTab(deleteExtraTab)
            PostbattleExtraTab.deleteInjectionView()

    def updatePostBattleExtraTab(self, updateMethod):
        for composer in self.__battleResults.composers.values():
            if hasattr(composer, 'getTabs'):
                tabsBlock = composer.getTabs()
                if tabsBlock is None:
                    continue
                if tabsBlock.getMeta() is None:
                    continue
                for tab in tabsBlock.getMeta()._meta:
                    if tab.get('viewId') == POST_BATTLE_EXTRA_TAB_UI:
                        updateMethod(tabsBlock)

        updateMethod(templates.RANDOM_TABS_BLOCK)
        return

    def isRandomArenaGuiType(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.RANDOMS) if self.prbDispatcher is not None else False

    def onAccountBecomeNonPlayer(self):
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__processAction

    @wg_async
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

    def getGoldenTicketsCount(self):
        return self.__itemsCache.items.stats.entitlements.get(BIRTHDAY_2025_GOLDEN_TICKET, 0)

    def getMaxSelectedPlayers(self):
        return self.__giftSystem.getAllowMultipleSendCount()

    def getSpecialStampCount(self):
        return self.__giftSystem.getSpecialStampCount()

    def getCooldownGiftTime(self):
        return getTimestampFromLocal(utcToLocalDatetime(getDateTimeInLocal(self.__giftSystem.getExpirationTime())).timetuple())

    def getLocalEndDate(self):
        return getTimestampFromLocal(getDateTimeInLocal(self.getExpiryTime()).timetuple())

    @staticmethod
    def getRandomPhraseID(currPhraseID=None):
        phrasesKeys = R.strings.player_phrases.player.keys()
        if currPhraseID is not None:
            phrases = [ x for x in phrasesKeys if x.split('_')[-1] != currPhraseID ]
        else:
            phrases = [ x for x in phrasesKeys ]
        chosenPhrase = random.choice(phrases)
        return int(chosenPhrase.split('_')[-1])

    @staticmethod
    def getRandomBloggerPhraseID(currPhraseID=None):
        phrasesKeys = R.strings.player_phrases.blogger.keys()
        if currPhraseID is not None:
            phrases = [ x for x in phrasesKeys if x.split('_')[-1] != currPhraseID ]
        else:
            phrases = [ x for x in phrasesKeys ]
        chosenPhrase = random.choice(phrases)
        return int(chosenPhrase.split('_')[-1])

    def isFirstBloggerAfterBattleGift(self, arenaUniqueID):
        return arenaUniqueID not in self.__bloggerGiftArenas and self.isBlogger()

    def onBloggerGiftSent(self, arenaUniqueID):
        self.__bloggerGiftArenas.add(arenaUniqueID)

    def getStampForSending(self, arenaUniqueID):
        return BIRTHDAY_2025_STAMP_CODE_SPECIAL if self.isBlogger() and self.getSpecialStampCount() and self.isFirstBloggerAfterBattleGift(arenaUniqueID) else BIRTHDAY_2025_STAMP_CODE

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

    def getMaxProgressionLevel(self):
        return len(self.__progression.getSimpleLevels())

    def getUnseenGiftsCount(self):
        return sum((v for k, v in self.__unseenGifts.iteritems() if not k[1]))

    def getUnseenGiftId(self):
        return first((k[0] for k in self.__unseenGifts if not k[1]))

    def pushNewGiftReceived(self, giftId, count):
        if self.isEnabled():
            lootbox = getLootBoxByID(giftId)
            isSpecialGift = lootbox is not None and lootbox.isTagExist(BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG)
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
        self.__registerPostBattleTab()
        self.onEventSettingsUpdated()

    def __onEndDate(self):
        self.__registerPostBattleTab()
        self.__updateHangarHeaderEnabled()

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

    def __pushBirthdayMessage(self, message):
        SystemMessages.pushMessage(text=backport.text(message.keyText), priority=message.priority, type=message.type, messageData={'header': backport.text(R.strings.mt_birthday.notification.header())})
