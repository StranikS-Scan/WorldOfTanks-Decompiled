# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamInfo.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class TeamInfo(BigWorld.Entity):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onCombatEquipmentUsed(self, vehicleID, equipmentID):
        self.__sessionProvider.shared.equipments.onCombatEquipmentUsed(vehicleID, equipmentID)

    def onEnterWorld(self, prereqs):
        LOG_DEBUG_DEV('[TeamInfo] onEnterWorld: team = {}'.format(self.teamID))
        BigWorld.player().arena.registerTeamInfo(self)

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('[TeamInfo] onLeaveWorld: team = {}'.format(self.teamID))
        BigWorld.player().arena.unregisterTeamInfo(self)

    def onDynamicComponentCreated(self, component):
        LOG_DEBUG_DEV('Component created', component)

    def showHittingArea(self, equipmentID, hittingPoint, hittingDirection, hittingTime):
        BigWorld.player().showHittingArea(equipmentID, hittingPoint, hittingDirection, hittingTime)
