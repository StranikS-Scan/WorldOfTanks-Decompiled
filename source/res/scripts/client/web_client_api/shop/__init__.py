# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/__init__.py
from web_client_api import w2capi
from web_client_api.shop.actions import ActionsWebApiMixin
from web_client_api.shop.stats import BalanceWebApiMixin
from web_client_api.shop.stock import ItemsWebApiMixin
from web_client_api.shop.trade import TradeWebApiMixin

@w2capi(name='shop', key='action')
class ShopWebApi(ActionsWebApiMixin, BalanceWebApiMixin, ItemsWebApiMixin, TradeWebApiMixin):
    pass
