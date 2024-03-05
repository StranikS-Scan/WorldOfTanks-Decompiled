# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import BigWorld
from helpers import dependency
from constants import EdgeColorMode, EdgeDrawMode
from skeletons.gui.battle_session import IBattleSessionProvider
from EdgeDrawer import HighlightComponent
import cgf_obsolete_script.py_component

class Highlighter(cgf_obsolete_script.py_component.Component):
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

    def __init__(self, enabled, collisions):
        super(Highlighter, self).__init__()
        self.__vehicle = None
        self.__highlightStatus = self.HIGHLIGHT_OFF if enabled else self.HIGHLIGHT_DISABLED
        self.__isPlayersVehicle = False
        self.__collisions = collisions
        self.__args = (0, EdgeDrawMode.OCCLUDED, True)
        return

    @property
    def _isPlayersVehicle(self):
        return self.__isPlayersVehicle

    @_isPlayersVehicle.setter
    def _isPlayersVehicle(self, value):
        self.__isPlayersVehicle = value

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle
        self.__isPlayersVehicle = vehicle.isPlayerVehicle

    def getVehicle(self):
        return self.__vehicle

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
        self.__highlightStatus &= ~self.HIGHLIGHT_DISABLED
        if self.__isPlayersVehicle and self.__vehicle is not None:
            BigWorld.wgAddIgnoredCollisionEntity(self.__vehicle, self.__collisions)
        return

    def deactivate(self):
        self.removeHighlight()
        self.__highlightStatus |= self.HIGHLIGHT_DISABLED
        if self.__isPlayersVehicle and self.__vehicle is not None:
            BigWorld.wgDelIgnoredCollisionEntity(self.__vehicle)
        return

    def destroy(self):
        self.deactivate()
        self.__highlightStatus = self.HIGHLIGHT_DISABLED
        self.__vehicle = None
        return

    def removeHighlight(self):
        if self.isOn and self.__vehicle is not None and not self.isDisabled:
            self.__highlightStatus &= ~self.HIGHLIGHT_ON
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
        return

    def highlight(self, enable, forceSimpleEdge=False):
        if bool(enable) == bool(self.isOn):
            return
        elif self.isDisabled or self.__vehicle is None:
            return
        else:
            vehicle = self.__vehicle
            args = self.__args
            highlightStatus = self.__highlightStatus
            if enable:
                highlightStatus |= self.HIGHLIGHT_ON
                if self.__isPlayersVehicle:
                    if forceSimpleEdge:
                        highlightStatus |= self.HIGHLIGHT_SIMPLE
                        args = (0, EdgeDrawMode.FULL, False)
                    else:
                        args = (0, EdgeDrawMode.OCCLUDED, True)
                else:
                    arenaDP = self.sessionProvider.getArenaDP()
                    isAllyTeam = arenaDP.isAllyTeam(vehicle.publicInfo['team'])
                    drawMode = EdgeDrawMode.FULL
                    if isAllyTeam:
                        colorMode = EdgeColorMode.ALLY
                    else:
                        colorMode = EdgeColorMode.ENEMY
                    args = (colorMode, drawMode, False)
            else:
                if self.__isPlayersVehicle and forceSimpleEdge:
                    highlightStatus &= ~self.HIGHLIGHT_SIMPLE
                    args = (0, EdgeDrawMode.OCCLUDED, True)
                highlightStatus &= ~self.HIGHLIGHT_ON
            if highlightStatus != self.__highlightStatus or args != self.__args:
                self.__doHighlightOperation(highlightStatus, args)
                self.__highlightStatus = highlightStatus
                self.__args = args
            return

    def __doHighlightOperation(self, status, args):
        if status & self.HIGHLIGHT_ON:
            BigWorld.wgAddEdgeDetectEntity(self.__vehicle, self.__collisions, args[0], args[1], args[2])
        else:
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
        self.__updateHighlightComponent(status, args)

    def __updateHighlightComponent(self, status, args):
        appearance = self.__vehicle.appearance
        if appearance is not None:
            root = appearance.gameObject
            highlight = root.findComponentByType(HighlightComponent)
            if highlight is not None:
                root.removeComponent(highlight)
            if status & self.HIGHLIGHT_ON:
                root.createComponent(HighlightComponent, args[0], args[1], args[2], False)
        return
