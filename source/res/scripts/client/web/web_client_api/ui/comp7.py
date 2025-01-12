# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/comp7.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_SHOP_TABS, IS_COMP7_BONS_BANNER_VISITED
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from gui.shared import event_dispatcher
from web.web_client_api import w2c, W2CSchema

class OpenComp7Mixin(object):

    @w2c(W2CSchema, name='open_comp7_page')
    def openComp7Page(self, _):
        event_dispatcher.showComp7ShopPage(selectComp7Hangar=comp7_prb_helpers.selectComp7)

    @w2c(W2CSchema, name='set_is_comp7_bons_banner_visited')
    def setIsComp7BonsBannerVisited(self, _):
        newShopTabsCounter = AccountSettings.getCounters(NEW_SHOP_TABS)
        newShopTabsCounter.update({IS_COMP7_BONS_BANNER_VISITED: True})
        AccountSettings.setCounters(NEW_SHOP_TABS, newShopTabsCounter)
