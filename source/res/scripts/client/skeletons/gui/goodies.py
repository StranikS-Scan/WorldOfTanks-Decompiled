# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/goodies.py


class IGoodiesCache(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def personalGoodies(self):
        raise NotImplementedError

    def getBoosterPriceData(self, boosterID):
        raise NotImplementedError

    def getItemByTargetValue(self, targetValue):
        raise NotImplementedError

    def getActiveBoostersTypes(self):
        raise NotImplementedError

    def getBooster(self, boosterID):
        raise NotImplementedError

    def haveBooster(self, boosterID):
        raise NotImplementedError

    def getDiscount(self, discoutID):
        raise NotImplementedError

    def getDemountKit(self, demountKitID=None, currency=None):
        raise NotImplementedError

    def getGoodieByID(self, goodieID):
        raise NotImplementedError

    def getBoosters(self, criteria=None):
        raise NotImplementedError

    def getDiscounts(self, criteria=None):
        raise NotImplementedError

    def getDemountKits(self, criteria=None):
        raise NotImplementedError

    def getClanReserves(self):
        raise NotImplementedError
