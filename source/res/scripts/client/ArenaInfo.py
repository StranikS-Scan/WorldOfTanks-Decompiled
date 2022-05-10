# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaInfo.py
import BigWorld
from arena_info_components.vehicles_area_marker_info import VehiclesAreaMarkerInfo
from cgf_script.entity_dyn_components import BWEntitiyComponentTracker
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
ARENA_INFO_COMPONENTS = {VehiclesAreaMarkerInfo}

class ArenaInfo(BigWorld.Entity, BWEntitiyComponentTracker, VehiclesAreaMarkerInfo):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        for comp in ARENA_INFO_COMPONENTS:
            comp.__init__(self)

    def set_planeTrajectory(self, _):
        avatar = BigWorld.player()
        if self.planeTrajectory and avatar.userSeesWorld():
            avatar.updatePlaneTrajectory(self.planeTrajectory)

    def showCarpetBombing(self, equipmentID, position, hittingDirection, time):
        avatar = BigWorld.player()
        if avatar is not None:
            avatar.showCarpetBombing(equipmentID, position, hittingDirection, time)
        return

    def onEnterWorld(self, prereqs):
        for comp in ARENA_INFO_COMPONENTS:
            comp.onEnterWorld(self)

        BigWorld.player().arena.registerArenaInfo(self)

    def onLeaveWorld(self):
        for comp in ARENA_INFO_COMPONENTS:
            comp.onLeaveWorld(self)

        BigWorld.player().arena.unregisterArenaInfo(self)
