# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_view.py
from gui.impl.lobby.personal_reserves.personal_reserves_utils import findNearestExpiryTimeInBoostersList
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier
from helpers.i18n import makeString as _ms
import copy
from account_helpers import AccountSettings
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from goodies.goodie_helpers import GoodieExpirationData
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, isStorageSessionTimeout
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPersonalReservesUrl
from gui.Scaleform.daapi.view.meta.StorageCategoryPersonalReservesViewMeta import StorageCategoryPersonalReservesViewMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import BOOSTERS_ORDERS, MAX_ACTIVE_BOOSTERS_COUNT
from gui.impl import backport
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PREMIUM_BOOSTER_IDS
from gui.impl.gen import R
from gui.shared.event_dispatcher import showShop, showPersonalReservesInfomationScreen, showBoostersActivation
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers import time_utils
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache

class _FilterBit(CONST_CONTAINER):
    XP = 1
    CREW_XP = 2
    FREE_XP = 4
    CREDITS = 8
    ONE = 16
    TWO = 32
    FOUR = 64
    SIX = 128
    FREE_XP_CREW_XP = 256
    EXPIRABLE = 512
    NON_EXPIRABLE = 1024
    PREMIUM = 2048


_TYPE_BIT_TO_RESOURCE_TYPE_MAP = {_FilterBit.XP: GOODIE_RESOURCE_TYPE.XP,
 _FilterBit.CREDITS: GOODIE_RESOURCE_TYPE.CREDITS,
 _FilterBit.FREE_XP_CREW_XP: GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP}
_TYPE_BIT_TO_CRITERIA = {_FilterBit.PREMIUM: REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS)}
_TYPE_FILTER_ITEMS = [{'filterValue': _FilterBit.XP,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_VEHICLEEXP),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_XP_SMALL_BW},
 {'filterValue': _FilterBit.CREDITS,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_CREDITS),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_CREDITS_SMALL_BW},
 {'filterValue': _FilterBit.FREE_XP_CREW_XP,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_COMBOEXP),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FREE_XP_AND_CREW_XP_SMALL_BW},
 {'filterValue': _FilterBit.PREMIUM,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_PREMIUM),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FILTER_PREMIUM_SMALL_BW},
 {'filterValue': _FilterBit.NON_EXPIRABLE,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_NONEXPIRABLE),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FILTER_NON_EXPIRABLE_SMALL_BW},
 {'filterValue': _FilterBit.EXPIRABLE,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_EXPIRABLE),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FILTER_EXPIRABLE_SMALL_BW}]

def getCriteriaFromFilterMask(filterMask):
    criteria = REQ_CRITERIA.EMPTY
    typesSet = {_TYPE_BIT_TO_RESOURCE_TYPE_MAP[bit] for bit in _TYPE_BIT_TO_RESOURCE_TYPE_MAP.iterkeys() if filterMask & bit}
    if typesSet:
        criteria |= REQ_CRITERIA.BOOSTER.BOOSTER_TYPES(typesSet)
    for bit, crit in _TYPE_BIT_TO_CRITERIA.iteritems():
        if filterMask & bit:
            criteria |= crit

    return criteria


