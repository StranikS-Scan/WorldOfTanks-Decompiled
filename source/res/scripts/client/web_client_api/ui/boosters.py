# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/boosters.py
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from web_client_api import w2c, W2CSchema, Field
from gui.shared import event_dispatcher as shared_events
BOOSTERS_WINDOW_TABS = (0, 1, 2)

class _OpenBoostersWindowSchema(W2CSchema):
    tab_id = Field(required=False, type=int, default=0, validator=lambda i, _: i in BOOSTERS_WINDOW_TABS)


class _ActiveBoostersSchema(W2CSchema):
    filter_types = Field(required=False, type=list)


class BoostersWindowWebApiMixin(object):

    @w2c(_OpenBoostersWindowSchema, 'boosters')
    def openBoostersWindow(self, cmd):
        shared_events.showBoostersWindow(tabID=cmd.tab_id)


class BoostersInfoWebApiMixin(object):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    @w2c(_ActiveBoostersSchema, 'get_active_boosters')
    def getActiveBoosters(self, cmd):
        boosters = [ booster.boosterType for booster in self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values() ]
        if hasattr(cmd, 'filter_types') and cmd.filter_types:
            filterTypes = cmd.filter_types
            if filterTypes:
                return [ boosterType for boosterType in boosters if boosterType in filterTypes ]
        return boosters
