# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/offers/events_data.py
import logging
import time
import typing
from constants import PREMIUM_ENTITLEMENTS, RentType
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.offers import getGfImagePath
from gui.server_events.bonuses import getOfferBonuses, VehiclesBonus
from gui.shared.money import Currency
from helpers import dependency, getClientLanguage, time_utils
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
CDN_KEY = 'cdn'
OFFER_BONUSES_PRIORITY = ('vehicles',
 Currency.GOLD,
 Currency.CRYSTAL,
 Currency.CREDITS,
 'freeXP',
 'items',
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 'customizations',
 'tankmen',
 'crewSkins',
 'goodies',
 'slots',
 'berths',
 'blueprints',
 'blueprintsAny',
 'tokens')
DEFAULT_PRIORITY = len(OFFER_BONUSES_PRIORITY)

class OfferEventData(object):
    __slots__ = ('_id', '_data', '_langCode')
    _itemsCache = dependency.descriptor(IItemsCache)
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _langCode = getClientLanguage()

    def __init__(self, itemID, data):
        self._id = itemID
        self._data = dict(data)

    @property
    def id(self):
        return self._id

    @property
    def token(self):
        return self._data.get('token')

    @property
    def giftToken(self):
        return self._data.get('giftToken')

    @property
    def giftTokenCount(self):
        return self._data.get('giftTokenCount')

    @property
    def showBanner(self):
        return self._data.get('showBanner')

    @property
    def priority(self):
        return self._data.get('priority')

    @property
    def showPrice(self):
        return self._data.get('showPrice', False)

    @property
    def showInGUI(self):
        return self._data.get('showInGUI')

    @property
    def cdnLocFilePath(self):
        _path = self._data.get(CDN_KEY, {}).get('localization')
        return _path % self._langCode if _path else ''

    @property
    def cdnBannerLogoPath(self):
        return self._data.get(CDN_KEY, {}).get('bannerLogo', '')

    @property
    def cdnLogoPath(self):
        return self._data.get(CDN_KEY, {}).get('logo', '')

    @property
    def cdnGiftsBackgroundPath(self):
        return self._data.get(CDN_KEY, {}).get('giftsBackground', '')

    @property
    def cdnGiftsTokenImgPath(self):
        return self._data.get(CDN_KEY, {}).get('giftTokenImg', '')

    @property
    def availableGifts(self):
        received = self._receivedGifts
        if received is None:
            return []
        else:
            return [ OfferGift(giftID, settings) for giftID, settings in self._data.get('gift', {}).iteritems() if giftID not in received or not settings.get('limit', 1) or giftID in received and settings.get('limit', 1) and received[giftID] < settings.get('limit', 1) ]

    def getGift(self, giftID):
        giftsData = self._data.get('gift')
        return OfferGift(giftID, self._data['gift'][giftID]) if giftsData and giftID in giftsData else None

    def getGiftAvailabelCount(self, giftID):
        received = self._receivedGifts
        if received is None:
            return 0
        else:
            giftsData = self._data.get('gift')
            if giftsData and giftID in giftsData:
                limits = giftsData[giftID].get('limit', 1)
                if limits > 0:
                    if giftID not in received:
                        return limits
                    return limits - received[giftID]
            return -1

    def getAllGifts(self):
        return [ OfferGift(giftID, settings) for giftID, settings in self._data.get('gift', {}).iteritems() ]

    def getFirstGift(self):
        for giftID, settings in self._data.get('gift', {}).iteritems():
            return OfferGift(giftID, settings)

        return None

    @property
    def clicksCount(self):
        return min(self.availableTokens, self.availableGiftsCount)

    @property
    def availableTokens(self):
        return self._tokensCache.getTokenCount(self.giftToken)

    @property
    def availableGiftsCount(self):
        received = self._receivedGifts
        if received is None:
            return 0
        else:
            giftsCount = len(self._data.get('gift', {}))
            notReceived = giftsCount - len(self.isOutOfLimit)
            return max(notReceived, 0)

    @property
    def isOutOfLimit(self):
        received = self._receivedGifts
        if received is None:
            return []
        else:
            outOfLimits = []
            gifts = self._data.get('gift', {})
            for giftID in received:
                limit = gifts.get(giftID, {}).get('limit', 1)
                if limit and received[giftID] >= limit:
                    outOfLimits.append(giftID)

            return outOfLimits

    @property
    def expiration(self):
        return min(self._tokensCache.getTokenExpiryTime(self.token), self._tokensCache.getTokenExpiryTime(self.giftToken), self.getFinishTime())

    @property
    def isOfferAvailable(self):
        return self._tokensCache.isTokenAvailable(self.token) and self._tokensCache.isTokenAvailable(self.giftToken) and not self.isOutOfDate and bool(self.availableGiftsCount)

    @property
    def isOutOfDate(self):
        return self.getFinishTimeLeft() <= 0

    def getFinishTime(self):
        return time_utils.makeLocalServerTime(self._data['finishTime']) if 'finishTime' in self._data else time.time()

    def getFinishTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getFinishTime())

    @property
    def _tokensCache(self):
        return self._itemsCache.items.tokens

    @property
    def _receivedGifts(self):
        return self._offersProvider.getReceivedGifts(self.id)


