# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/promo_screens/contexts.py
from typing import TYPE_CHECKING
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.promo_screens.parsers import PromoDataParser
from gui.wgcg.settings import WebRequestDataType
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
if TYPE_CHECKING:
    from typing import Dict

class BasePromoTeaserRequestCtx(CommonWebRequestCtx):
    __loginManager = dependency.descriptor(ILoginManager)

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    @classmethod
    def getAdditionalData(cls):
        return {'additionalData': {'is_steam': cls.__loginManager.isWgcSteam}}


class PromoGetTeaserRequestCtx(BasePromoTeaserRequestCtx):

    def getDataObj(self, incomeData):
        return PromoDataParser.parse(incomeData)

    def getRequestType(self):
        return WebRequestDataType.PROMO_GET_TEASER

    @classmethod
    def getAdditionalData(cls):
        additionalData = super(PromoGetTeaserRequestCtx, cls).getAdditionalData()
        additionalDataParams = additionalData.setdefault('additionalData', {})
        additionalDataParams.update({'number_of_battles': cls.itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()})
        return additionalData


class PromoSendTeaserShownRequestCtx(BasePromoTeaserRequestCtx):

    def __init__(self, promoID, waitingID=''):
        super(PromoSendTeaserShownRequestCtx, self).__init__(waitingID=waitingID)
        self.__promoID = promoID

    def getPromoID(self):
        return self.__promoID

    def getRequestType(self):
        return WebRequestDataType.PROMO_TEASER_SHOWN


class PromoGetUnreadCountRequestCtx(BasePromoTeaserRequestCtx):

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
