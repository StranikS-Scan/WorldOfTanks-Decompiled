# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.shared import IItemsCache

class FunRandomVehiclesWatcher(LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        super(FunRandomVehiclesWatcher, self).start()
        self.__funRandomCtrl.onUpdated += self._update

    def stop(self):
        self.__funRandomCtrl.onUpdated -= self._update
        super(FunRandomVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        eventVehiclesTags = BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
        eventVehiclesCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS(eventVehiclesTags)
        return chain.from_iterable((LimitedLevelVehiclesWatcher._getUnsuitableVehicles(self, onClear), ForbiddenVehiclesWatcher._getUnsuitableVehicles(self, onClear), self.__itemsCache.items.getVehicles(eventVehiclesCriteria).itervalues()))

    def _getForbiddenVehicleClasses(self):
        return self.__funRandomCtrl.getModeSettings().forbiddenClassTags

    def _getForbiddenVehicleTypes(self):
        return self.__funRandomCtrl.getModeSettings().forbiddenVehTypes

    def _getValidLevels(self):
        return self.__funRandomCtrl.getModeSettings().levels
