# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/prb_control/entities/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import Configs
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from versus_ai.skeletons.versus_ai_controller import IVersusAIController

class VersusAIVehiclesWatcher(LimitedLevelVehiclesWatcher):
    __versusAICtrl = dependency.descriptor(IVersusAIController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        super(VersusAIVehiclesWatcher, self).start()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(VersusAIVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        eventVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE ^ REQ_CRITERIA.VEHICLE.CLAN_WARS ^ REQ_CRITERIA.VEHICLE.COMP7).itervalues()
        epicVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        forbiddenVehicleTags = self.__versusAICtrl.getConfig().forbiddenVehicleTags
        forbiddenByTagVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(forbiddenVehicleTags)).itervalues()
        return chain.from_iterable((LimitedLevelVehiclesWatcher._getUnsuitableVehicles(self, onClear),
         forbiddenByTagVehs,
         eventVehs,
         epicVehs))

    def _getValidLevels(self):
        return self.__versusAICtrl.getConfig().levels

    @server_settings.serverSettingsChangeListener(Configs.VERSUS_AI_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self._update()
