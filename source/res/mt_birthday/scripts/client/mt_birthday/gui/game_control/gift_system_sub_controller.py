# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/gift_system_sub_controller.py
import logging
import typing
from Event import EventManager, Event
from gui.gift_system.constants import GifterResponseState, HubUpdateReason
from gui.gift_system.wrappers import SendGiftResponse, IncomeSysMessage, GiftsHistoryData
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.view_helpers.UsersInfoHelper import BatchUsersInfoHelper
from lootboxes_common import makeLootboxTokenID
from mt_birthday.birthday_constants import BIRTHDAY_2025_STAMP_CODE, BIRTHDAY_2025_STAMP_CODE_SPECIAL, BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG
from mt_birthday.gui.birthday_helpers import getLootBoxByID
from mt_birthday.gui.gift_system.constants import GiftEventID
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import getServerUTCTime
from adisp import adisp_process
from mt_birthday.gui.impl.lobby.birthday.birthday_rewards_view import BirthdayRewardsViewWindow
from shared_utils import first
from skeletons.gui.game_control import IGiftSystemController
from mt_birthday.skeletons.sub_controllers import IGiftSystemSubController
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Optional, Set, Any, Dict, List
    from gui.shared.gui_items.loot_box import LootBox
_logger = logging.getLogger(__name__)
_LIMIT_GIFTS = 0
_ALLOWED_BLOGGERS_GIFT_COUNT = 1

def checkHubExistence(func):

    def wrapper(self, *args, **kwargs):
        return None if not self._giftEventHub else func(self, *args, **kwargs)

    return wrapper


