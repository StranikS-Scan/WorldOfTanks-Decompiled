# Embedded file name: scripts/common/goodies/GoodieTargets.py


class GoodieTarget(object):

    def __init__(self, targetId):
        self._targetId = targetId

    @property
    def targetId(self):
        return self._targetId

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._targetId == other._targetId

    def __hash__(self):
        return hash(self._targetId)


class BuyPremiumAccount(GoodieTarget):

    def __init__(self, targetId):
        super(BuyPremiumAccount, self).__init__(targetId)


class BuySlot(GoodieTarget):

    def __init__(self, targetId = None):
        super(BuySlot, self).__init__(targetId)


class PostBattle(GoodieTarget):

    def __init__(self, targetId = None):
        super(PostBattle, self).__init__(targetId)
