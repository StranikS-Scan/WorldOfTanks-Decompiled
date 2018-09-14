# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/booster_tabs.py
from collections import defaultdict
from operator import attrgetter
import constants
from Event import EventManager, Event
from adisp import process
from gui import DialogsInterface, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs.ConfirmBoosterMeta import BuyBoosterMeta
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.genConsts.ACTION_PRICE_CONSTANTS import ACTION_PRICE_CONSTANTS
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from gui.goodies.Booster import BOOSTERS_ORDERS
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.server_events import g_eventsCache, events_dispatcher as quests_events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers.i18n import makeString as _ms
from gui.shared.utils import decorators
MAX_GUI_COUNT = 999
DEFAULT_SHOP_COUNT = 1

class TABS_IDS(object):
    INVENTORY = 0
    QUESTS = 1
    SHOP = 2


class _PRICE_STATE(object):
    NORMAL = 'iconColor'
    ERROR = 'error'


class BoosterTab(object):

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
        booster = g_goodiesCache.getBooster(boosterID)
        activeBooster = self.__getActiveBoosterByType(booster.boosterType)
        if activeBooster is not None:
            canActivate = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(BOOSTER_CONSTANTS.BOOSTER_ACTIVATION_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(booster.description),
             'curBoosterName': text_styles.middleTitle(activeBooster.description)}, focusedID=DIALOG_BUTTON_ID.CLOSE))
        else:
            canActivate = True
        if canActivate:
            self.__activateBoosterRequest(booster)
        return

    def _processBoostersData(self):
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        boosters = sorted(g_goodiesCache.getBoosters(criteria=criteria).values(), self._sort)
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
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @staticmethod
    def __getActiveBoosterByType(bType):
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([bType])
        activeBoosters = g_goodiesCache.getBoosters(criteria=criteria).values()
        return max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None


class ShopBoostersTab(BoosterTab):

    def __init__(self):
        super(ShopBoostersTab, self).__init__()
        self.__balance = g_itemsCache.items.stats.money

    def getID(self):
        return TABS_IDS.SHOP

    @process
    def doAction(self, boosterID, questID):
        booster = g_goodiesCache.getBooster(boosterID)
        if booster:
            yield DialogsInterface.showDialog(BuyBoosterMeta(boosterID, self.__balance))

    def updateBalance(self):
        self.__balance = g_itemsCache.items.stats.money
        self.update()

    def _processBoostersData(self):
        criteria = REQ_CRITERIA.BOOSTER.ENABLED | ~REQ_CRITERIA.HIDDEN
        boosters = sorted(g_goodiesCache.getBoosters(criteria=criteria).values(), self._sort)
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
        return {'id': booster.boosterID,
         'actionBtnEnabled': isPurchaseEnabled,
         'actionBtnTooltip': btnTooltip,
         'headerText': text_styles.middleTitle(booster.fullUserName),
         'descriptionText': text_styles.main(booster.description),
         'addDescriptionText': booster.getExpiryDateStr(),
         'actionBtnLabel': _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_BUYBTNLABEL),
         'tooltip': TOOLTIPS_CONSTANTS.BOOSTERS_SHOP,
         'boosterSlotVO': _makeBoosterSlotVO(booster, DEFAULT_SHOP_COUNT),
         'priceText': text_styles.standard(MENU.SHOP_TABLE_BUYACTIONOR),
         'creditsPriceState': priceState,
         'goldPriceState': priceState,
         'actionPriceData': self.__getActionVO(booster),
         'actionStyle': ACTION_PRICE_CONSTANTS.STATE_ALIGN_TOP,
         'rendererState': BOOSTER_CONSTANTS.RENDERER_STATE_SHOP,
         'price': {'oldPrice': booster.defaultPrice,
                   'newPrice': booster.buyPrice}}

    @staticmethod
    def __getActionVO(booster):
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.BOOSTER, str(booster.boosterID), True, booster.buyPrice, booster.defaultPrice) if booster.buyPrice != booster.defaultPrice else None

    @staticmethod
    def __getPriceState(isPurchaseEnabled):
        return _PRICE_STATE.NORMAL if isPurchaseEnabled else _PRICE_STATE.ERROR


