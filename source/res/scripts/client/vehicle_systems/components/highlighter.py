# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import svarog_script.py_component

class Highlighter(svarog_script.py_component.Component):
    HIGHLIGHT_OFF = 0
    HIGHLIGHT_SIMPLE = 1
    HIGHLIGHT_ON = 2
    HIGHLIGHT_DISABLED = 4
    status = property(lambda self: self.__highlightStatus)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def isOn(self):
        return self.__highlightStatus & self.HIGHLIGHT_ON and not self.isDisabled

    @property
    def isDisabled(self):
        return self.__highlightStatus & self.HIGHLIGHT_DISABLED

    @property
    def isSimpleEdge(self):
        return self.isOn and self.__highlightStatus & self.HIGHLIGHT_SIMPLE

    def __init__(self, enabled):
        super(Highlighter, self).__init__()
        self.__vehicle = None
        self.__highlightStatus = self.HIGHLIGHT_OFF if enabled else self.HIGHLIGHT_DISABLED
        self.__isPlayersVehicle = False
        return

    def setVehicle(self, vehicle):
        if self.isDisabled:
            return
        self.__vehicle = vehicle
        self.__isPlayersVehicle = vehicle.isPlayerVehicle

    def setVehicleOwnership(self):
        if self.isDisabled:
            return
        wasPlayerVehicle = self.__isPlayersVehicle
        if BigWorld.player().isObserver():
            self.__isPlayersVehicle = BigWorld.player().vehicle == self.__vehicle
        else:
            self.__isPlayersVehicle = self.__vehicle.isPlayerVehicle
        if wasPlayerVehicle != self.__isPlayersVehicle:
            self.highlight(self.__isPlayersVehicle)

    def activate(self):
        pass

    def deactivate(self):
        if self.isDisabled:
            return
        else:
            if self.isOn:
                BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
                self.__highlightStatus &= ~self.HIGHLIGHT_ON
            self.__vehicle = None
            return

    def destroy(self):
        self.deactivate()
        self.__highlightStatus = self.HIGHLIGHT_DISABLED
        self.__vehicle = None
        return

    def removeHighlight(self):
        if self.isOn and self.__vehicle is not None:
            self.__highlightStatus &= ~self.HIGHLIGHT_ON
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
        return

    def highlight(self, enable, forceSimpleEdge=False):
        if self.isDisabled or self.__vehicle is None:
            return
        else:
            vehicle = self.__vehicle
            if self.isOn:
                BigWorld.wgDelEdgeDetectEntity(vehicle)
            args = (0, 1, True)
            if enable:
                self.__highlightStatus |= self.HIGHLIGHT_ON
                if self.__isPlayersVehicle:
                    if forceSimpleEdge:
                        self.__highlightStatus |= self.HIGHLIGHT_SIMPLE
                        args = (0, 0, False)
                    else:
                        args = (0, 1, True)
                else:
                    arenaDP = self.sessionProvider.getArenaDP()
                    isAllyTeam = arenaDP.isAllyTeam(vehicle.publicInfo['team'])
                    args = (2, 0, False) if isAllyTeam else (1, 0, False)
            else:
                if self.__isPlayersVehicle and forceSimpleEdge:
                    self.__highlightStatus &= ~self.HIGHLIGHT_SIMPLE
                    args = (0, 1, True)
                self.__highlightStatus &= ~self.HIGHLIGHT_ON
            self.__doHighlightOperation(self.__highlightStatus, args)
            return

    def __doHighlightOperation(self, status, args):
        if status & self.HIGHLIGHT_ON:
            BigWorld.wgAddEdgeDetectEntity(self.__vehicle, args[0], args[1], args[2])
        else:
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
