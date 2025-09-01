# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTMapPointSelectorComponent.py
import BigWorld
import Event
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from aih_constants import CTRL_MODE_NAME

class WTMapPointSelectorComponent(DynamicScriptComponent):
    onVehicleRespawned = Event.Event()
    onSetEndTime = Event.Event()
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTMapPointSelectorComponent, self).__init__()
        self.__enableShow = False

    def _onAvatarReady(self):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        BigWorld.player().inputHandler.onCameraChanged += self.onCameraChanged

    def onDestroy(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        BigWorld.player().inputHandler.onCameraChanged -= self.onCameraChanged
        super(WTMapPointSelectorComponent, self).onDestroy()

    def onCameraChanged(self, controlModeName, _):
        if self.entity.health > 0 and self.entity.isCrewActive:
            return
        if not self.__enableShow and controlModeName == CTRL_MODE_NAME.LOOK_AT_KILLER:
            self.__enableShow = True
        if self.__enableShow and controlModeName == CTRL_MODE_NAME.POSTMORTEM:
            self.__enableShow = False
            self.showSelector()

    def choosePoint(self, pointName):
        self.cell.choosePoint(pointName)

    def set_endTime(self, prev):
        self.onSetEndTime(self.entity.id, self.endTime)

    def showSelector(self):
        if not self.endTime:
            return
        elif self.entity.id != BigWorld.player().playerVehicleID:
            return
        else:
            from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
            teleport = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
            if teleport is not None:
                teleport.showSpawnPoints(self.__createPoints(), self.selectedPoint)
            return

    def updateSelector(self):
        if self.entity.id != BigWorld.player().playerVehicleID:
            return
        elif not self.endTime:
            return
        else:
            from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
            teleport = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
            if teleport is not None:
                teleport.updateSpawnPoints(self.__createPoints(), self.selectedPoint)
            return

    def hideSelector(self):
        if not self.endTime:
            return
        elif self.entity.id != BigWorld.player().playerVehicleID:
            return
        else:
            from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
            teleport = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
            if teleport is not None:
                teleport.closeSpawnPoints()
            return

    def __createPoints(self):
        points = [ {'guid': point['name'],
         'position': (point['position'].x, point['position'].y)} for point in self.spawnGroups ]
        return points

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.AFTERBATTLE:
            BigWorld.player().inputHandler.onCameraChanged -= self.onCameraChanged
