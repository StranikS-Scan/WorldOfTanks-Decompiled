# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/goodies.py


class IGoodiesCache(object):
    """
    Global goodies cache. Contains booster and goodie GUI items.
    Uses IItemsCache.items.shop and IItemsCache.items.goodies to create goodies cache
    Listen IItemsCache events and keep cache in valid state
    """

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def personalGoodies(self):
        """
        Gets dynamic parts of goodies received on Account in player data. GoodiesRequester is Inventory analogue.
        """
        raise NotImplementedError

    def getBoosterPriceData(self, boosterID):
        """
        Gets tuple of Booster price, Booster default price, is booster hidden
        """
        raise NotImplementedError

    def getItemByTargetValue(self, targetValue):
        """
        Gets GUI Item by target value
        """
        raise NotImplementedError

    def getActiveBoostersTypes(self):
        """
        Gets active boosters types
        """
        raise NotImplementedError

    def getBooster(self, boosterID):
        """
        Gets booster GUI instance
        """
        raise NotImplementedError

    def getDiscount(self, discoutID):
        """
        Gets personal discount GUI instance
        """
        raise NotImplementedError

    def getBoosters(self, criteria=None):
        """
        Gets boosters GUI instances in format: {boosterID: booster, ...}
        """
        raise NotImplementedError

    def getDiscounts(self, criteria=None):
        """
        Gets personal discounts GUI instances in format: {discountID: discount, ...}
        """
        raise NotImplementedError
