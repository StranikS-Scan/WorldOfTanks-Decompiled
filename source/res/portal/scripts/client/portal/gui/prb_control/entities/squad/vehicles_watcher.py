# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/squad/vehicles_watcher.py
import typing
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List
    from Vehicle import Vehicle

class PortalVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.PORTAL])).itervalues()
        return vehs
