# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/hero_tank.py
import typing
from helpers import dependency
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class HBHeroTankController(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)

    def _getConfig(self):
        settings = self._lobbyContext.getServerSettings().getSettings()
        return settings.get(HB_GAME_PARAMS_KEY, {})

    def _getHeroTankData(self):
        eventData = self._getConfig()
        return eventData.get('heroVehicle', {})

    def getVehicleCD(self):
        return self._getHeroTankData().get('vehicleCD', None)

    def getVehicle(self):
        return self._itemsCache.items.getItemByCD(self.getVehicleCD())

    def hasHeroVehicle(self):
        vehicle = self.getVehicle()
        vehicleOwned = vehicle.isPurchased or vehicle.isRestorePossible()
        return vehicleOwned
