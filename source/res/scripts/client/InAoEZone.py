# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/InAoEZone.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from wotdecorators import noexcept

class InAoEZone(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(InAoEZone, self).__init__()
        if self.isVehicleInActiveZone():
            self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AOE_ZONE, self.inAoEZoneData)

    @noexcept
    def setSlice_inAoEZoneData(self, path, old):
        LOG_DEBUG_DEV('setSlice_inAoEZoneData in zone = ', self.isVehicleInActiveZone(), 'new', self.inAoEZoneData, 'path', path)
        self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AOE_ZONE, self.inAoEZoneData)

    def isVehicleInActiveZone(self):
        return len(self.inAoEZoneData) > 0
