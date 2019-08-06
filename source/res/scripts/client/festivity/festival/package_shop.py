# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/package_shop.py
import logging
from collections import namedtuple
from gui import g_htmlTemplates
from gui.shared.gui_items.customization.c11n_items import STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP
from items import makeIntCompactDescrByID as makeCD
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, i18n
from items.components.c11n_constants import CustomizationType
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger()

class _PackageItem(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__packageID', '__extractedData', '__multiplier', '__price', '__allowMultiple')

    def __init__(self, packageID, extractedData, multiplier, price, allowMultiple):
        self.__packageID = packageID
        self.__extractedData = extractedData
        self.__multiplier = multiplier
        self.__price = price
        self.__allowMultiple = allowMultiple

    @property
    def extractedItems(self):
        return self.__extractedData

    @property
    def packageID(self):
        return self.__packageID

    @property
    def price(self):
        purchases = self.__itemsCache.items.festivity.getPurchases()
        alreadyBought = purchases.get(self.__packageID, 0)
        finalPrice = int(self.__price * self.__multiplier ** alreadyBought)
        return finalPrice

    @property
    def isMultipleAllowed(self):
        return self.__allowMultiple


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _itemsExtractor(rawData, formatter, itemsCache=None):
    result = []
    for itemIntCD, count in rawData.iteritems():
        result.append(formatter(itemsCache.items.getItemByCD(itemIntCD), count))

    return result


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def _goodiesExtractor(rawData, formatter, goodiesCache=None):
    result = []
    for boosterID, countDict in rawData.iteritems():
        result.append(formatter(goodiesCache.getBooster(boosterID), countDict['count']))

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _customizationsExtractor(rawData, formatter, itemsCache=None):
    result = []
    for customizationData in rawData:
        custType = customizationData['custType']
        custID = customizationData['id']
        count = customizationData['value']
        custIntCD = _getCustomizationIntCDFromID(custType, custID)
        result.append(formatter(itemsCache.items.getItemByCD(custIntCD), count))

    return result


def _getCustomizationIntCDFromID(custType, custID):
    return makeCD('customizationItem', _CUSTOMIZATION_MAP[custType], custID) if custType in _CUSTOMIZATION_MAP else custID


class _BaseFormatter(object):
    __slots__ = ('_itemObj', '__count')

    def __init__(self, itemObj, count):
        self._itemObj = itemObj
        self.__count = count

    @property
    def title(self):
        return self._getTitle()

    @property
    def shortName(self):
        return self._getShortName()

    @property
    def description(self):
        return self._getDescription()

    @property
    def count(self):
        return self.__count

    @property
    def icon(self):
        return self._getIcon()

    @property
    def modifierIcon(self):
        return self._getModifierIcon()

    @property
    def userType(self):
        return self._getUserType()

    @property
    def shortUserType(self):
        return self._getShortUserType()

    def _getTitle(self):
        raise NotImplementedError

    def _getShortName(self):
        raise NotImplementedError

    def _getDescription(self):
        raise NotImplementedError

    def _getIcon(self):
        shopIcon = self._itemObj.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL)
        return '../../' + shopIcon if shopIcon else self._itemObj.icon

    def _getModifierIcon(self):
        pass

    def _getUserType(self):
        raise NotImplementedError

    def _getShortUserType(self):
        raise NotImplementedError


class _ItemFormatter(_BaseFormatter):
    __slots__ = ()

    def _getTitle(self):
        return self._itemObj.userName

    def _getShortName(self):
        return self._getTitle()

    def _getDescription(self):
        special = self._itemObj.shortDescriptionSpecial
        if special:
            template = g_htmlTemplates['html_templates:lobby/festival/shopPackages']['description'].source
            return special.format(**template)
        return self._itemObj.shortDescription

    def _getModifierIcon(self):
        return backport.image(R.images.gui.maps.icons.festival.shop.battle_booster_modifier()) if self._itemObj.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else super(_ItemFormatter, self)._getModifierIcon()

    def _getUserType(self):
        return self._itemObj.userType

    def _getShortUserType(self):
        itemType = self._itemObj.itemTypeName
        userType = R.strings.festival.festivalShopView.buy.dyn(itemType)
        return backport.text(userType()) if userType.exists() else self._getUserType()


class _GoodieFormatter(_BaseFormatter):
    __slots__ = ()

    def _getTitle(self):
        return self._itemObj.getBonusDescription(valueFormatter=text_styles.neutral)

    def _getShortName(self):
        return self._itemObj.getBonusDescription()

    def _getDescription(self):
        return self._itemObj.shortDescriptionSpecial

    def _getUserType(self):
        return backport.text(R.strings.menu.boosters.common.name())

    def _getShortUserType(self):
        return backport.text(R.strings.festival.festivalShopView.buy.booster())


class _CustomizationFormatter(_ItemFormatter):
    __slots__ = ('__userKey',)

    def __init__(self, itemObj, count):
        super(_CustomizationFormatter, self).__init__(itemObj, count)
        self.__userKey = itemObj.descriptor.userKey.split('/')[-1]

    def _getUserType(self):
        return i18n.makeString(STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP[self._itemObj.groupID]) if self._itemObj.itemTypeID == GUI_ITEM_TYPE.STYLE else self._getUserType()

    def _getIcon(self):
        styleIcon = R.images.gui.maps.icons.festival.shop.styles.dyn(self.__userKey)
        return backport.image(styleIcon()) if styleIcon.exists() else super(_CustomizationFormatter, self)._getIcon()

    def _getDescription(self):
        shortDescr = R.strings.festival.festivalShopView.description.style.dyn(self.__userKey)
        return backport.text(shortDescr()) if shortDescr.exists() else super(_CustomizationFormatter, self)._getDescription()


_Processor = namedtuple('_Processor', 'extractor, formatter')
_BONUS_PROCESSOR = {'items': _Processor(_itemsExtractor, _ItemFormatter),
 'goodies': _Processor(_goodiesExtractor, _GoodieFormatter),
 'customizations': _Processor(_customizationsExtractor, _CustomizationFormatter)}
_CUSTOMIZATION_MAP = {'style': CustomizationType.STYLE}

class FestivalPackageShop(object):
    __slots__ = ('__packages',)

    def __init__(self, festivalConfig):
        self.__packages = {}
        self.update(festivalConfig)

    def getPackages(self):
        return self.__packages

    def getPackageByID(self, pkgID):
        return self.__packages.get(pkgID)

    def update(self, festivalConfig):
        self.__packages = {}
        for packageID, packageInfo in festivalConfig.iteritems():
            bonuses = packageInfo['bonus']
            extracted = []
            for bonusName, bonusValue in bonuses.iteritems():
                if bonusName not in _BONUS_PROCESSOR:
                    _logger.error('Bonus %s is not supported by UI.', bonusName)
                    continue
                processor = _BONUS_PROCESSOR[bonusName]
                bonusData = processor.extractor(bonusValue, processor.formatter)
                extracted.extend(bonusData)

            price = packageInfo['price']
            multiplier = packageInfo['multiplier']
            allowMultiple = packageInfo['allowMultiple']
            self.__packages[packageID] = _PackageItem(packageID, extracted, multiplier, price, allowMultiple)
