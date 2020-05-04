# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/shop.py
import logging
import re
import BigWorld
from Event import EventManager, Event
from shared_utils import first
from gui.SystemMessages import SM_TYPE
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.utils import decorators
from gui import SystemMessages
from constants import EventPackTypes, GENERAL_ENERGY_MULTIPLIER_PATTERN, MULTIPLIER_GROUP, EventPackGuiTypes
from gui.shared.money import Money
from gui.impl.gen import R
from gui.impl import backport
_BONUS_BATTLETOKEN = 'battleToken'
_BONUS_CUSTOMIZATIONS = 'customizations'
ENERGY_TOKEN_PREFIX = 'img:se20_energy_general'
ENERGY_DISCOUNT_TOKEN = 'img:se20_energy_general_x15_discount:webId'
_logger = logging.getLogger(__name__)

class Shop(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self._em = EventManager()
        self.onShopUpdated = Event(self._em)
        self._items = None
        return

    def start(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted

    def isEnabled(self):
        return self._getShopData().get('enabled', False)

    def getExchangeTokenCount(self):
        return self.eventsCache.questsProgress.getTokenCount(ENERGY_DISCOUNT_TOKEN)

    def getPacksByGuiType(self, guiType):
        return [ item for item in self.items.itervalues() if item.packGuiType == guiType ]

    def getMegaPack(self):
        return first(self.getPacksByGuiType(EventPackGuiTypes.MEGA_PACK.value))

    def getExchangePackOfGeneral(self, generalID):
        packs = self.getPacksByGuiType(EventPackGuiTypes.EXCHANGE.value)
        return first((pack for pack in packs if isinstance(pack, GeneralItemMixin) and pack.generalID == generalID), None)

    @property
    def items(self):
        if self._items is None:
            _logger.warning('Shop items was not built yet')
            self._buildItems()
        return self._items

    def getItem(self, packID):
        return self.items.get(packID)

    def getPacksByType(self, packType):
        if packType not in EventPackTypes.values():
            _logger.warning('Wrong requested type of packs, must be in EventPackTypes, found %s', packType)
        return [ item for item in self.items.itervalues() if item.packType == packType ]

    def getPacksData(self):
        return self._getShopData().get('packs', {})

    def canBuy(self, packID):
        pack = self.getItem(packID)
        return pack.canBuy if pack else False

    @decorators.process('updating')
    def buy(self, packID, sucSysMsg=None, errSysMsg=None):
        pack = self.getItem(packID)
        currency, amount = pack.getPrice()
        if currency is None or amount is None or not self.canBuy(packID) or not pack.isBuyForCurrencyEnabled and amount != 0:
            return
        else:
            result = yield ShopItemBuyer(packID, sucSysMsg=sucSysMsg, errSysMsg=errSysMsg, *pack.getPrice()).request()
            if result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            self.onShopUpdated()
            return

    def _getShopData(self):
        return self.eventsCache.getGameEventData().get('shop', {})

    def _buildItems(self):
        hiddenQuests = self.eventsCache.getHiddenQuests().values()
        packs = (_createShopObject(packID, packInfo, hiddenQuests) for packID, packInfo in self.getPacksData().iteritems())
        self._items = {pack.packID:pack for pack in packs if pack.canBuy}
        _logger.info('Built shop items %s', self._items)

    def _delBoughtItem(self, packID):
        if packID in self._items:
            del self._items[packID]
            _logger.info('Deleted shop item %s', packID)

    def _onSyncCompleted(self):
        self._buildItems()


class ShopItem(object):
    _HUNDRED_PERCENT = 100
    _SINGLE_REWARD_COUNT = 1
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, packID, packInfo, packType):
        self._id = packID
        self._info = packInfo
        self._packType = packType
        self._quest = None
        _logger.debug('Created shop item id = %s, type %s', self._id, self._packType)
        return

    def init(self, hiddenQuests):
        quests = [ q for q in hiddenQuests if q.getID().startswith(self._id) ]
        if len(quests) != 1:
            _logger.warning("There must be one to one correspondence of a pack token '%s' and its bonus quest %s", self._id, quests)
            return
        self._quest = first(quests)

    @property
    def packID(self):
        return self._id

    def getQuest(self):
        return self._quest

    @property
    def canBuy(self):
        return False if self._quest is None else not self._quest.isCompleted() and self._quest.isAvailable().isValid

    @property
    def info(self):
        return self._info

    @property
    def packType(self):
        return self._packType

    @property
    def packGuiType(self):
        return self._info.get('guiType')

    @property
    def hasSingleReward(self):
        return len(self.getBonuses()) == self._SINGLE_REWARD_COUNT

    @property
    def isBuyForCurrencyEnabled(self):
        return self._info.get('currencyBuyEnabled', True)

    def getQuestID(self):
        return self._quest.getID()

    def getFinishTime(self):
        return self._quest.getFinishTime()

    def getDiscountInfo(self):
        return self._info.get('discount', {})

    def getDiscountID(self):
        return self.getDiscountInfo().get('id')

    def getDiscountLifeTime(self):
        return self.eventsCache.questsProgress.getTokenExpiryTime(self.getDiscountID())

    def getDiscountTokenCount(self):
        tokenID = self.getDiscountInfo()['id']
        return self.eventsCache.questsProgress.getTokenCount(tokenID)

    def getPriceInTokens(self):
        discountInfo = self.getDiscountInfo()
        tokenID = discountInfo['id']
        amount = int(round(self._HUNDRED_PERCENT / float(discountInfo['percent'])))
        return (tokenID, amount)

    @property
    def isTokenShortage(self):
        tokenID, amount = self.getPriceInTokens()
        return self.eventsCache.questsProgress.getTokenCount(tokenID) < amount

    def hasRealDiscount(self):
        discountInfo = self.getDiscountInfo()
        return discountInfo and discountInfo['enabled']

    def getDefPrice(self):
        return (self._info['price']['currency'], self._info['price']['amount']) if self.hasRealDiscount() else (self._info['price']['currency'], self._info['price']['oldAmount'])

    def getPrice(self):
        amount = self._info['price']['amount']
        if self.hasRealDiscount():
            discountInfo = self.getDiscountInfo()
            tokenCount = self.getDiscountTokenCount()
            percent = min(float(tokenCount * discountInfo['percent']), self._HUNDRED_PERCENT)
            amount = int(round(amount * (1 - percent / self._HUNDRED_PERCENT)))
        return (self._info['price']['currency'], amount)

    def getDiscount(self):
        _, amount = self.getPrice()
        _, oldAmount = self.getDefPrice()
        percent = int(round((1 - amount / float(oldAmount)) * self._HUNDRED_PERCENT))
        return min(percent, self._HUNDRED_PERCENT)

    def getBonuses(self):
        return [] if not self._quest else self._quest.getBonuses()

    def getBonusByType(self, bonusType):
        return next((bonus for bonus in self.getBonuses() if bonus.getName() == bonusType), None)

    def getTokenBonus(self):
        return self.getBonusByType(_BONUS_BATTLETOKEN)

    def getCustomizationsBonus(self):
        return self.getBonusByType(_BONUS_CUSTOMIZATIONS)


class GeneralItemMixin(object):
    _GENERAL_ID_PATTERN = re.compile('general_(?P<generalID>[0-9]*)')

    def init(self):
        self._setGeneralID()

    def _setGeneralID(self):
        self._generalID = self._getParamFromID(self._GENERAL_ID_PATTERN, 'generalID')

    @property
    def generalID(self):
        return self._generalID

    def _getParamFromID(self, pattern, paramName):
        match = re.search(pattern, self.packID)
        if match is None:
            _logger.warning('Wrong format for buying general bundle pack: %s, must be general_(number)', self.packID)
            return
        else:
            return int(match.group(paramName))


class GeneralEnergyItem(ShopItem, GeneralItemMixin):

    def __init__(self, packID, packInfo, packType):
        super(GeneralEnergyItem, self).__init__(packID, packInfo, packType)
        self._token = None
        self._generalID = None
        return

    def init(self, hiddenQuests):
        super(GeneralEnergyItem, self).init(hiddenQuests)
        self._setGeneralID()
        self._setEnergyToken()

    @property
    def energyCount(self):
        return 0 if self._token is None else self._token.count

    @property
    def energyID(self):
        return 0 if self._token is None else self._token.id

    @property
    def energyModifier(self):
        return self._energyModifier

    def _setEnergyModifier(self):
        self._energyModifier = self._getParamFromID(GENERAL_ENERGY_MULTIPLIER_PATTERN, MULTIPLIER_GROUP)

    def _setEnergyToken(self):
        tokenBonus = self.getTokenBonus()
        tokenBonuses = self.getTokenBonus().getTokens() if tokenBonus else {}
        for tokenID, token in tokenBonuses.iteritems():
            if tokenID.startswith(ENERGY_TOKEN_PREFIX):
                self._token = token

        self._setEnergyModifier()


class GeneralProgressItem(ShopItem, GeneralItemMixin):
    _GENERAL_LEVEL_PATTERN = re.compile('level_(?P<level>[0-9]*)')
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, packID, packInfo, packType):
        super(GeneralProgressItem, self).__init__(packID, packInfo, packType)
        self._level = None
        return

    def init(self, hiddenQuests):
        super(GeneralProgressItem, self).init(hiddenQuests)
        self._setGeneralID()
        self._setLevel()

    @property
    def level(self):
        return self._level

    def getGeneralIDs(self):
        return [self.generalID]

    def _getProgressBonuses(self):
        general = self.gameEventController.getCommander(self.generalID)
        return [ bonus for quest in general.getUncompletedProgressItems() for bonus in quest.getBonuses() ]

    def _setLevel(self):
        if self.level is None:
            self._level = self._getParamFromID(self._GENERAL_LEVEL_PATTERN, 'level')
        return


