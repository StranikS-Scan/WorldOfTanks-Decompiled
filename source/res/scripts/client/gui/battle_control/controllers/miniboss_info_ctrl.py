# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/miniboss_info_ctrl.py
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class MiniBossInfoController(ViewComponentsController, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getControllerID(self):
        return BATTLE_CTRL_ID.MINI_BOSS_INFO_CTRL

    def startControl(self, *_):
        pass

    def stopControl(self):
        pass

    def addVehicleInfo(self, vInfo, _):
        if VEHICLE_TAGS.EVENT_MINI_BOSS in vInfo.vehicleType.tags:
            self.__setupMiniBossInfo(vInfo)

    def __setupMiniBossInfo(self, miniBossInfo):
        for component in self._viewComponents:
            component.setupMiniBossInfo(miniBossInfo)

    def clearViewComponents(self):
        if self.sessionProvider.isReplayPlaying:
            for component in self._viewComponents:
                component.resetMiniBossWidget()

        super(MiniBossInfoController, self).clearViewComponents()
