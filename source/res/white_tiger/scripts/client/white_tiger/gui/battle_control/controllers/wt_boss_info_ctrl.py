# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/wt_boss_info_ctrl.py
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.wt_event.wt_event_helpers import getBossType

class WTBossInfoController(ViewComponentsController, IArenaVehiclesController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getControllerID(self):
        return BATTLE_CTRL_ID.BOSS_INFO_CTRL

    def startControl(self, *_):
        pass

    def stopControl(self):
        pass

    def setViewComponents(self, *components):
        super(WTBossInfoController, self).setViewComponents(*components)
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            bossType = getBossType(vInfo.vehicleType.tags)
            if bossType is not None:
                self.__setupBossInfo(vInfo)
                break

        return

    def addVehicleInfo(self, vInfo, _):
        if VEHICLE_TAGS.WT_BOSS in vInfo.vehicleType.tags:
            self.__setupBossInfo(vInfo)

    def invalidateVehiclesStats(self, arenaDP):
        for vInfo in arenaDP.getVehiclesInfoIterator():
            bossType = getBossType(vInfo.vehicleType.tags)
            if bossType is not None:
                self.__updateBossInfo(vInfo)
                break

        return

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStatsVO in updated:
            vInfo = arenaDP.getVehicleInfo(vStatsVO.vehicleID)
            bossType = getBossType(vInfo.vehicleType.tags)
            if bossType is not None:
                self.__updateBossInfo(vInfo)

        return

    def __setupBossInfo(self, bossInfo):
        for component in self._viewComponents:
            component.setupBossInfo(bossInfo)

    def __updateBossInfo(self, bossInfo):
        for component in self._viewComponents:
            component.updateBossInfo(bossInfo)
