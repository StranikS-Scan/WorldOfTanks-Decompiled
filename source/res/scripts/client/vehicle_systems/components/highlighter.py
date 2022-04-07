# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
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
        self.__activeArgs = None
        self.__isCommander = True if self.sessionProvider.dynamic.rtsCommander else False
        return

    @property
    def isRTSSelected(self):
        if self.__vehicle is not None:
            rtsCommander = self.sessionProvider.dynamic.rtsCommander
            if rtsCommander is not None:
                return rtsCommander.vehicles.hasEdge(self.__vehicle.id) and not rtsCommander.vehicles.hasForceSimpleEdge(self.__vehicle.id) and rtsCommander.vehicles.get(self.__vehicle.id).isAlly
        return False

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle
        self.__isPlayersVehicle = vehicle.isPlayerVehicle

    def setVehicleOwnership(self):
        if self.isDisabled or self.__vehicle is None:
            return
        else:
            wasPlayerVehicle = self.__isPlayersVehicle
            if BigWorld.player().isObserver():
                self.__isPlayersVehicle = BigWorld.player().vehicle == self.__vehicle
            else:
                self.__isPlayersVehicle = self.__vehicle.isPlayerVehicle
            if wasPlayerVehicle != self.__isPlayersVehicle and not self.__isCommander:
                self.highlight(self.__isPlayersVehicle)
            return

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
        if self.isDisabled or self.__vehicle is None:
            return
        else:
            vehicle = self.__vehicle
            args = (0,
             False,
             1,
             True)
            if enable:
                self.__highlightStatus |= self.HIGHLIGHT_ON
                if self.isRTSSelected:
                    args = (2,
                     False,
                     0,
                     False)
                elif self.__isPlayersVehicle:
                    if forceSimpleEdge:
                        self.__highlightStatus |= self.HIGHLIGHT_SIMPLE
                        args = (0,
                         False,
                         0,
                         False)
                    else:
                        args = (0,
                         False,
                         1,
                         True)
                else:
                    arenaDP = self.sessionProvider.getArenaDP()
                    isAllyTeam = arenaDP.isAllyTeam(vehicle.publicInfo['team'])
                    if not isAllyTeam:
                        args = (1,
                         False,
                         0,
                         False)
                    else:
                        args = (4,
                         False,
                         0,
                         False) if forceSimpleEdge else (2,
                         False,
                         0,
                         False)
            else:
                if self.__isPlayersVehicle and forceSimpleEdge:
                    self.__highlightStatus &= ~self.HIGHLIGHT_SIMPLE
                    args = (0,
                     False,
                     1,
                     True)
                self.__highlightStatus &= ~self.HIGHLIGHT_ON
            self.__doHighlightOperation(self.__highlightStatus, args)
            return

    def __doHighlightOperation(self, status, args):
        if status & self.HIGHLIGHT_ON:
            if self.__activeArgs is None:
                BigWorld.wgAddEdgeDetectEntity(self.__vehicle, self.__collisions, args[0], args[1], args[2], args[3])
            else:
                self.__activeArgs = args
                BigWorld.wgUpdateEdgeDetectEntityColorIndex(self.__vehicle, args[0], True)
        else:
            self.__activeArgs = None
            BigWorld.wgDelEdgeDetectEntity(self.__vehicle)
        return