class AllGeneralsProgressItem(GeneralProgressItem):
    _ALL_GENERALS_ID = -1

    def getGeneralIDs(self):
        return sorted(self.gameEventController.getCommanders().keys())

    def _setGeneralID(self):
        self._generalID = self._ALL_GENERALS_ID

    def _getProgressBonuses(self):
        generals = self.gameEventController.getCommanders().values()
        return [ bonus for general in generals for quest in general.getUncompletedProgressItems() for bonus in quest.getBonuses() ]


class ShopItemBuyer(Processor):
    _SUCCESS = 'se20_buy_pack/success'
    _ERROR = 'se20_buy_pack/{}'

    def __init__(self, itemID, currency, amount, sucSysMsg=None, errSysMsg=None):
        super(ShopItemBuyer, self).__init__(plugins=(plugins.MoneyValidator(Money(**{currency: amount})),))
        self._currency = currency
        self._amount = amount
        self._itemID = itemID
        self._successSysMsg = self._SUCCESS if sucSysMsg is None else sucSysMsg
        self._errorSysMsg = self._ERROR if errSysMsg is None else errSysMsg
        return

    def _request(self, callback):
        _logger.debug('Make server request to buy pack %s for: %s', self._itemID, self._amount)
        BigWorld.player().buyEventPack(self._itemID, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(self._errorSysMsg.format(errStr), defaultSysMsgKey='se20/server_error')

    def _successHandler(self, code, ctx=None):
        return super(ShopItemBuyer, self)._successHandler(code, ctx) if self._amount == 0 else makeI18nSuccess(self._successSysMsg, money=self._amount, packTitle=backport.text(R.strings.system_messages.se20_shop_pack.dyn(self._itemID)()), type=SM_TYPE.FinancialTransactionWithGold)


_SHOP_ITEMS_CLASSES = {EventPackTypes.PROGRESSION_OF_GENERAL: GeneralProgressItem,
 EventPackTypes.PROGRESSION_FOR_ALL_GENERALS: AllGeneralsProgressItem,
 EventPackTypes.ENERGY_OF_GENERAL: GeneralEnergyItem,
 EventPackTypes.ENERGY: ShopItem,
 EventPackTypes.REGULAR: ShopItem}

def _createShopObject(packID, packInfo, hiddenQuests):
    if packID.startswith(EventPackTypes.ENERGY_OF_GENERAL.value):
        packType = EventPackTypes.ENERGY_OF_GENERAL
    elif packID.startswith(EventPackTypes.PROGRESSION_OF_GENERAL.value):
        packType = EventPackTypes.PROGRESSION_OF_GENERAL
    elif packID.startswith(EventPackTypes.PROGRESSION_FOR_ALL_GENERALS.value):
        packType = EventPackTypes.PROGRESSION_FOR_ALL_GENERALS
    elif packID.startswith(EventPackTypes.ENERGY.value):
        packType = EventPackTypes.ENERGY
    else:
        packType = EventPackTypes.REGULAR
    item = _SHOP_ITEMS_CLASSES[packType](packID, packInfo, packType)
    item.init(hiddenQuests)
    return item