class StorageCategoryPersonalReservesView(StorageCategoryPersonalReservesViewMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(StorageCategoryPersonalReservesView, self).__init__()
        self._boosters = []
        self.__filterMask = 0
        self.__notificatorManager = Notifiable()
        self._loadFilters()

    def navigateToStore(self):
        showShop(getBuyPersonalReservesUrl())

    def resetFilter(self):
        self.__filterMask = 0
        self.as_resetFilterS(self.__filterMask)
        self.__onUpdateBoosters()

    def onFiltersChange(self, filterMask):
        self.__filterMask = filterMask
        self.__onUpdateBoosters()

    def onInfoClicked(self):
        showPersonalReservesInfomationScreen()

    def activateReserve(self, boosterID):
        showBoostersActivation()

    def _getClientSectionKey(self):
        pass

    def _loadFilters(self):
        if isStorageSessionTimeout():
            return
        filterDict = AccountSettings.getSessionSettings(self._getClientSectionKey())
        self.__filterMask = filterDict['filterMask']

    def _saveFilters(self):
        filterDict = {'filterMask': self.__filterMask}
        AccountSettings.setSessionSettings(self._getClientSectionKey(), filterDict)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StorageCategoryPersonalReservesView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOSTERS_PANEL:
            viewPy.setSlotProps({'slotsCount': MAX_ACTIVE_BOOSTERS_COUNT,
             'slotWidth': 50,
             'paddings': 64,
             'groupPadding': 18,
             'ySlotPosition': 5,
             'offsetSlot': -2,
             'useOnlyLeftBtn': True})

    def _populate(self):
        super(StorageCategoryPersonalReservesView, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onGoodiesCacheUpdate,
         'shop': self.__onUpdateBoosters})
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdate
        self._epicCtrl.onUpdated += self.__onUpdateBoosters
        self.__onUpdateBoosters()
        self.__initFilter()
        self.__notificatorManager.addNotificator(TimerNotifier(self.__timeTillNextNotification, self.__onUpdateBoosters))
        self.__notificatorManager.startNotification()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdate
        self._epicCtrl.onUpdated -= self.__onUpdateBoosters
        self.__notificatorManager.clearNotification()
        self._saveFilters()
        super(StorageCategoryPersonalReservesView, self)._dispose()

    def _update(self, *args):
        self.__onUpdateBoosters()

    def __getBoosters(self):
        return self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT).values()

    def __timeTillNextNotification(self):
        nextExpiry = findNearestExpiryTimeInBoostersList(self.__getBoosters())
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(nextExpiry))
        return timeLeft

    def __onGoodiesCacheUpdate(self, *args):
        self.__onUpdateBoosters()
        self.__notificatorManager.startNotification()

    def __onUpdateBoosters(self, *args):
        _time = time_utils.getServerUTCTime()
        totalBoostersCount = 0
        for booster in self.__getBoosters():
            expirations = booster.expirations
            totalBoostersCount += len(expirations)
            remaining = booster.count - sum((exp.amount for exp in expirations.itervalues()))
            if remaining:
                totalBoostersCount += 1

        filteredBoostersCount = 0
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        criteria |= getCriteriaFromFilterMask(self.__filterMask)
        boosters = self._goodiesCache.getBoosters(criteria=criteria).values()
        dataProviderValues = []
        showDummyScreen = False
        filterWarningVO = None
        newBoosters = []
        if boosters:
            filterExpirable = self.__filterMask & _FilterBit.EXPIRABLE
            filterNonExpirable = self.__filterMask & _FilterBit.NON_EXPIRABLE
            if filterExpirable and filterNonExpirable:
                filterExpirable = False
                filterNonExpirable = False
            for booster in boosters:
                expirations = booster.expirations
                if not filterNonExpirable:
                    newBoosters.extend(expirations.itervalues())
                remaining = booster.count - sum((exp.amount for exp in expirations.itervalues()))
                if remaining and not filterExpirable:
                    newBoosters.append(GoodieExpirationData(booster, float('inf'), remaining))

        if newBoosters:
            for booster, timestamp, amount in sorted(newBoosters, cmp=self.__sort):
                influence = backport.text(R.strings.menu.booster.influence.dyn(booster.boosterGuiType)())
                limitResource = R.strings.menu.booster.limit.dyn(booster.boosterGuiType)
                if limitResource:
                    additionalInfo = text_styles.alert(backport.text(limitResource()))
                else:
                    additionalInfo = ''
                vo = createStorageDefVO(booster.boosterID, text_styles.hightlight(_ms(MENU.BOOSTER_DESCRIPTION_EFFECTVALUETIME, effectValue=booster.getFormattedValue(), effectTime=booster.getEffectTimeStr(hoursOnly=True))), text_styles.main(influence), amount, getItemPricesVO(booster.getSellPrice())[0], booster.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL), booster.getShopIcon(), 'altimage', available=booster.isAvailable, contextMenuId=None, additionalInfo=additionalInfo, sellBtnLabel=backport.text(R.strings.storage.buttonLabel.activate()))
                if timestamp != float('inf'):
                    timeLeft = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(timestamp)))
                    message = time_utils.getTillTimeString(timeLeft, MENU.BOOSTERS_TIMELEFT, removeLeadingZeros=True)
                    expTimeStr = makeHtmlString('html_templates:lobby/textStyle/', 'clockWithText', {'text': message})
                    vo['customData'] = {'expiryTime': expTimeStr}
                dataProviderValues.append(vo)
                filteredBoostersCount += 1

        elif totalBoostersCount == 0:
            showDummyScreen = True
        else:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        self._dataProvider.buildList(dataProviderValues)
        self.__updateFilterCounter(filteredBoostersCount, totalBoostersCount)
        self.as_showFilterWarningS(filterWarningVO)
        self.as_showDummyScreenS(showDummyScreen)
        return

    def __onQuestsUpdate(self, *args):
        self.__onUpdateBoosters()

    def __sort(self, a, b):
        return cmp(a.timestamp, b.timestamp) or cmp(BOOSTERS_ORDERS[a.booster.boosterType], BOOSTERS_ORDERS[b.booster.boosterType]) or cmp(b.booster.effectValue, a.booster.effectValue) or cmp(b.booster.effectTime, a.booster.effectTime)

    def __initFilter(self):
        typeItems = copy.deepcopy(_TYPE_FILTER_ITEMS)
        for item in typeItems:
            if self.__filterMask & item['filterValue'] == item['filterValue']:
                item.update({'selected': True})

        typeFilters = {'items': typeItems,
         'minSelectedItems': 0}
        self.as_initFilterS(typeFilters)

    def __updateFilterCounter(self, count, total):
        shouldShow = self.__filterMask != 0
        if shouldShow and total > 0:
            countString = self._formatCountString(count, total)
            drawAttention = count == 0
            self.as_updateCounterS(shouldShow, countString, drawAttention)
        else:
            countString = self._formatTotalCountString(total)
            self.as_updateCounterS(False, countString, False)
