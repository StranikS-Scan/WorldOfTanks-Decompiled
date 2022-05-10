# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/regular/pre_queue/vehicles_watcher.py
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class BattleRoyaleVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE).itervalues()
        return vehs
