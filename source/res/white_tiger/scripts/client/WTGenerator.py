# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTGenerator.py
import BigWorld
from Capturable import Capturable
from WTGeneratorActivation import WTGeneratorActivationComponent, WTGeneratorCapturedComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import IS_VS_EDITOR
from white_tiger_common.wt_constants import WTGeneratorState, WT_GENERATOR_MAX_PROGRESS
if not IS_VS_EDITOR:
    from shared_utils import nextTick
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
    from WhiteTigerComponents import WTGeneratorProgressComponent
    from white_tiger.cgf_components.wt_helpers import getBattleStateComponent

class WTGenerator(Capturable):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTGenerator, self).__init__()
        self.__marker = None
        self.__minimapMarker = None
        self.__generatorMarker = None
        return

    def set_activationProgress(self, prev):
        activation = self.activationProgress
        generatorID = self.__getIndex()
        gameObject = self.entity.entityGameObject
        if activation.progress > 0:
            if activation.timeLeft <= 0 and activation.progress >= WT_GENERATOR_MAX_PROGRESS:
                self.__createCapturedComponent(gameObject)
            self.__updateMarker(self.__generatorMarker, generatorID)
            self.__updateMarker(self.__minimapMarker, generatorID)
            self.__updateController(generatorID)
            self.__createProgressComponent(gameObject)
            if prev is None:
                self.activationAdd(activation.invadersVehicleIDs)
            elif len(activation.invadersVehicleIDs) != len(prev.invadersVehicleIDs):
                self.activationRemove(frozenset(prev.invadersVehicleIDs).difference(activation.invadersVehicleIDs))
                self.activationAdd(frozenset(activation.invadersVehicleIDs).difference(prev.invadersVehicleIDs))
            elif prev.progress > activation.progress:
                self.updateFirstDamaged(activation.invadersVehicleIDs)
        elif prev is not None:
            self.__updateController(generatorID)
            self.__stopCapture()
            self.activationRemove(prev.invadersVehicleIDs)
            gameObject.removeComponentByType(WTGeneratorProgressComponent)
        return

    def set_state(self, prev):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.receiveGeneratorStatus(self.__getIndex(), self.state, self.entity.id, self.blockedByMiniboss)

    def updateFirstDamaged(self, vIds):
        for veh in [ BigWorld.entities[vId] for vId in vIds if BigWorld.entities.has_key(vId) ]:
            activation = veh.entityGameObject.findComponentByType(WTGeneratorActivationComponent)
            if activation and activation.wasDamaged:
                self.activationRemove([veh.id])
                self.activationAdd([veh.id])
                return

    def activationAdd(self, added):
        gameObject = self.entity.entityGameObject
        for veh in [ BigWorld.entities[vId] for vId in added if BigWorld.entities.has_key(vId) ]:
            veh.entityGameObject.createComponent(WTGeneratorActivationComponent, gameObject)

    def activationRemove(self, removed):
        for veh in [ BigWorld.entities[vId] for vId in removed if BigWorld.entities.has_key(vId) ]:
            veh.entityGameObject.removeComponentByType(WTGeneratorActivationComponent)

    def updateMarkers(self):
        nextTick(self.__updateMarkers)()

    def _onAvatarReady(self):
        self.set_activationProgress(None)
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            if self.state != WTGeneratorState.CAPTURED:
                battleStateComponent.receiveSentinelData(self.__getIndex(), self.sentinelData)
            battleStateComponent.receiveGeneratorStatus(self.__getIndex(), self.state, self.entity.id, False, True)
            if self.state == WTGeneratorState.BLOCKED:
                battleStateComponent.receiveGeneratorCaptureInProgress(self.__getIndex(), self.activationProgress, self.state)
        nextTick(self.__updateMarkers)()
        return

    def __fetchMarkers(self):
        self.__marker = self.__fetchMarkerID()
        if not self.__marker:
            return
        self.__minimapMarker = self.__fetchMiniMapMarkerComponent(self.__marker)
        self.__generatorMarker = self.__fetchGeneratorMarkerComponent(self.__marker)

    def __updateMarkers(self):
        if self.state == WTGeneratorState.CAPTURED:
            return
        self.__fetchMarkers()
        generatorID = self.__getIndex()
        isBlocked = self.state == WTGeneratorState.BLOCKED
        if self.__generatorMarker:
            self.__generatorMarker.onGeneratorLocked(generatorID, isBlocked)
        if self.__minimapMarker:
            self.__minimapMarker.onGeneratorLocked(generatorID, isBlocked)

    def __getIndex(self):
        return self.entity.indexPool.index

    def __stopCapture(self):
        generatorID = self.__getIndex()
        if self.__generatorMarker:
            self.__generatorMarker.onGeneratorStopCapture(generatorID)
        if self.__minimapMarker:
            self.__minimapMarker.onGeneratorStopCapture(generatorID)
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.receiveGeneratorStatus(self.__getIndex(), self.state, self.entity.id)

    def __fetchMarkerID(self):
        if 'entityMarker' in self.entity.dynamicComponents:
            ctrl = self.__guiSessionProvider.shared.areaMarker
            if ctrl:
                marker = ctrl.getMarkerById(self.entity.entityMarker.markerID)
                return marker
        return None

    def __fetchGeneratorMarkerComponent(self, marker):
        if marker.hasMarker2D():
            components = marker.getComponentByType(ComponentBitMask.MARKER_2D)
            if components:
                return components[0]
        return None

    def __fetchMiniMapMarkerComponent(self, marker):
        if marker.hasMinimap():
            components = marker.getComponentByType(ComponentBitMask.MINIMAP_MARKER)
            return components[0]
        else:
            return None

    def __updateMarker(self, marker, generatorID):
        if not marker:
            return
        activation = self.activationProgress
        numInvaders = len(activation.invadersVehicleIDs)
        marker.onGeneratorCapture(generatorID, activation.progress, activation.timeLeft, numInvaders)

    def __updateController(self, generatorID):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.receiveGeneratorCaptureInProgress(generatorID, self.activationProgress, self.state)

    def __createProgressComponent(self, gameObject):
        if gameObject.findComponentByType(WTGeneratorProgressComponent) is not None:
            return
        else:
            gameObject.createComponent(WTGeneratorProgressComponent, lambda : self.activationProgress.progress, lambda : self.activationProgress.timeLeft)
            return

    def __createCapturedComponent(self, gameObject):
        if gameObject.findComponentByType(WTGeneratorCapturedComponent) is not None:
            return
        else:
            gameObject.createComponent(WTGeneratorCapturedComponent, self.activationProgress.invadersVehicleIDs)
            return

    def set_sentinelData(self, sentinelData):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.receiveSentinelData(self.__getIndex(), self.sentinelData)

    def invokeCaptureReset(self):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.receiveGeneratorStopCaptureProgress(self.__getIndex(), self.state)

    def set_numInvaders(self, prevNum):
        if self.state != WTGeneratorState.BLOCKED:
            return
        if prevNum == 0 and self.numInvaders > 0:
            self.__updateController(self.__getIndex())
        elif prevNum > 0 and self.numInvaders == 0:
            self.invokeCaptureReset()
