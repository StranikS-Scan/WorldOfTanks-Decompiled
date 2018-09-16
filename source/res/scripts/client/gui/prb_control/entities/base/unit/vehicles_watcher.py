# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/vehicles_watcher.py
from UnitBase import UNIT_SLOT
from account_helpers import getAccountDatabaseID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.unit.ctx import AssignUnitCtx
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRentalsController, IIGRController
from skeletons.gui.shared import IItemsCache

class UnitVehiclesWatcher(object):
    itemsCache = dependency.descriptor(IItemsCache)
    rentals = dependency.descriptor(IRentalsController)
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self, entity):
        super(UnitVehiclesWatcher, self).__init__()
        self.__entity = entity

    def init(self):
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehiclesUpdated})
        self.rentals.onRentChangeNotify += self.__onRentUpdated
        self.igrCtrl.onIgrTypeChanged += self.__onIgrRoomChanged

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.rentals.onRentChangeNotify -= self.__onRentUpdated
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrRoomChanged

    def validate(self, update=False):
        items = self.itemsCache.items
        invVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
        vehCDs = invVehicles.keys()
        pInfo = self.__entity.getPlayerInfo()
        if pInfo.isInSlot:
            _, unit = self.__entity.getUnit()
            roster = unit.getRoster()
            if not roster.checkVehicleList(vehCDs, pInfo.slotIdx) and not pInfo.isCommander():
                self.__entity.request(AssignUnitCtx(pInfo.dbID, UNIT_SLOT.REMOVE, 'prebattle/assign'))
        elif update:
            self.__entity.unit_onUnitPlayerVehDictChanged(getAccountDatabaseID())

    def __onVehiclesUpdated(self, vehicles):
        self.validate(update=True)

    def __onRentUpdated(self, vehicles):
        self.validate(update=True)

    def __onIgrRoomChanged(self, roomType, xpFactor):
        self.validate(update=True)
