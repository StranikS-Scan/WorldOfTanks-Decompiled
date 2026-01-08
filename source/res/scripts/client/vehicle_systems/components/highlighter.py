# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import weakref
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from EdgeDrawer import EdgeHighlightComponent
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
        self.__vehicleRef = None
        self.__highlightStatus = self.HIGHLIGHT_OFF if enabled else self.HIGHLIGHT_DISABLED
        self.__isPlayersVehicle = False
        self.__collisions = collisions
        return

    def setVehicle(self, vehicle):
        self.__vehicleRef = weakref.ref(vehicle)
        self.__isPlayersVehicle = vehicle.isPlayerVehicle

    def setVehicleOwnership(self):
        if self.isDisabled:
            return
        else:
            vehicle = self.__getVehicle()
            wasPlayerVehicle = self.__isPlayersVehicle
            if vehicle is None:
                self.__isPlayersVehicle = False
            elif BigWorld.player().isObserver():
                self.__isPlayersVehicle = BigWorld.player().vehicle == vehicle
            else:
                self.__isPlayersVehicle = vehicle.isPlayerVehicle
            if wasPlayerVehicle != self.__isPlayersVehicle:
                self.highlight(self.__isPlayersVehicle)
            return

    def activate(self):
        self.__highlightStatus &= ~self.HIGHLIGHT_DISABLED
        vehicle = self.__getVehicle()
        if self.__isPlayersVehicle and vehicle is not None:
            BigWorld.wgAddIgnoredCollisionEntity(vehicle, self.__collisions)
        return

    def deactivate(self):
        self.removeHighlight()
        self.__highlightStatus |= self.HIGHLIGHT_DISABLED
        vehicle = self.__getVehicle()
        if self.__isPlayersVehicle and vehicle is not None:
            BigWorld.wgDelIgnoredCollisionEntity(vehicle)
        return

    def destroy(self):
        self.deactivate()
        self.__highlightStatus = self.HIGHLIGHT_DISABLED
        self.__vehicleRef = None
        return

    def removeHighlight(self):
        vehicle = self.__getVehicle()
        if self.isOn and vehicle is not None and not self.isDisabled:
            self.__highlightStatus &= ~self.HIGHLIGHT_ON
            BigWorld.wgDelEdgeDetectEntity(vehicle)
        return

    def highlight(self, enable, forceSimpleEdge=False):
        if bool(enable) == bool(self.isOn):
            return
        else:
            vehicle = self.__getVehicle()
            if self.isDisabled or vehicle is None:
                return
            if self.isOn:
                BigWorld.wgDelEdgeDetectEntity(vehicle)
            args = (0,
             False,
             1,
             True)
            if enable:
                self.__highlightStatus |= self.HIGHLIGHT_ON
                if self.__isPlayersVehicle:
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
                    args = (2,
                     False,
                     0,
                     False) if isAllyTeam else (1,
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
            self.__doHighlightOperation(vehicle, self.__highlightStatus, args)
            return

    def __getVehicle(self):
        return self.__vehicleRef() if self.__vehicleRef is not None else None

    def __doHighlightOperation(self, vehicle, status, args):
        if not status & self.HIGHLIGHT_ON:
            BigWorld.wgDelEdgeDetectEntity(vehicle)
        self.__updateHighlightComponent(vehicle, status, args)

    def __updateHighlightComponent(self, vehicle, status, args):
        appearance = vehicle.appearance
        if appearance is not None:
            isOn = status & self.HIGHLIGHT_ON
            root = appearance.gameObject
            if root is None or not root.isValid():
                return
            highlight = root.findComponentByType(EdgeHighlightComponent)
            if highlight is not None:
                root.removeComponent(highlight)
            if isOn:
                root.createComponent(EdgeHighlightComponent, args[0], args[1], args[2], args[3])
        return
