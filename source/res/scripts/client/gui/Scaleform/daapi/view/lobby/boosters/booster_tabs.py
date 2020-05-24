# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/booster_tabs.py
from operator import attrgetter
from Event import EventManager, Event
from adisp import process
from gui import DialogsInterface, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs.ConfirmBoosterMeta import BuyBoosterMeta
from gui.Scaleform.genConsts.ACTION_PRICE_CONSTANTS import ACTION_PRICE_CONSTANTS
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import BOOSTERS_ORDERS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
MAX_GUI_COUNT = 999
DEFAULT_SHOP_COUNT = 1

class TABS_IDS(object):
    INVENTORY = 0
    SHOP = 1


class _PRICE_STATE(object):
    NORMAL = 'iconColor'
    ERROR = 'error'


class BoosterTab(object):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(BoosterTab, self).__init__()
        self.__qualities = []
        self.__boosterTypes = []
        self._boosters = []
        self._count = 0
        self._totalCount = 0

    def fini(self):
        self.__qualities = None
        self.__boosterTypes = None
        self._count = None
        self._totalCount = None
        self._boosters = None
        return

    def setFilters(self, qualities, boosterTypes):
        self.__qualities = qualities
        self.__boosterTypes = boosterTypes
        self.update()

    def getID(self):
        raise NotImplementedError

    def getCount(self):
        return self._count

    def getTotalCount(self):
        return self._totalCount

    def update(self):
        self._processBoostersData()

    def getBoostersVOs(self):
        boosterVOs = []
        for booster in self._boosters:
            boosterVOs.append(self._makeBoosterVO(booster))

        return boosterVOs

    def doAction(self, boosterID, questID):
        raise NotImplementedError

    def _sort(self, a, b):
        return cmp(a.quality, b.quality) or cmp(BOOSTERS_ORDERS[a.boosterType], BOOSTERS_ORDERS[b.boosterType]) or cmp(b.effectValue, a.effectValue)

    def _isBoosterValid(self, booster):
        isTypeValid = True
        if self.__boosterTypes:
            isTypeValid = booster.boosterType in self.__boosterTypes
        isQualityValid = True
        if self.__qualities:
            isQualityValid = booster.quality in self.__qualities
        return isTypeValid and isQualityValid

    def _makeBoosterVO(self, *args):
        raise NotImplementedError

    def _processBoostersData(self):
        raise NotImplementedError


class InventoryBoostersTab(BoosterTab):

    def getID(self):
        return TABS_IDS.INVENTORY

    @process
    def doAction(self, boosterID, questID):
        booster = self.goodiesCache.getBooster(boosterID)
        activeBooster = self.__getActiveBoosterByType(booster.boosterType)
        if activeBooster is not None:
            canActivate = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(BOOSTER_CONSTANTS.BOOSTER_REPLACE_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(booster.description),
             'curBoosterName': text_styles.middleTitle(activeBooster.description)}, focusedID=DIALOG_BUTTON_ID.CLOSE))
        else:
            canActivate = True
        if canActivate:
            self.__activateBoosterRequest(booster)
        return

    def _processBoostersData(self):
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        boosters = sorted(self.goodiesCache.getBoosters(criteria=criteria).values(), cmp=self._sort)
        self._boosters = []
        self._count = 0
        self._totalCount = 0
        for booster in boosters:
            self._totalCount += booster.count
            if self._isBoosterValid(booster):
                self._count += booster.count
                self._boosters.append(booster)

    def _makeBoosterVO(self, booster):
        isBtnEnabled = booster.isReadyToActivate
        activateBtnLabel = MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_ACTIVATEBTNLABEL
        btnTooltip = makeTooltip(None, _ms(TOOLTIPS.BOOSTER_ACTIVEBTN_DISABLED_BODY)) if not isBtnEnabled else ''
        return {'id': booster.boosterID,
         'actionBtnEnabled': isBtnEnabled,
         'actionBtnTooltip': btnTooltip,
         'headerText': text_styles.middleTitle(booster.fullUserName),
         'descriptionText': text_styles.main(booster.description),
         'addDescriptionText': booster.getExpiryDateStr(),
         'actionBtnLabel': _ms(activateBtnLabel),
         'tooltip': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
         'boosterSlotVO': _makeBoosterSlotVO(booster, booster.count),
         'rendererState': BOOSTER_CONSTANTS.RENDERER_STATE_DEFAULT}

    @decorators.process('loadStats')
    def __activateBoosterRequest(self, booster):
        result = yield BoosterActivator(booster).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @classmethod
    def __getActiveBoosterByType(cls, bType):
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([bType])
        activeBoosters = cls.goodiesCache.getBoosters(criteria=criteria).values()
        return max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None


