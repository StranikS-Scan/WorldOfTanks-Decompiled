# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/store_cm_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import VEHICLE
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_cm_handlers import CommonContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

class VehicleContextMenuHandler(CommonContextMenuHandler):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cmProxy, ctx=None):
        super(VehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.COMPARE: 'compareVehicle'})

    def showVehiclePreview(self):
        shared_events.showVehiclePreview(self.vehCD, VIEW_ALIAS.LOBBY_STORE)

    def compareVehicle(self):
        self.comparisonBasket.addVehicle(self.vehCD)

    def _manageStartOptions(self, options, vehicle):
        options.append(self._makeItem(VEHICLE.INFO, MENU.contextmenu(VEHICLE.INFO), {'enabled': vehicle.isContextMenuEnabled(VEHICLE.INFO)}))
        super(VehicleContextMenuHandler, self)._manageStartOptions(options, vehicle)
        if self.comparisonBasket.isEnabled():
            options.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self.comparisonBasket.isReadyToAdd(self.itemsCache.items.getItemByCD(self.vehCD))}))
