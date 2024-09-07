# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/armory_shop.py
from web.web_client_api import W2CSchema, w2c
from debug_utils import LOG_WARNING

class ArmoryShopWebApiMixin(object):

    @w2c(W2CSchema, 'armory_yard_shop')
    def openArmoryShopView(self, _):
        try:
            from armory_yard.gui.window_events import showArmoryYardShopWindow
            showArmoryYardShopWindow()
        except ImportError:
            LOG_WARNING('ArmoryYardShopWindow is not found')