class ShopBoostersTab(BoosterTab):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ShopBoostersTab, self).__init__()
        self.__balance = self.itemsCache.items.stats.money

    def getID(self):
        return TABS_IDS.SHOP

    @process
    def doAction(self, boosterID, questID):
        booster = self.goodiesCache.getBooster(boosterID)
        if booster:
            yield DialogsInterface.showDialog(BuyBoosterMeta(boosterID, self.__balance))

    def updateBalance(self):
        self.__balance = self.itemsCache.items.stats.money
        self.update()

    def _processBoostersData(self):
        criteria = REQ_CRITERIA.BOOSTER.ENABLED | ~REQ_CRITERIA.HIDDEN
        boosters = sorted(self.goodiesCache.getBoosters(criteria=criteria).values(), cmp=self._sort)
        self._boosters = []
        self._count = 0
        self._totalCount = 0
        for booster in boosters:
            self._totalCount += DEFAULT_SHOP_COUNT
            if self._isBoosterValid(booster):
                self._count += DEFAULT_SHOP_COUNT
                self._boosters.append(booster)

    def _makeBoosterVO(self, booster):
        isPurchaseEnabled, _ = booster.mayPurchase(self.__balance)
        btnTooltip = makeTooltip(None, _ms(TOOLTIPS.BOOSTER_ACTIVEBTN_DISABLED_BODY)) if not isPurchaseEnabled else ''
        priceState = self.__getPriceState(isPurchaseEnabled)
        itemPrice = booster.buyPrices.itemPrice
        return {'id': booster.boosterID,
         'actionBtnEnabled': isPurchaseEnabled,
         'actionBtnTooltip': btnTooltip,
         'headerText': text_styles.middleTitle(booster.fullUserName),
         'descriptionText': text_styles.main(booster.description),
         'addDescriptionText': booster.getExpiryDateStr(),
         'actionBtnLabel': _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_BUYBTNLABEL),
         'tooltip': TOOLTIPS_CONSTANTS.BOOSTER,
         'boosterSlotVO': _makeBoosterSlotVO(booster, DEFAULT_SHOP_COUNT),
         'priceText': text_styles.standard(MENU.SHOP_TABLE_BUYACTIONOR),
         'creditsPriceState': priceState,
         'goldPriceState': priceState,
         'actionPriceData': self.__getActionVO(booster),
         'actionStyle': ACTION_PRICE_CONSTANTS.STATE_ALIGN_TOP,
         'rendererState': BOOSTER_CONSTANTS.RENDERER_STATE_SHOP,
         'price': {'oldPrice': itemPrice.defPrice.toMoneyTuple(),
                   'newPrice': itemPrice.price.toMoneyTuple()}}

    @staticmethod
    def __getActionVO(booster):
        itemPrice = booster.buyPrices.itemPrice
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.BOOSTER, str(booster.boosterID), True, itemPrice.price, itemPrice.defPrice) if itemPrice.isActionPrice() else None

    @staticmethod
    def __getPriceState(isPurchaseEnabled):
        return _PRICE_STATE.NORMAL if isPurchaseEnabled else _PRICE_STATE.ERROR


class TabsContainer(object):
    eventsCache = dependency.descriptor(IEventsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        self.__tabs = {TABS_IDS.INVENTORY: InventoryBoostersTab(),
         TABS_IDS.SHOP: ShopBoostersTab()}
        self.__currentTabIdx = None
        self.__activeBoostersCount = None
        self.__eManager = EventManager()
        self.onTabsUpdate = Event(self.__eManager)
        return

    def init(self):
        self.__activeBoostersCount = len(self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateBoosters,
         'shop': self.__onUpdateBoosters,
         'stats': self.__onStatsChanged})

    def setCurrentTabIdx(self, currentTabIdx):
        self.__currentTabIdx = currentTabIdx

    @property
    def currentTab(self):
        return self.__tabs[self.__currentTabIdx]

    @property
    def inventoryTab(self):
        return self.__tabs[TABS_IDS.INVENTORY]

    @property
    def shopTab(self):
        return self.__tabs[TABS_IDS.SHOP]

    def getTabs(self):
        return self.__tabs

    def setFilters(self, qualities, boosterTypes):
        for tab in self.__tabs.itervalues():
            tab.setFilters(qualities, boosterTypes)

    def getActiveBoostersCount(self):
        return self.__activeBoostersCount

    def fini(self):
        self.__currentTabIdx = None
        self.__eManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        for tab in self.__tabs.itervalues():
            tab.fini()

        self.__tabs.clear()
        self.__activeBoostersCount = None
        return

    def __onUpdateBoosters(self, *args):
        for tab in self.__tabs.itervalues():
            tab.update()

        self.__activeBoostersCount = len(self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        self.onTabsUpdate()

    def __onStatsChanged(self, stats):
        if Money.hasMoney(stats):
            self.shopTab.updateBalance()
            self.onTabsUpdate()


def getGuiCount(count):
    return str(count) if count <= MAX_GUI_COUNT else '%s+' % MAX_GUI_COUNT


def _makeBoosterSlotVO(booster, count):
    return {'boosterId': booster.boosterID,
     'icon': booster.icon,
     'countText': text_styles.counter(getGuiCount(count)),
     'showCount': count > 1,
     'qualityIconSrc': booster.getQualityIcon(),
     'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
     'showLeftTime': False}
