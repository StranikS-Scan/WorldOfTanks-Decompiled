# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/GoodieTargets.py
from abc import ABCMeta

class GoodieTarget(object):
    __metaclass__ = ABCMeta

    def __init__(self, targetID, limit=None):
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


class GoodieTargetAvatar(GoodieTarget):
    __metaclass__ = ABCMeta


class GoodieTargetVehicle(GoodieTarget):
    __metaclass__ = ABCMeta


class HangarTarget(GoodieTarget):
    __metaclass__ = ABCMeta


class BuyPremiumAccount(HangarTarget):

    def __init__(self, targetID, limit=None):
        super(BuyPremiumAccount, self).__init__(targetID, limit)


class BuySlot(HangarTarget):

    def __init__(self, targetID=None, limit=None):
        super(BuySlot, self).__init__(targetID, limit)


class PostBattle(GoodieTargetVehicle):

    def __init__(self, targetID=None, limit=None):
        super(PostBattle, self).__init__(targetID, limit)


class BuyGoldTankmen(HangarTarget):

    def __init__(self, targetID=None, limit=None):
        super(BuyGoldTankmen, self).__init__(targetID, limit)


class FreeExperienceConversion(HangarTarget):

    def __init__(self, targetID=None, limit=None):
        super(FreeExperienceConversion, self).__init__(targetID, limit)


class BuyVehicle(HangarTarget):

    def __init__(self, targetID, limit=None):
        super(BuyVehicle, self).__init__(targetID, limit)


class EpicMeta(GoodieTargetAvatar):

    def __init__(self, targetID=None, limit=None):
        super(EpicMeta, self).__init__(targetID, limit)


class EpicPostBattle(PostBattle):
    pass


class DemountOptionalDevice(HangarTarget):
    pass


class DropSkill(GoodieTarget):
    pass
