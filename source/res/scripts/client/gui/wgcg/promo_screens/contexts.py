# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/promo_screens/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.promo_screens.parsers import PromoDataParser
from gui.wgcg.settings import WebRequestDataType

class PromoGetTeaserRequestCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def getDataObj(self, incomeData):
        return PromoDataParser.parse(incomeData)

    @classmethod
    def getAdditionalData(cls):
        battlesCount = cls.itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        return {'additionalData': {'number_of_battles': battlesCount}}

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.PROMO_GET_TEASER


class PromoSendTeaserShownRequestCtx(CommonWebRequestCtx):

    def __init__(self, promoID, waitingID=''):
        super(PromoSendTeaserShownRequestCtx, self).__init__(waitingID=waitingID)
        self.__promoID = promoID

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def getPromoID(self):
        return self.__promoID

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.PROMO_TEASER_SHOWN


class PromoGetUnreadCountRequestCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.PROMO_GET_UNREAD

    @staticmethod
    def getCount(response):
        return response.getData().get('unread', 0)


class PromoSendActionLogCtx(CommonWebRequestCtx):

    def __init__(self, data, waitingID=''):
        super(PromoSendActionLogCtx, self).__init__(waitingID=waitingID)
        self.__data = data

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.PROMO_SEND_LOG

    def getActionData(self):
        return self.__data
