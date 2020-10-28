# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/shop.py
import logging
import enum
import BigWorld
from adisp import async
from Event import EventManager, Event
from gui import SystemMessages
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import mergeBonuses
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from gui.server_events.game_event.commander_event_progress import BONUS_TANKMAN_TOKEN
from shared_utils import first
from skeletons.gui.game_control import IEventTokenController
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError
from gui.shared.utils import decorators
from gui.server_events.conditions import getTokenNeededCountInCondition
from constants import HE19_MONEY_TOKEN_ID, EventPackType
from gui.shared.money import Money
_HE19_SHOP_BEST_DEAL_GROUP_QUESTS = 'he19_shop_items_best_deal'
_BONUS_BATTLETOKEN = 'battleToken'
_BONUS_CUSTOMIZATIONS = 'customizations'

class ShopItems(enum.Enum):
    Styles = 'he20_shop_items_style'
    Boosters = 'he20_shop_items_battleBoosters'
    Goodies = 'he20_shop_items_goodies'
    CrewBooks = 'he20_shop_items_crewBooks'


_logger = logging.getLogger(__name__)

class Shop(object):
    eventsCache = dependency.descriptor(IEventsCache)
    eventToken = dependency.descriptor(IEventTokenController)

    def __init__(self):
        self._em = EventManager()
        self.onShopUpdated = Event(self._em)
        self._itemsCache = {}
        self._packsCache = {}

    def start(self):
        self.updateCache()
        self.eventToken.onShopItemUpdated += self.updateCache
        self.eventToken.onEventMoneyUpdated += self.updateCache

    def stop(self):
        self._em.clear()
        self.eventToken.onShopItemUpdated -= self.updateCache
        self.eventToken.onEventMoneyUpdated -= self.updateCache

    def updateCache(self):
        self._itemsCache = {}
        self._packsCache = {}
        self._itemsCache = {itemType.value:self.__makeShopItems(itemType) for itemType in ShopItems}
        self._packsCache = {info['id']:self.__makePackItem(info) for info in self.getBestDealsData()}
        self.onShopUpdated()

    @property
    def shopData(self):
        return self._getShopData()

    @property
    def allSimpleItems(self):
        return self._itemsCache

    @property
    def packItems(self):
        return self._packsCache

    def getStyleItems(self):
        return self.getSimpleItemsByType(ShopItems.Styles.value)

    def getSimpleItemsByType(self, itemTypeValue):
        return self._itemsCache.get(itemTypeValue)

    def getPackItemByType(self, itemType):
        return self._packsCache.get(itemType)

    def getSimpleItemByQuestId(self, questId):
        for groupItems in self._itemsCache.itervalues():
            for item in groupItems:
                if item.getID() == questId:
                    return item

    def getSimpleItemByTypeAndIndex(self, itemType, itemIndex):
        simpleItems = self.getSimpleItemsByType(itemType)
        if simpleItems is not None and itemIndex < len(simpleItems):
            return simpleItems[itemIndex]
        else:
            logging.warning("Can't get item by context.")
            return

    def isEnabled(self):
        return self._getShopData().get('enabled', False)

    def getCoins(self):
        return self.eventsCache.questsProgress.getTokenCount(HE19_MONEY_TOKEN_ID)

    def getBestDealsData(self):
        return self._getShopData().get('bestDeals', {})

    def getStylesForRandom(self):
        return self._getShopData().get('stylesForRandom', {})

    def getStylesForRandomBundle(self):
        return self._getShopData().get('stylesForRandomBundle', {})

    def isRandomStylesSellingAvailable(self):
        return self._getShopData().get('enabledRandomStylesSelling', False)

    def _getShopData(self):
        return self.eventsCache.getGameEventData().get('shop', {})

    def __makeShopItems(self, itemType):
        return sorted([ ShopItem(quest) for quest in self.eventsCache.getHiddenQuests(lambda q: q.getGroupID() == itemType.value).itervalues() ], key=lambda i: i.getID())

    def __makePackItem(self, info):
        quest = first(self.eventsCache.getHiddenQuests(lambda q: q.getID() == info['questID']).itervalues())
        bonusQuests = [ bonusQuest for bonusQuest in self.eventsCache.getHiddenQuests(lambda bq: bq.getGroupID() == info['bonusGroupId'] and getTokenNeededCountInCondition(bq, info['token'], 0) != 0).itervalues() ]
        return PackItem(quest, info, bonusQuests)


