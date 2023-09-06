# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/highlighter.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from EdgeDrawer import HighlightComponent
import CGF
from GenericComponents import DynamicModelComponent
from cgf_script.managers_registrator import autoregister, onProcessQuery
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
        return

    def setVehicle(self, vehicle):
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
            self.__doHighlightOperation(self.__highlightStatus, args)
            return

    def __doHighlightOperation(self, status, args):
        if status & self.HIGHLIGHT_ON:
            BigWorld.wgAddEdgeDetectEntity(self.__vehicle, self.__collisions, args[0], args[1], args[2], args[3])
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
                root.createComponent(HighlightComponent, args[0], args[1], args[2], args[3], False)
        return

    def observeGameObjectForDynamicModels(self, appearance, gameObject):
        hm = CGF.HierarchyManager(appearance.spaceID)
        childComponents = hm.findComponentsInHierarchy(gameObject, DynamicModelComponent)
        for childGO, _ in childComponents:
            childGO.createComponent(EdgeDrawInitializerComponent, self)


class EdgeDrawInitializerComponent(object):
    INITIALIZATION_TIMEOUT_TICKS = 10

    def __init__(self, highlighter):
        self.highlighter = highlighter
        self.ticksProcessed = 0

    def tryInit(self, dynamicModelComponent):
        self.ticksProcessed += 1
        if not dynamicModelComponent.isValid():
            return False
        if self.highlighter.isOn:
            forceSimple = self.highlighter.isSimpleEdge
            self.highlighter.highlight(False)
            self.highlighter.highlight(True, forceSimple)
        return True

    def timeoutOccurred(self):
        return self.ticksProcessed > self.INITIALIZATION_TIMEOUT_TICKS


@autoregister(presentInAllWorlds=True)
class EdgeDrawInitializer(CGF.ComponentManager):

    @onProcessQuery(CGF.GameObject, EdgeDrawInitializerComponent, DynamicModelComponent, period=0.5)
    def processEdgeDrawerInitialization(self, gameObject, edgeDrawInitializerComponent, dynamicModelComponent):
        inited = edgeDrawInitializerComponent.tryInit(dynamicModelComponent)
        if inited or edgeDrawInitializerComponent.timeoutOccurred():
            gameObject.removeComponent(edgeDrawInitializerComponent)
