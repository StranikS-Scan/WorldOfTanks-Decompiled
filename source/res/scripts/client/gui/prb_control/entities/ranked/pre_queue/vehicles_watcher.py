# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/vehicles_watcher.py
import typing
from itertools import chain
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import ForbiddenVehiclesWatcher
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers import dependency, server_settings
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class RankedVehiclesWatcher(ForbiddenVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def start(self):
        super(RankedVehiclesWatcher, self).start()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(RankedVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        allVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        config = self.__lobbyContext.getServerSettings().rankedBattles
        vehLevels = range(MIN_VEHICLE_LEVEL, config.minLevel) + range(config.maxLevel + 1, MAX_VEHICLE_LEVEL + 1)
        baseVehs = super(RankedVehiclesWatcher, self)._getUnsuitableVehicles(onClear)
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        eventVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        battleRoyaleVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BATTLE_ROYALE).itervalues()
        clanWarsVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLAN_WARS).itervalues()
        comp7Vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.COMP7).itervalues()
        randomOnlyVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.RANDOM_ONLY).itervalues()
        return chain(vehs, baseVehs, eventVehs, epicVehs, battleRoyaleVehs, clanWarsVehs, comp7Vehs, randomOnlyVehs) if not onClear else allVehs

    def _getForbiddenVehicleClasses(self):
        return self.__lobbyContext.getServerSettings().rankedBattles.forbiddenClassTags

    def _getForbiddenVehicleTypes(self):
        return self.__lobbyContext.getServerSettings().rankedBattles.forbiddenVehTypes

    @server_settings.serverSettingsChangeListener('ranked_config')
    def __onServerSettingsChanged(self, diff):
        self._update()
