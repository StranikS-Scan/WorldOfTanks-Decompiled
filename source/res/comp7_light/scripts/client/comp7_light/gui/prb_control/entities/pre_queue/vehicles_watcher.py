# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/pre_queue/vehicles_watcher.py
from itertools import chain
import typing
from comp7_light_constants import BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7_LIGHT, Configs
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import LimitedLevelVehiclesWatcher, RestrictedVehiclesWatcher
from helpers import dependency, server_settings
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class Comp7LightVehiclesWatcher(LimitedLevelVehiclesWatcher, RestrictedVehiclesWatcher):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7_LIGHT

    def start(self):
        super(Comp7LightVehiclesWatcher, self).start()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(Comp7LightVehiclesWatcher, self).stop()

    def _getUnsuitableVehicles(self, onClear=False):
        return chain.from_iterable((LimitedLevelVehiclesWatcher._getUnsuitableVehicles(self, onClear), RestrictedVehiclesWatcher._getUnsuitableVehicles(self, onClear), self._getUnsuitableVehiclesBase()))

    def _getForbiddenVehicleClasses(self):
        return self.__comp7LightController.getModeSettings().forbiddenClassTags

    def _getForbiddenVehicleTypes(self):
        return self.__comp7LightController.getModeSettings().forbiddenVehTypes

    def _getValidLevels(self):
        return self.__comp7LightController.getModeSettings().levels

    @server_settings.serverSettingsChangeListener(Configs.COMP7_LIGHT_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self._update()
