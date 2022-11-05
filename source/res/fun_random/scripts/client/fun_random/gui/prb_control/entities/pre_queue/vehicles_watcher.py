# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class FunRandomVehiclesWatcher(LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher, FunSubModesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        super(FunRandomVehiclesWatcher, self).start()
        self.startSubSettingsListening(self._update, desiredOnly=True)
        self.startSubSelectionListening(self._update)

    def stop(self):
        self.stopSubSelectionListening(self._update)
        self.stopSubSettingsListening(self._update, desiredOnly=True)
        super(FunRandomVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        eventVehiclesTags = BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
        eventVehiclesCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(eventVehiclesTags)
        return chain.from_iterable((LimitedLevelVehiclesWatcher._getUnsuitableVehicles(self, onClear), ForbiddenVehiclesWatcher._getUnsuitableVehicles(self, onClear), self.__itemsCache.items.getVehicles(eventVehiclesCriteria).itervalues()))

    @hasDesiredSubMode(defReturn=set())
    def _getForbiddenVehicleClasses(self):
        return self.getDesiredSubMode().getSettings().filtration.forbiddenClassTags

    @hasDesiredSubMode(defReturn=set())
    def _getForbiddenVehicleTypes(self):
        return self.getDesiredSubMode().getSettings().filtration.forbiddenVehTypes

    @hasDesiredSubMode(defReturn=())
    def _getValidLevels(self):
        return self.getDesiredSubMode().getSettings().filtration.levels
