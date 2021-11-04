# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop_sales_event/commands.py
from helpers import dependency
from skeletons.gui.game_control import IShopSalesEventController
from web.common import formatShopSalesInfo
from web.web_client_api import Field, W2CSchema, w2c

class _SetFavoritesCountSchema(W2CSchema):
    count = Field(required=True, type=int, validator=lambda value, _: value >= 0)


class ShopSalesEventWebApiMixin(object):
    __shopSalesEvent = dependency.descriptor(IShopSalesEventController)

    @w2c(W2CSchema, 'get_info')
    def getEventInfo(self, _):
        return formatShopSalesInfo()

    @w2c(W2CSchema, 'reroll_bundle')
    def reRollBundle(self, _):
        currentBundleID, currentBundleReRolls = yield self.__shopSalesEvent.reRollBundle()
        yield {'id': currentBundleID,
         'rerolls': currentBundleReRolls}

    @w2c(_SetFavoritesCountSchema, 'set_favorites_count')
    def setFavoritesCount(self, cmd):
        self.__shopSalesEvent.setFavoritesCount(cmd.count)
