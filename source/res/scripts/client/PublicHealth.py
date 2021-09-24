# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PublicHealth.py
from debug_utils import LOG_DEBUG_DEV
from script_component.ScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class PublicHealth(DynamicScriptComponent):

    def __init__(self):
        LOG_DEBUG_DEV('[PublicHealth] __init__')
        super(PublicHealth, self).__init__()

    def onAvatarReady(self):
        for healthInfo in self.healthInfoList:
            self.__setVehicleHealth(healthInfo)

    def setNested_healthInfoList(self, path, prev):
        self.__setVehicleHealth(self.healthInfoList[path[0]])

    def setSlice_healthInfoList(self, path, prev):
        self.__setVehicleHealth(self.healthInfoList[path[0][0]])

    def __setVehicleHealth(self, healthInfo):
        LOG_DEBUG_DEV('[PublicHealth] __setVehicleHealth', healthInfo)
        guiSessionProvider = dependency.instance(IBattleSessionProvider)
        guiSessionProvider.setVehicleHealth(False, healthInfo.vehicleID, healthInfo.health, 0, 0)
