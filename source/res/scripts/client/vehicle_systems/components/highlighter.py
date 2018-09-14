# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import BigWorld
from gui.battle_control import g_sessionProvider
from svarog_script import auto_properties
import svarog_script.py_component

class Highlighter(svarog_script.py_component.Component):
    HIGHLIGHT_OFF = 0
    HIGHLIGHT_SIMPLE = 1
    HIGHLIGHT_ON = 2
    status = property(lambda self: self.__highlightStatus)

    @property
    def enabled(self):
        return self.__highlightStatus != self.HIGHLIGHT_OFF

    def __init__(self):
        super(Highlighter, self).__init__()
        self.__vehicle = None
        self.__highlightStatus = self.HIGHLIGHT_OFF
        return

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle

    def activate(self):
        pass

    def deactivate(self):
        if self.__vehicle is None:
            return
        else:
            if self.__highlightStatus != self.HIGHLIGHT_OFF:
                BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
                self.__highlightStatus = self.HIGHLIGHT_OFF
            self.__vehicle = None
            return

    def destroy(self):
        self.deactivate()

    def highlight(self, enable, forceSimpleEdge=False):
        if self.__vehicle is None:
            return
        else:
            vehicle = self.__vehicle
            if self.__highlightStatus != self.HIGHLIGHT_OFF:
                BigWorld.wgDelEdgeDetectEntity(vehicle)
            args = (0, 1, True)
            if enable:
                if vehicle.isPlayerVehicle:
                    if forceSimpleEdge:
                        self.__highlightStatus |= self.HIGHLIGHT_SIMPLE
                        args = (0, 0, False)
                    else:
                        self.__highlightStatus |= self.HIGHLIGHT_ON
                        args = (0, 1, True)
                else:
                    self.__highlightStatus |= self.HIGHLIGHT_ON
                    arenaDP = g_sessionProvider.getArenaDP()
                    isAllyTeam = arenaDP.isAllyTeam(vehicle.publicInfo['team'])
                    args = (2, 0, False) if isAllyTeam else (1, 0, False)
            elif vehicle.isPlayerVehicle and forceSimpleEdge:
                self.__highlightStatus &= ~self.HIGHLIGHT_SIMPLE
                args = (0, 1, True)
            else:
                self.__highlightStatus &= ~self.HIGHLIGHT_ON
            self.__doHighlightOperation(self.__highlightStatus, args)
            return

    def __doHighlightOperation(self, status, args):
        if status != self.HIGHLIGHT_OFF:
            BigWorld.wgAddEdgeDetectEntity(self.__vehicle, args[0], args[1], args[2])
        else:
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