class QuestsBoostersTab(BoosterTab):

    def __init__(self):
        super(QuestsBoostersTab, self).__init__()
        self.__boosterQuests = self.__getBoosterQuests()
        self.__questsDescriptor = events_helpers.getTutorialEventsDescriptor()

    def getID(self):
        return TABS_IDS.QUESTS

    def fini(self):
        self.__boosterQuests = None
        self.__questsDescriptor = None
        super(QuestsBoostersTab, self).fini()
        return

    def updateQuests(self):
        self.__boosterQuests = self.__getBoosterQuests()

    def doAction(self, boosterID, questID):
        if questID and questID.isdigit():
            questID = int(questID)
        quest = g_eventsCache.getAllQuests(includePotapovQuests=True).get(questID)
        if quest is not None:
            quests_events.showEventsWindow(quest.getID(), quest.getType())
        elif self.__questsDescriptor and self.__questsDescriptor.getChapter(questID):
            quests_events.showEventsWindow(questID, constants.EVENT_TYPE.TUTORIAL)
        return

    def _sort(self, qBoosterInfoA, qBoosterInfoB):
        _, _, boosterA, _ = qBoosterInfoA
        _, _, boosterB, _ = qBoosterInfoB
        return super(QuestsBoostersTab, self)._sort(boosterA, boosterB)

    def _makeBoosterVO(self, qBoosterInfo):
        questID, qUserName, booster, count = qBoosterInfo
        isBtnEnabled = questID is not None
        activateBtnLabel = MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_GOTOQUESTBTNLABEL
        addDescriptionText = ''
        btnTooltip = ''
        if qUserName is not None:
            btnTooltip = makeTooltip(None, _ms(TOOLTIPS.BOOSTER_QUESTLINKBTN_BODY, questName=qUserName))
            addDescriptionText = text_styles.standard(_ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_QUESTFOROPEN, questName=qUserName))
        return {'id': booster.boosterID,
         'questID': str(questID) if questID else None,
         'actionBtnEnabled': isBtnEnabled,
         'actionBtnTooltip': btnTooltip,
         'headerText': text_styles.middleTitle(booster.fullUserName),
         'descriptionText': text_styles.main(booster.description),
         'addDescriptionText': addDescriptionText,
         'actionBtnLabel': _ms(activateBtnLabel),
         'tooltip': TOOLTIPS_CONSTANTS.BOOSTERS_QUESTS,
         'boosterSlotVO': _makeBoosterSlotVO(booster, count),
         'rendererState': BOOSTER_CONSTANTS.RENDERER_STATE_DEFAULT}

    def _processBoostersData(self):
        self._boosters = []
        self._count = 0
        self._totalCount = 0
        for (questID, qUserName), boosters in self.__boosterQuests.iteritems():
            for booster, count in boosters:
                self._totalCount += count
                if self._isBoosterValid(booster):
                    self._count += count
                    self._boosters.append((questID,
                     qUserName,
                     booster,
                     count))

        self._boosters = sorted(self._boosters, self._sort)

    @staticmethod
    def __getBoosterQuests():
        result = defaultdict(list)
        quests = events_helpers.getBoosterQuests()
        for q in quests.itervalues():
            bonuses = q.getBonuses('goodies')
            for b in bonuses:
                boosters = b.getBoosters()
                for booster, count in boosters.iteritems():
                    result[q.getID(), q.getUserName()].append((booster, count))

        for chapter, boosters in events_helpers.getTutorialQuestsBoosters().iteritems():
            result[chapter.getID(), chapter.getTitle()].extend(boosters)

        return result


class TabsContainer(object):

    def __init__(self):
        self.__tabs = {TABS_IDS.INVENTORY: InventoryBoostersTab(),
         TABS_IDS.QUESTS: QuestsBoostersTab(),
         TABS_IDS.SHOP: ShopBoostersTab()}
        self.__currentTabIdx = None
        self.__activeBoostersCount = None
        self.__eManager = EventManager()
        self.onTabsUpdate = Event(self.__eManager)
        return

    def init(self):
        self.__activeBoostersCount = len(g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateBoosters,
         'shop': self.__onUpdateBoosters,
         'stats': self.__onStatsChanged})
        g_eventsCache.onSyncCompleted += self.__onQuestsUpdate

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

    @property
    def questsTab(self):
        return self.__tabs[TABS_IDS.QUESTS]

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
        g_eventsCache.onSyncCompleted -= self.__onQuestsUpdate
        for tab in self.__tabs.itervalues():
            tab.fini()

        self.__tabs.clear()
        self.__activeBoostersCount = None
        return

    def __onUpdateBoosters(self, *args):
        for tab in self.__tabs.itervalues():
            tab.update()

        self.__activeBoostersCount = len(g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        self.onTabsUpdate()

    def __onQuestsUpdate(self, *args):
        self.questsTab.updateQuests()
        self.__onUpdateBoosters()

    def __onStatsChanged(self, stats):
        if 'credits' in stats or 'gold' in stats:
            self.shopTab.updateBalance()
            self.onTabsUpdate()


def getGuiCount(count):
    if count <= MAX_GUI_COUNT:
        return str(count)
    else:
        return '%s+' % MAX_GUI_COUNT


def _makeBoosterSlotVO(booster, count):
    return {'boosterId': booster.boosterID,
     'icon': booster.icon,
     'countText': text_styles.counter(getGuiCount(count)),
     'showCount': count > 1,
     'qualityIconSrc': booster.getQualityIcon(),
     'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
     'showLeftTime': False}
