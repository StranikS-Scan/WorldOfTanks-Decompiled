# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/components.py
import typing
import account_helpers
from constants import VEHICLE_CLASS_INDICES
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.squad.entity import SquadEntity

class RestrictedVehicleClassDataProvider(object):
    __slots__ = ('__unitEntity',)
    _VEHICLE_CLASS_NAME = ''

    def __init__(self):
        self.__unitEntity = None
        return

    def init(self, unitEntity):
        self.__unitEntity = unitEntity

    def fini(self):
        self.__unitEntity = None
        return

    def getMaxVehiclesOfClass(self):
        raise NotImplementedError

    def isVehcleOfClassAvailable(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        availableVehicles = self.getMaxVehiclesOfClass() - self.getCurrentVheiclesOfClassCount()
        if self.getMaxVehiclesOfClass() == 0:
            return False
        if self.__unitEntity.isCommander(accountDbID):
            return True
        if availableVehicles == 0:
            _, _ = self.__unitEntity.getUnit()
            vInfos = self.__unitEntity.getVehiclesInfo()
            for vInfo in vInfos:
                if vInfo.vehClassIdx == VEHICLE_CLASS_INDICES[self._VEHICLE_CLASS_NAME]:
                    return True

            return False
        return availableVehicles > 0

    def hasSlotForVehicleClass(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        return self.getMaxVehiclesOfClass() > 0 and (self.getCurrentVheiclesOfClassCount() < self.getMaxVehiclesOfClass() or self.__unitEntity.isCommander(accountDbID))

    def getCurrentVheiclesOfClassCount(self):
        unitMgrId, unit = self.__unitEntity.getUnit(safe=True)
        return 0 if unit is None else sum((slot.player is not None and slot.player.isReady and slot.vehicle is not None and slot.vehicle.vehClassIdx == VEHICLE_CLASS_INDICES[self._VEHICLE_CLASS_NAME] for slot in self.__unitEntity.getSlotsIterator(unitMgrId, unit)))


class RestrictedSPGDataProvider(RestrictedVehicleClassDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _VEHICLE_CLASS_NAME = VEHICLE_CLASS_NAME.SPG

    def getMaxVehiclesOfClass(self):
        return self.__lobbyContext.getServerSettings().getMaxSPGinSquads()
