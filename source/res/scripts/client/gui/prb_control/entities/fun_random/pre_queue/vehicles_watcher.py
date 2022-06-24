# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import Configs, BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, server_settings
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class FunRandomVehiclesWatcher(LimitedLevelVehiclesWatcher, ForbiddenVehiclesWatcher):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        super(FunRandomVehiclesWatcher, self).start()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
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

    @server_settings.serverSettingsChangeListener(Configs.FUN_RANDOM_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self._update()
