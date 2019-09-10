# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/techtree.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from gui.shared import event_dispatcher, events
from skeletons.gui.shared import IItemsCache
from web.web_client_api import W2CSchema, w2c, Field

class _OpenTechTreeSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)


class TechTreeTabWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_OpenTechTreeSchema, 'tech_tree')
    def openTechTree(self, cmd):
        event_dispatcher.showTechTree(cmd.vehicle_id)

    @w2c(_OpenTechTreeSchema, 'research')
    def openResearch(self, cmd):
        vehicle = self.itemsCache.items.getStockVehicle(cmd.vehicle_id)
        exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': vehicle.nationName})
        event_dispatcher.showResearchView(cmd.vehicle_id, exitEvent=exitEvent)
