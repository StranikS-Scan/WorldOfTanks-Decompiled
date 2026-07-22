# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/web/web_client_api/gold_wagon/gold_wagon.py
from gui.clientgw.gold_wagon.contexts import GoldWagonFetchInfoCtx
from helpers import dependency
from skeletons.gui.web import IWebController
from web.web_client_api import w2c, W2CSchema, w2capi
from mt_birthday.gui.shared.event_dispatcher import showMainView

class GoldWagonWebApiMixin(object):
    __webController = dependency.descriptor(IWebController)

    @w2c(W2CSchema, 'get_info')
    def getInfo(self, cmd):
        result = yield self.__webController.sendRequest(ctx=GoldWagonFetchInfoCtx())
        if result.isSuccess():
            yield {'gold_daily_refill_amount': result.data.get('gold_daily_refill_amount', 0),
             'gold_per_container': result.data.get('gold_per_container', 0)}

    @w2c(W2CSchema, 'show_birthday_main_view')
    def openBirthdayMainView(self, _):
        showMainView()


@w2capi(name='gold_wagon', key='action')
class GoldWagonWebApi(GoldWagonWebApiMixin):
    pass
