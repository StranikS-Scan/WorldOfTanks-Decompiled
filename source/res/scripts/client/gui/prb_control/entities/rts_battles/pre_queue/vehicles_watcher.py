# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_battles/pre_queue/vehicles_watcher.py
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IRTSBattlesController

class RTSVehiclesWatcher(BaseVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, isCommander):
        super(RTSVehiclesWatcher, self).__init__()
        self.__isCommander = isCommander

    def start(self):
        super(RTSVehiclesWatcher, self).start()
        self.__rtsController.onControlModeChanged += self.__onControlModeChanged

    def stop(self):
        self.__rtsController.onControlModeChanged -= self.__onControlModeChanged
        super(RTSVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        if onClear:
            return self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        if self.__isCommander:
            unsuitableCriteria = self.__rtsController.getUnsuitableRosterCriteria(ARENA_BONUS_TYPE.RTS)
        else:
            unsuitableCriteria = self.__rtsController.getUnsuitableVehicleCriteria(ARENA_BONUS_TYPE.RTS)
        return self.__itemsCache.items.getVehicles(unsuitableCriteria).itervalues()

    def __onControlModeChanged(self, isCommander):
        if self._isWatching:
            clearIDs = self._clearCustomsStates(asTransaction=True)
            self.__isCommander = isCommander
            setIDs = self._setCustomStates(asTransaction=True)
            notifyIDs = clearIDs | setIDs
            if notifyIDs:
                g_prbCtrlEvents.onVehicleClientStateChanged(notifyIDs)
