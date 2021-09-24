# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/boss_info_ctrl.py
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from skeletons.gui.battle_session import IBattleSessionProvider

class BossInfoController(ViewComponentsController, IArenaVehiclesController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getControllerID(self):
        return BATTLE_CTRL_ID.BOSS_INFO_CTRL

    def startControl(self, *_):
        pass

    def stopControl(self):
        pass

    def setViewComponents(self, *components):
        super(BossInfoController, self).setViewComponents(*components)
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if VEHICLE_TAGS.EVENT_BOSS in vInfo.vehicleType.tags:
                self.__setupBossInfo(vInfo)
                break

    def addVehicleInfo(self, vInfo, _):
        if VEHICLE_TAGS.EVENT_BOSS in vInfo.vehicleType.tags:
            self.__setupBossInfo(vInfo)

    def __setupBossInfo(self, bossInfo):
        for component in self._viewComponents:
            component.setupBossInfo(bossInfo)