class OfferGift(object):
    _langCode = getClientLanguage()

    def __init__(self, giftID, giftData):
        self._id = giftID
        self._data = giftData
        self._bonus = None
        self._bonuses = None
        return

    @property
    def id(self):
        return self._id

    @property
    def cdnLocFilePath(self):
        _path = self._data.get(CDN_KEY, {}).get('localization')
        return _path % self._langCode if _path else ''

    @property
    def cdnImagePath(self):
        return self._data.get(CDN_KEY, {}).get('image', '')

    @property
    def cdnIconPath(self):
        return self._data.get(CDN_KEY, {}).get('icon', '')

    @property
    def fromCdn(self):
        return CDN_KEY in self._data

    @property
    def title(self):
        return self.bonus.getOfferName() if not self.fromCdn and self.bonus else ''

    @property
    def description(self):
        if not self.fromCdn and self.bonus:
            description = self.bonus.getOfferDescription()
            separator = ''
            itemsInfo = ''
            if self.isVehicle:
                items = None
                if self.bonus.isWithCrew and self.isWithSlotBonus:
                    items = R.strings.offers.giftDescription.tank.withCrewAndSlot()
                elif self.bonus.isWithCrew:
                    items = R.strings.offers.giftDescription.tank.withCrew()
                elif self.isWithSlotBonus:
                    items = R.strings.offers.giftDescription.tank.withSlot()
                if items is not None:
                    itemsInfo = backport.text(R.strings.offers.giftDescription.tank.base(), items=backport.text(items))
                if description and itemsInfo:
                    separator = ' ' if description.endswith('.') else '. '
            return ''.join([description, separator, itemsInfo])
        else:
            return ''

    @property
    def icon(self):
        return getGfImagePath(self.bonus.getOfferIcon()) if not self.fromCdn and self.bonus else ''

    @property
    def price(self):
        return self._data.get('price', 1)

    def limit(self):
        return self._data.get('limit', 1)

    @property
    def nationFlag(self):
        flag = None
        if not self.fromCdn and self.bonus:
            flag = self.bonus.getOfferNationalFlag()
        return flag or ''

    @property
    def highlight(self):
        return self.bonus.getOfferHighlight() if not self.fromCdn and self.bonus else ''

    @property
    def giftCount(self):
        return self.bonus.getGiftCount() if self.bonus else 0

    @property
    def inventoryCount(self):
        return self.bonus.getInventoryCount() if self.bonus else 0

    @property
    def rentType(self):
        if self.bonus and self.isVehicle:
            _, vInfo = self.bonus.getVehicles()[0]
            rentType, _ = self.bonus.getRentInfo(vInfo)
            return rentType
        return RentType.NO_RENT

    @property
    def rentValue(self):
        if self.bonus and self.isVehicle:
            _, vInfo = self.bonus.getVehicles()[0]
            _, rentValue = self.bonus.getRentInfo(vInfo)
            return rentValue

    @property
    def isDisabled(self):
        disabled = True
        if self.bonuses:
            disabled = any((bonus.isMaxCountExceeded() for bonus in self.bonuses))
        return disabled

    @property
    def bonuses(self):
        if self._bonuses is None:
            self._bonuses = []
            for name, value in self._data.get('bonus', dict()).iteritems():
                self._bonuses += getOfferBonuses(name, value)

            if not self._bonuses:
                if not self.fromCdn:
                    _logger.error('Wrong gift id=%d. For representation must be at least one valid bonus or cdn section. bonus=%s', self.id, self._data)
            else:
                self._bonuses.sort(key=lambda x: OFFER_BONUSES_PRIORITY.index(x.getName()) if x.getName() in OFFER_BONUSES_PRIORITY else DEFAULT_PRIORITY)
        return self._bonuses

    @property
    def bonus(self):
        if self._bonus is None:
            for bonus in self.bonuses:
                if bonus.canBeShown():
                    self._bonus = bonus
                    break

        return self._bonus

    @property
    def isWithSlotBonus(self):
        return 'slots' in self._data.get('bonus', dict())

    @property
    def buttonLabel(self):
        return R.strings.offers.giftsWindow.previewButtonLabel() if self.isVehicle else R.strings.offers.giftsWindow.takeButtonLabel()

    @property
    def isVehicle(self):
        return isinstance(self.bonus, VehiclesBonus)

    @property
    def bonusType(self):
        return self.bonus.getName() if self.bonus else None
