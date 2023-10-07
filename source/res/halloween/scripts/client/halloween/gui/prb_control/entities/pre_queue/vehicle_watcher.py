# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/vehicle_watcher.py
from itertools import chain
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from halloween_common.halloween_constants import HALLOWEEN_GAME_PARAMS_KEY
from skeletons.gui.game_control import IHalloweenController

class HalloweenBattleVehiclesWatcher(LimitedLevelVehiclesWatcher):
    __eventBattleCtrl = dependency.descriptor(IHalloweenController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        super(HalloweenBattleVehiclesWatcher, self).start()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(HalloweenBattleVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLAN_WARS ^ REQ_CRITERIA.VEHICLE.BATTLE_ROYALE ^ REQ_CRITERIA.VEHICLE.EPIC_BATTLE).values()
        return chain.from_iterable((LimitedLevelVehiclesWatcher._getUnsuitableVehicles(self, onClear), vehs))

    def _getValidLevels(self):
        return self.__eventBattleCtrl.getModeSettings().levels

    def __onServerSettingsChanged(self, diff):
        if HALLOWEEN_GAME_PARAMS_KEY in diff:
            self._update()
