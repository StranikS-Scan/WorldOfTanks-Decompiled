# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/carousel/handlers.py
from logging import getLogger
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from gui.shared import event_dispatcher as shared_events
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control import prbDispatcherProperty
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import SimpleVehicleCMHandler
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController
_logger = getLogger(__name__)

class VEHICLE(object):
    STATS = 'showVehicleStatistics'
    TAKE_TEST_DRIVE = 'takeToRent'
    TAKE_RENT = 'takeToRent'


class BRVehicleContextMenuHandler(SimpleVehicleCMHandler):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self, cmProxy, ctx=None):
        handlers = {VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.TAKE_TEST_DRIVE: 'takeToTestDrive',
         VEHICLE.TAKE_RENT: 'takeToRent'}
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
                options.extend([self._makeItem(VEHICLE.STATS, MENU.contextmenu(VEHICLE.STATS), {'enabled': True})])
            rentState = self.__rentVehiclesController.getRentState(self.vehCD)
            if rentState != EquipmentPanelCmpRentStates.STATE_NORMAL:
                testDriveStates = (EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE, EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_ACTIVE)
                rentStates = (EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE, EquipmentPanelCmpRentStates.STATE_RENT_ACTIVE)
                if rentState in testDriveStates:
                    days = self.__rentVehiclesController.getNextTestDriveDaysTotal(self.vehCD)
                    text = backport.text(R.strings.menu.battleRoyale.contextMenu.takeTestDrive(), days=days)
                    options.extend([self._makeItem(VEHICLE.TAKE_TEST_DRIVE, text, {'enabled': rentState == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE})])
                elif rentState in rentStates:
                    isEnough = self.__rentVehiclesController.isEnoughMoneyToPurchase(self.vehCD)
                    isEnabled = rentState == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE and isEnough
                    days = self.__rentVehiclesController.getNextRentDaysTotal(self.vehCD)
                    text = backport.text(R.strings.menu.battleRoyale.contextMenu.takeRent(), days=days)
                    options.extend([self._makeItem(VEHICLE.TAKE_RENT, text, {'enabled': isEnabled})])
            return options

    def takeToRent(self):
        self.__rentVehiclesController.purchaseRent(self.vehCD)

    def showVehicleStats(self):
        shared_events.showVehicleStats(self.getVehCD(), 'battleRoyale')
