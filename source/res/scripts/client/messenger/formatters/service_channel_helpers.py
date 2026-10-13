# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel_helpers.py
import typing
import logging
from collections import namedtuple
from Queue import Queue
from adisp import adisp_async
from gui.collection.collections_constants import COLLECTION_ITEM_PREFIX_NAME
from gui.server_events.bonuses import BattleTokensBonus
from items import makeIntCompactDescrByID
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.shared import IItemsCache
from items.components.c11n_constants import CustomizationNamesToTypes
from helpers import dependency
from messenger import g_settings
_logger = logging.getLogger(__name__)
EOL = '\n'
DEFAULT_MESSAGE = 'defaultMessage'
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
MessageData = namedtuple('MessageData', 'data, settings')

class AsyncStateWaiter(object):

    def __init__(self, checkFunc, event):
        self.__checkFunc = checkFunc
        self.__event = event
        self.__callbackQueue = None
        return

    @adisp_async
    def waitFor(self, callback):
        if self.__isReady():
            callback(True)
        else:
            self.__registerHandler(callback)

    def __isReady(self):
        return self.__checkFunc()

    def __registerHandler(self, callback):
        needSubscribe = self.__callbackQueue is None
        if needSubscribe:
            self.__callbackQueue = Queue()
        if self.__isReady():
            if needSubscribe:
                self.__callbackQueue = None
            callback(True)
            return
        else:
            self.__callbackQueue.put(callback)
            if needSubscribe:
                self.__event += self.__onEventTriggered
            return

    def __onEventTriggered(self, *_, **__):
        if self.__callbackQueue is None:
            return
        else:
            while not self.__callbackQueue.empty():
                try:
                    self.__callbackQueue.get_nowait()(self.__isReady())
                except Exception:
                    _logger.exception('Exception in AsyncStateWaiter callback')

            self.__unregisterHandler()
            return

    def __unregisterHandler(self):
        if self.__callbackQueue is None:
            return
        else:
            if not self.__callbackQueue.empty():
                _logger.warning('AsyncStateWaiter pending callbacks')
            self.__callbackQueue = None
            self.__event -= self.__onEventTriggered
            return


def getRewardsForBoxes(message, boxIDs):
    data = message.data or {}
    resultRewards = {}
    for boxID in boxIDs:
        mergeRewards(resultRewards, data[boxID]['rewards'])

    return resultRewards


def getRewardsForQuests(message, questIDs):
    data = message.data or {}
    detailRewards = data.get('detailedRewards', {})
    resultRewards = {}
    for questID, rewards in detailRewards.items():
        if questID in questIDs:
            mergeRewards(resultRewards, rewards)

    return resultRewards


def mergeRewards(resultRewards, rewards):
    for bonusName, bonusValue in rewards.items():
        if bonusName in BONUS_MERGERS:
            BONUS_MERGERS[bonusName](resultRewards, bonusName, bonusValue, False, 1, None)
        if bonusName == 'selectableCrewbook':
            _mergeSelectableCrewbook(resultRewards, bonusName, bonusValue)
        _logger.warning('BONUS_MERGERS has not bonus %s', bonusName)

    return


def _mergeSelectableCrewbook(resultRewards, bonusName, bonusValue):
    selectablesTotal = resultRewards.setdefault(bonusName, {})
    for item in bonusValue:
        selectablesTotal[item['itemName']] = item['count']


def getCustomizationItem(itemId, customizationName):
    itemsCache = dependency.instance(IItemsCache)
    customizationType = CustomizationNamesToTypes.get(customizationName.upper())
    if customizationType is None:
        _logger.warning('Wrong customization name: %s', customizationName)
    compactDescr = makeIntCompactDescrByID('customizationItem', customizationType, itemId)
    return itemsCache.items.getItemByCD(compactDescr)


def getCustomizationItemData(itemId, customizationName):
    item = getCustomizationItem(itemId, customizationName)
    itemName = item.userName
    itemTypeName = item.itemFullTypeName
    return _CustomizationItemData(itemTypeName, itemName)


_CustomizationItemData = namedtuple('_CustomizationItemData', ('guiItemType', 'userName'))

def getDefaultMessage(normal='', bold=''):
    return g_settings.msgTemplates.format(DEFAULT_MESSAGE, {'normal': normal,
     'bold': bold})


def popCollectionEntitlements(rewards):
    entitlements = {name:data for name, data in rewards['entitlements'].iteritems() if name.startswith(COLLECTION_ITEM_PREFIX_NAME)} if 'entitlements' in rewards else {}
    for eName in entitlements.iterkeys():
        rewards['entitlements'].pop(eName)

    return entitlements


def parseTokenBonusCount(bonus, tokenName):
    return bonus.getValue().get(tokenName, {}).get('count', 0) if isinstance(bonus, BattleTokensBonus) else 0
