# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
from copy import copy
import BigWorld
from gui import SystemMessages
from gui.server_events.bonuses import getMergedBonusesFromDicts, getLunarMergedBonusesFromDicts
from gui.gift_system.wrappers import OpenedGiftData
from gui.shared import g_eventBus
from gui.shared.events import GiftSystemOperationEvent
from lunar_ny import ILunarNYController
from lootboxes_common import makeLootboxID
from gui.shared.gui_items.processors import Processor, makeI18nError
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
from items.components.ny_constants import CurrentNYConstants
_logger = logging.getLogger(__name__)

class LootBoxOpenProcessor(Processor):
    __systemMessages = dependency.descriptor(ISystemMessages)
    __nyController = dependency.descriptor(INewYearController)
    __lunarNyController = dependency.descriptor(ILunarNYController)

    def __init__(self, lootBoxItem, count=1, senderID=-1):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count
        self.__senderID = senderID
        self.__prevCollectedToys = self.__nyController.getAllCollectedToysId()

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'lootboxes/open/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        bonus = ctx['bonus']
        if self.__isLunarBonus(bonus):
            fmt = QuestAchievesFormatter.formatQuestAchieves(getLunarMergedBonusesFromDicts(bonus), False)
        else:
            bonuses = getMergedBonusesFromDicts(ctx['bonus'])
            ctx['giftsInfo'] = [ OpenedGiftData(*item) for item in ctx.get('giftsInfo', []) ]
            fmt = QuestAchievesFormatter.formatQuestAchieves(bonuses, False)
        if fmt is not None:
            if ctx['giftsInfo'] and not self.__isLunarBonus(bonus):
                eventCtx = {'lootbox': self.__lootBox,
                 'giftsInfo': copy(ctx['giftsInfo']),
                 'fmtBonuses': fmt}
                g_eventBus.handleEvent(GiftSystemOperationEvent(GiftSystemOperationEvent.GIFT_OPENED, ctx=eventCtx))
            else:
                SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        for bonuses in ctx['bonus']:
            nyToys = bonuses.get(CurrentNYConstants.TOYS)
            if nyToys is None:
                continue
            for toyId, toyData in nyToys.iteritems():
                toyData['newCount'] = 0 if toyId in self.__prevCollectedToys else 1
                self.__prevCollectedToys.add(toyId)

        if ctx is not None and 'giftsInfo' in ctx:
            self.__preRequestNickName(ctx['giftsInfo'])
        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d, senderID: %d', self.__lootBox, self.__count, self.__senderID)
        if self.__senderID != -1:
            BigWorld.player().tokens.openLootBoxBySender(self.__lootBox.getID(), int(self.__count), int(self.__senderID), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
        else:
            BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), int(self.__count), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def __preRequestNickName(self, giftsInfo):
        userInfoHelper = UsersInfoHelper()
        hasInvalidName = False
        for senderID, _ in giftsInfo:
            senderName = userInfoHelper.getUserName(senderID, withEmptyName=True)
            hasInvalidName = hasInvalidName or not senderName

        if hasInvalidName and userInfoHelper.proto.isConnected():
            userInfoHelper.syncUsersInfo()

    def __isLunarBonus(self, bonus):
        result = False
        if bonus:
            tokens = bonus[0].get('tokens')
            if tokens:
                firstToken = tokens.keys()[0]
                tokenID = makeLootboxID(firstToken)
                result = self.__lunarNyController.receivedEnvelopes.getEnvelopeTypeByLootBoxID(tokenID) is not None
        return result