class BaseItem(object):

    def __init__(self, quest, *args, **kwargs):
        self._quest = quest
        self._bonuses = None
        self._price = None
        self._currency = None
        if not quest:
            logging.warning("Dyn updater hasn't been run yet.")
            return
        else:
            self.init(*args, **kwargs)
            return

    def init(self, *args, **kwargs):
        raise NotImplementedError

    def buy(self, callback, count=1):
        raise NotImplementedError

    @property
    def price(self):
        return self._price

    @property
    def currency(self):
        return self._currency

    @property
    def quest(self):
        return self._quest

    def getBonusCount(self):
        return self._quest.bonusCond.getBonusLimit() - self._quest.getBonusCount()

    def getBonuses(self):
        return self._bonuses

    def getID(self):
        return self._quest.getID()

    def getBonusByType(self, bonusType):
        return next((bonus for bonus in self._bonuses if bonus.getName() == bonusType), None)

    def canBuy(self):
        return not self._quest.isCompleted()


class ShopItem(BaseItem):

    def init(self, *args, **kwargs):
        self._bonuses = self._quest.getBonuses()
        self._price = getTokenNeededCountInCondition(self._quest, HE19_MONEY_TOKEN_ID)
        self._currency = HE19_MONEY_TOKEN_ID

    def getTankmanBonus(self):
        return self.getBonusByType(BONUS_TANKMAN_TOKEN)

    def getTankmanBonusTokenID(self):
        tankmanBonus = self.getTankmanBonus()
        return None if tankmanBonus is None else next(tankmanBonus.getTokens().iterkeys(), None)

    def getTokenBonus(self):
        return self.getBonusByType(_BONUS_BATTLETOKEN)

    def getCustomizationsBonus(self):
        return self.getBonusByType(_BONUS_CUSTOMIZATIONS)

    @async
    @decorators.process('updating')
    def buy(self, callback, count=1):
        result = yield ShopItemBuyer(self.getID(), self.price * count, count).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result)


class PackItem(BaseItem):
    _HUNDRED_PERCENT = 100

    def __init__(self, quest, packsInfo, bonusQuests):
        self._id = None
        self._bonusQuests = None
        self._token = None
        self._bonusGroupId = None
        self._oldPrice = None
        self._discount = None
        self._extraBonuses = []
        super(PackItem, self).__init__(quest, packsInfo, bonusQuests)
        return

    def init(self, packInfo, bonusQuests):
        self._id = packInfo['id']
        self._price = packInfo['price']
        self._oldPrice = packInfo['oldPrice']
        self._currency = packInfo['currency']
        self._token = packInfo['token']
        self._bonusGroupId = packInfo['bonusGroupId']
        self._discount = int(round((1 - float(self._price) / self._oldPrice) * self._HUNDRED_PERCENT))
        self._bonusQuests = bonusQuests
        self._buildBonuses()

    @property
    def packID(self):
        return self._id

    @property
    def token(self):
        return self._token

    @property
    def bonusGroupId(self):
        return self._bonusGroupId

    @property
    def oldPrice(self):
        return self._oldPrice

    @property
    def discount(self):
        return self._discount

    @property
    def extraBonuses(self):
        return self._extraBonuses

    def getExtraBonusCount(self):
        if self.packID == EventPackType.ITEM.value:
            count = sum((bq.bonusCond.getBonusLimit() for bq in self._bonusQuests)) if self._bonusQuests else 0
        elif self.packID == EventPackType.PLAYER.value:
            count = 0
            extraBonus = first(self.extraBonuses)
            if extraBonus.getName() == 'battleToken':
                for tokenName, tokenData in extraBonus.getValue().iteritems():
                    count += tokenData['count'] if tokenName.startswith('img:') else 0

        else:
            count = len(self.extraBonuses)
        return count

    @async
    @decorators.process('updating')
    def buy(self, callback):
        result = yield BestDealBuyer(self.packID, self.currency, self.price).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result)

    def _buildBonuses(self):
        self._bonuses = mergeBonuses(self._quest.getBonuses())
        for quest in self._bonusQuests:
            self._extraBonuses.extend(quest.getBonuses())

        self._extraBonuses = mergeBonuses(self._extraBonuses)


class BestDealBuyer(Processor):

    def __init__(self, packID, currency, money):
        ctx = {'goldCost': text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(money)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))}
        super(BestDealBuyer, self).__init__(plugins=(plugins.MessageConfirmator(backport.text(R.strings.event.shop.bestDealConfirmation.num(packID)()), isEnabled=True, ctx=ctx), plugins.MoneyValidator(Money(**{currency: money}))))
        self._packID = packID

    def _request(self, callback):
        BigWorld.player().buyBestDealBandle(self._packID, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_bestdeal/{}'.format(errStr), defaultSysMsgKey='hw19/server_error')


class ShopItemBuyer(Processor):

    def __init__(self, itemID, money, count=1):
        super(ShopItemBuyer, self).__init__(plugins=(plugins.TokenValidator(HE19_MONEY_TOKEN_ID, money),))
        self._money = money
        self._itemID = itemID
        self._count = count

    def _request(self, callback):
        BigWorld.player().buyHalloweenShopItem(self._count, self._itemID, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19/{}'.format(errStr), defaultSysMsgKey='hw19/server_error')
