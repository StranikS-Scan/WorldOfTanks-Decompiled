# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/vehicles_watcher.py
import typing
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _TAGS
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class WhiteTigerBattlesSquadVehiclesWatcher(BaseVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({_TAGS.EVENT_HUNTER})).values()
        return vehs
