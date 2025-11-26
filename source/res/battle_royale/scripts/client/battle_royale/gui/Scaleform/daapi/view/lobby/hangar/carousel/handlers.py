# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/carousel/handlers.py
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control import prbDispatcherProperty
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import SimpleVehicleCMHandler

class VEHICLE(object):
    STATS = 'showVehicleStatistics'


class BRVehicleContextMenuHandler(SimpleVehicleCMHandler):

    def __init__(self, cmProxy, ctx=None):
        handlers = {VEHICLE.STATS: 'showVehicleStats'}
        super(BRVehicleContextMenuHandler, self).__init__(cmProxy, ctx, handlers)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getVehCD(self):
        return self.vehCD

    def getVehInvID(self):
        return self.vehInvID

    def _initFlashValues(self, ctx):
        self.vehInvID = int(ctx.inventoryId)
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        self.vehCD = vehicle.intCD if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self.vehInvID = None
        self.vehCD = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is None:
            return options
        else:
            if BATTLE_ROYALE_STATS_ENABLED:
                accountDossier = self.itemsCache.items.getAccountDossier()
                statsSolo = accountDossier.getBattleRoyaleSoloStats().getVehicle(vehicle.intCD)
                statsSquad = accountDossier.getBattleRoyaleSquadStats().getVehicle(vehicle.intCD)
                battlesCount = statsSolo.getBattlesCount() + statsSquad.getBattlesCount()
                options.extend([self._makeItem(VEHICLE.STATS, MENU.contextmenu(VEHICLE.STATS), {'enabled': battlesCount != 0})])
            return options

    def showVehicleStats(self):
        shared_events.showVehicleStats(self.getVehCD(), 'battleRoyale')
