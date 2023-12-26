# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/MarketplaceConfig.py
from typing import List, Dict, Optional, Callable, Union
from ny_common.settings import MarketplaceConsts
from items.new_year import g_cache
from items.components.ny_constants import YEARS_INFO
from math import ceil

class MarketplaceConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getCategoryByID(self, categoryID):
        return self._config[categoryID] if 0 <= categoryID < len(self._config) else None

    def getCategoryByName(self, categoryName):
        for categoryData in self._config:
            if categoryData.get(MarketplaceConsts.CATEGORY_NAME, None) == categoryName:
                return categoryData

        return

    def getCategory(self, categoryID):
        if isinstance(categoryID, int):
            return self.getCategoryByID(categoryID)
        else:
            return self.getCategoryByName(categoryID) if isinstance(categoryID, str) else None

    def getCategoryItems(self, categoryID):
        categoryData = self.getCategory(categoryID)
        return None if categoryData is None else map(CategoryItem, categoryData[MarketplaceConsts.CATEGORY_ITEMS])

    def getCategoryItem(self, categoryID, index):
        categoryData = self.getCategory(categoryID)
        if categoryData is None:
            return
        else:
            itemsData = categoryData[MarketplaceConsts.CATEGORY_ITEMS]
            return CategoryItem(itemsData[index]) if 0 <= index < len(itemsData) else None


class CategoryItem(object):
    __slots__ = ('_itemData', '_actionDiscountProcessors')

    def __init__(self, itemData):
        self._itemData = itemData
        self._actionDiscountProcessors = {MarketplaceConsts.FILL_COLLECTION: self.calculateDiscountForFillCollection,
         MarketplaceConsts.BUY_REWARDS: self.calculateDiscountForBuyReward,
         MarketplaceConsts.CHECK_PREV_NY_LEVEL: self.calculateDiscountForCheckPrevNYLevel}

    def getID(self):
        return self._itemData.get(MarketplaceConsts.ITEM_ID, None)

    def getPrice(self):
        return self._itemData.get(MarketplaceConsts.ITEM_PRICE, 0)

    def getActions(self):
        return self._itemData.get(MarketplaceConsts.ITEM_ACTIONS, None)

    @staticmethod
    def calculateDiscountForFillCollection(actionData, **kwargs):
        collectionDistributions = kwargs['collectionDistributions']
        collectionStrID = YEARS_INFO.getCollectionSettingID(actionData[MarketplaceConsts.FILL_COLLECTION_SETTING], actionData[MarketplaceConsts.FILL_COLLECTION_YEAR])
        collectionIntID = g_cache.collections[collectionStrID]
        return sum(collectionDistributions[collectionIntID]) * 100 / g_cache.toyCountByCollectionID[collectionIntID]

    @staticmethod
    def calculateDiscountForBuyReward(actionData, **kwargs):
        inventoryChecker = kwargs['inventoryChecker']
        discount = 0
        for discountValue, _, rewardsData in actionData:
            if inventoryChecker(rewardsData):
                discount += discountValue

        return discount

    @staticmethod
    def calculateDiscountForCheckPrevNYLevel(actionData, **kwargs):
        prevNYLevel = kwargs['prevNYLevel']
        return prevNYLevel * 10 if prevNYLevel > 0 else 0

    def calculateDiscount(self, collectionDistributions, inventoryChecker, prevNYLevel):
        discount = 0
        actionsData = self.getActions()
        if actionsData is None:
            return discount
        else:
            params = {'collectionDistributions': collectionDistributions,
             'inventoryChecker': inventoryChecker,
             'prevNYLevel': prevNYLevel}
            for actionName, actionData in actionsData.iteritems():
                discount += self._actionDiscountProcessors[actionName](actionData, **params)

            return discount

    def getTotalPrice(self, collectionDistributions, inventoryChecker, prevNYLevel, discount=None):
        if discount is None:
            discount = self.calculateDiscount(collectionDistributions, inventoryChecker, prevNYLevel)
        defaultPrice = self.getPrice()
        return max(0, defaultPrice - int(ceil(defaultPrice * discount / 100.0)))
