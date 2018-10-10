# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/__init__.py
from actions import ActionsWebApiMixin
from stats import BalanceWebApiMixin
from stock import ItemsWebApiMixin
from trade import TradeWebApiMixin
from web_client_api import w2capi

@w2capi(name='shop', key='action')
class ShopWebApi(ActionsWebApiMixin, BalanceWebApiMixin, ItemsWebApiMixin, TradeWebApiMixin):
    pass