class GiftSystemSubController(IGiftSystemSubController):
    __giftController = dependency.descriptor(IGiftSystemController)
    __giftEventID = GiftEventID.BIRTHDAY_2025
    __itemsCache = dependency.descriptor(IItemsCache)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._giftEventHub = None
        self._eventManager = EventManager()
        self.updateStampBalance = Event(self._eventManager)
        self.onOutcomeGift = Event(self._eventManager)
        self.onLimitReset = Event(self._eventManager)
        self.__userInfoHelper = BatchUsersInfoHelper()
        self.__bloggersData = []
        self.__callbackDelayer = CallbackDelayer()
        return

    def start(self):
        self.__giftController.onEventHubsCreated += self.__onEventHubsCreated
        self.__giftController.onEventHubsDestroyed += self.__onEventHubsDestroyed
        self.__addEventHub()

    def stop(self):
        self.__removeEventHub()
        self.__giftController.onEventHubsCreated -= self.__onEventHubsCreated
        self.__giftController.onEventHubsDestroyed -= self.__onEventHubsDestroyed
        self._eventManager.clear()
        self.__callbackDelayer.destroy()

    def __sendRewardWindow(self, fullName, lootbox, messageID, spaID=None, isNameLoading=None):
        lootboxToken = makeLootboxTokenID(lootbox.getID())
        bonuses = getNonQuestBonuses('tokens', {lootboxToken: self.getRewardDataFromLootbox(lootbox)})
        window = BirthdayRewardsViewWindow(bonuses, fullName, 0, isFinalReward=False, phraseID=messageID, spaID=spaID, isNameLoading=isNameLoading)
        self._notificationMgr.append(WindowNotificationCommand(window))

    def getRewardDataFromLootbox(self, lootbox):
        return {'id': makeLootboxTokenID(lootbox.getID()),
         'expires': {'at': self.__itemsCache.items.tokens.getTokenExpiryTime(makeLootboxTokenID(lootbox.getID()))},
         'count': _ALLOWED_BLOGGERS_GIFT_COUNT,
         'limit': _LIMIT_GIFTS}

    def isGiftEventActive(self):
        return self._giftEventHub and self._giftEventHub.getSettings().isEnabled

    def __addEventHub(self):
        self._giftEventHub = self.__giftController.getEventHub(self.__giftEventID)
        if self._giftEventHub is not None:
            self._giftEventHub.onHubUpdated += self.__onHubUpdated
        return

    def __removeEventHub(self):
        if self._giftEventHub is not None:
            self._giftEventHub.onHubUpdated -= self.__onHubUpdated
            self._giftEventHub = None
        return

    def __onEventHubsCreated(self, hubsToCreate):
        if self.__giftEventID in hubsToCreate:
            self.__addEventHub()

    def __onEventHubsDestroyed(self, hubsToDestroyed):
        if self.__giftEventID in hubsToDestroyed:
            self.__removeEventHub()

    def __onHubUpdated(self, reason, *args):
        if reason == HubUpdateReason.STAMPER_UPDATE:
            self.updateStampBalance()
        elif reason == HubUpdateReason.HISTORY:
            self.__processHistory(*args)
        elif reason == HubUpdateReason.INCOME_GIFT:
            self.__processIncomeGift(*args)
        elif reason == HubUpdateReason.OUTCOME_GIFT:
            self.onOutcomeGift(*args)
        elif reason == HubUpdateReason.WEB_STATE:
            self.__updateWebState()

    def __updateWebState(self):
        if self.getLimitResetTime():
            self.__callbackDelayer.delayCallback(self.getLimitResetTime() - getServerUTCTime(), self.__onLimitReset)

    def __onLimitReset(self):
        if self._giftEventHub:
            self._giftEventHub.getKeeper().updateExpireTime()
            self.__updateWebState()
            self.onLimitReset()

    def __processIncomeGift(self, event, *args):
        _logger.info('Start process income gifts event: %s args: %r', event, args)
        if not isinstance(event, IncomeSysMessage):
            return
        isNameLoading = False
        bloggerFullName = ''
        lootbox = getLootBoxByID(event.giftItemID)
        if lootbox:
            if not lootbox.isTagExist(BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG):
                return
            name = self.__userInfoHelper.getUserName(event.senderID, withEmptyName=True)
            if not name:
                _logger.info('Name is lost, need to sync')
                isNameLoading = True
            else:
                _logger.info('Name is not lost, show reward window name: %s', name)
                clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(event.senderID)
                bloggerFullName = self.__lobbyContext.getPlayerFullName(name, clanAbbrev=clanAbbrev)
            self.__sendRewardWindow(bloggerFullName, lootbox, event.meta['message_id'], spaID=event.senderID, isNameLoading=isNameLoading)

    def __processHistory(self, giftsInfo, *args, **kwargs):
        if not isinstance(giftsInfo, GiftsHistoryData):
            return
        isNameLoading = False
        for detail in giftsInfo.detailed:
            for lootboxID, meta in detail.iteritems():
                bloggerFullName = ''
                lootbox = getLootBoxByID(lootboxID)
                if lootbox:
                    if not lootbox.isTagExist(BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG):
                        continue
                    name = self.__userInfoHelper.getUserName(meta['senderID'], withEmptyName=True)
                    if not name:
                        isNameLoading = True
                    else:
                        clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(meta['senderID'])
                        bloggerFullName = self.__lobbyContext.getPlayerFullName(name, clanAbbrev=clanAbbrev)
                    self.__sendRewardWindow(bloggerFullName, lootbox, meta['messageID'], spaID=meta['senderID'], isNameLoading=isNameLoading)

    @checkHubExistence
    def getStampCount(self, stampName):
        return self._giftEventHub.getStamper().getStampCount(stampName)

    def getSimpleStampCount(self):
        return self.getStampCount(BIRTHDAY_2025_STAMP_CODE)

    def getSpecialStampCount(self):
        return self.getStampCount(BIRTHDAY_2025_STAMP_CODE_SPECIAL)

    @checkHubExistence
    def getExpirationTime(self):
        return self._giftEventHub.getKeeper().getExpirationTime()

    @checkHubExistence
    def getMagicPercent(self):
        return self._giftEventHub.getKeeper().getMagicPercent()

    @checkHubExistence
    def getAllowMultipleSendCount(self):
        return self._giftEventHub.getKeeper().getAllowMultipleSendCount()

    @checkHubExistence
    def getLimitResetTime(self):
        return self._giftEventHub.getKeeper().getExpireTime()

    @checkHubExistence
    def isAlreadyReceivedGift(self, playerID):
        return self._giftEventHub.getKeeper().isAlreadyReceivedGift(playerID)

    @checkHubExistence
    def getKeeper(self):
        return self._giftEventHub.getKeeper()

    @checkHubExistence
    def getGifter(self):
        return self._giftEventHub.getGifter()

    @checkHubExistence
    def getStamper(self):
        return self._giftEventHub.getStamper()

    @checkHubExistence
    def getMessenger(self):
        return self._giftEventHub.getMessenger()

    @adisp_process
    @checkHubExistence
    def sendGifts(self, stampType, receiversIDs, messageIdx, callback=None):
        metaInfo = {'message_id': messageIdx}
        allowMultipleSendCount = self.getAllowMultipleSendCount() or 1
        if allowMultipleSendCount < len(receiversIDs):
            result = SendGiftResponse(state=GifterResponseState.GIFT_SYSTEM_LIMIT_REACHED, receiverIDs=receiversIDs, outCount=None, entitlementCode=stampType, declinedReceivers=[], meta=metaInfo, description='The number of receivers in the request is higher than the limit value.', statusCode=409, executionTime=0)
        elif allowMultipleSendCount > 1:
            result = yield self.getGifter().sendGiftMultiple(stampType, list(receiversIDs), metaInfo)
        else:
            result = yield self.getGifter().sendGift(stampType, first(receiversIDs), metaInfo)
        self.__processCallback(result)
        if callback:
            callback(result)
        return

    def __processCallback(self, result):
        if result.state is GifterResponseState.WEB_SUCCESS:
            for receiverID in set(result.receiverIDs).difference(result.declinedReceivers):
                self.getKeeper().updateSentGiftState(receiverID)
