# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/boosters.py
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from web.web_client_api import w2c, W2CSchema, Field

class _ActiveBoostersSchema(W2CSchema):
    filter_types = Field(required=False, type=list, default=None)


class BoostersInfoWebApiMixin(object):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    @w2c(_ActiveBoostersSchema, 'get_active_boosters')
    def getActiveBoosters(self, cmd):
        return [ {'id': booster.boosterID,
         'type': booster.boosterType,
         'time_remaining': booster.getUsageLeftTime(),
         'formatted_time_remaining': booster.getUsageLeftTimeStr()} for booster in self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values() if cmd.filter_types is None or booster.boosterType in cmd.filter_types ]
