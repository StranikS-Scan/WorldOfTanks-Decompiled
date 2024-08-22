# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/shop.py
from gui.shared import event_dispatcher, g_eventBus, events
from gui.shared.event_dispatcher import hideWebBrowserOverlay
from web.web_client_api import w2c, W2CSchema, Field

class _OpenShopSchema(W2CSchema):
    path = Field(required=False, type=basestring)


class ShopWebApiMixin(object):

    @w2c(_OpenShopSchema, 'shop')
    def openShop(self, cmd):
        hideWebBrowserOverlay()
        event_dispatcher.showShop(path=cmd.path)

    @w2c(W2CSchema, 'premium_shop_external_browser')
    def openShopExternalBrowser(self, *_):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PREM_SHOP))
