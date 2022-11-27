# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop_sales_event/__init__.py
from web.web_client_api import w2capi
from web.web_client_api.shop_sales_event.commands import ShopSalesEventWebApiMixin

@w2capi(name='shop_sales', key='action')
class ShopSalesEventWebApi(ShopSalesEventWebApiMixin):
    pass
