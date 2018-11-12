# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/shop.py
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.shared import event_dispatcher
from web_client_api import w2c, W2CSchema, Field

class _OpenShopScheme(W2CSchema):
    path = Field(required=False, type=basestring)


class ShopWebApiMixin(object):

    @w2c(_OpenShopScheme, 'shop')
    def openShop(self, cmd):
        if isIngameShopEnabled():
            event_dispatcher.showWebShop(path=cmd.path)
        else:
            event_dispatcher.showOldShop()
