# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/shop_sales_event.py
from helpers import dependency
from skeletons.gui.game_control import IShopSalesEventController
from web.web_client_api import Field, W2CSchema, w2c

class _OpenShopSalesEventViewSchema(W2CSchema):
    url = Field(required=False, type=basestring)
    origin = Field(required=False, type=basestring)


class OpenShopSalesEventViewWebApiMixin(object):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    @w2c(_OpenShopSalesEventViewSchema, 'shop_sales_event')
    def openShopSalesEventWindow(self, cmd):
        self.__shopSales.openMainView(cmd.url, cmd.origin)
