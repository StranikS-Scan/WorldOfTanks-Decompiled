# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/promo.py


class IPromoLogger(object):

    def logAction(self, **kwargs):
        raise NotImplementedError

    def logTeaserAction(self, teaserData, **kwargs):
        raise NotImplementedError

    def getLoggingFuture(self, teaserData=None, **kwargs):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
