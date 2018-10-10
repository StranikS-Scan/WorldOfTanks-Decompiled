# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/GoodieTargets.py


class GoodieTarget(object):

    def __init__(self, targetID, limit):
        self._targetID = targetID
        self._limit = limit

    @property
    def targetID(self):
        return self._targetID

    @property
    def limit(self):
        return self._limit

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._targetID == other._targetID

    def __hash__(self):
        return hash(self._targetID)


class BuyPremiumAccount(GoodieTarget):

    def __init__(self, targetID, limit=None):
        super(BuyPremiumAccount, self).__init__(targetID, limit)


class BuySlot(GoodieTarget):

    def __init__(self, targetID=None, limit=None):
        super(BuySlot, self).__init__(targetID, limit)


class PostBattle(GoodieTarget):

    def __init__(self, targetID=None, limit=None):
        super(PostBattle, self).__init__(targetID, limit)


class BuyGoldTankmen(GoodieTarget):

    def __init__(self, targetID=None, limit=None):
        super(BuyGoldTankmen, self).__init__(targetID, limit)


class FreeExperienceConversion(GoodieTarget):

    def __init__(self, targetID=None, limit=None):
        super(FreeExperienceConversion, self).__init__(targetID, limit)


class BuyVehicle(GoodieTarget):

    def __init__(self, targetID, limit=None):
        super(BuyVehicle, self).__init__(targetID, limit)
