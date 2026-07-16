# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/managers.py
import typing
import CGF
import SoundGroups
from points_of_interest.components import PoiStateComponent, PoiVehicleStateComponent, PoiStateUIListenerComponent, PoiCaptureBlockerStateComponent, PoiStateUpdateMask
from points_of_interest.poi_view_states import PointViewStateUpdater, VehicleViewStateUpdater
from points_of_interest_shared import PoiStatus

class PoiStateCreateSystem(CGF.System):
    StateActivated = CGF.ActivateReaction(CGF.ReactRo(PoiStateComponent))
    StateDeactivated = CGF.DeactivateReaction(CGF.ReactRo(PoiStateComponent))
    StateIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateComponent))
    VehicleStateActivated = CGF.ActivateReaction(CGF.ReactRo(PoiVehicleStateComponent))
    VehicleStateDeactivated = CGF.DeactivateReaction(CGF.ReactRo(PoiVehicleStateComponent))
    VehicleStateIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiVehicleStateComponent))
    ListenersIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateUIListenerComponent))
    Reactions = CGF.Reactions(StateActivated, StateDeactivated, StateIterate, VehicleStateActivated, VehicleStateDeactivated, VehicleStateIterate, ListenersIterate)

    def update(self):
        for state in self.reaction(self.StateDeactivated):
            for listener in self.reaction(self.ListenersIterate):
                listener.listener.onPoiRemoved(state)

            state.resetUpdatedFields()

        for state in self.reaction(self.StateActivated):
            for listener in self.reaction(self.ListenersIterate):
                listener.listener.onPoiAdded(state)

            state.resetUpdatedFields()

        for state in self.reaction(self.VehicleStateDeactivated):
            for listener in self.reaction(self.ListenersIterate):
                listener.listener.onPoiLeft(state.id)

        for state in self.reaction(self.VehicleStateActivated):
            for listener in self.reaction(self.ListenersIterate):
                listener.listener.onPoiEntered(state.id)


class PoiStateUpdateSystem(CGF.System):
    StateIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateComponent))
    ListenersIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateUIListenerComponent))
    StateAccess = CGF.AccessReaction(CGF.Ro(PoiStateComponent))
    Reactions = CGF.Reactions(StateIterate, ListenersIterate, StateAccess)

    def periodUpdate(self):
        for state in self.reaction(self.StateIterate):
            for listener in self.reaction(self.ListenersIterate):
                listener.listener.onProcessPoi(state)

            state.resetUpdatedFields()

    def getStateAccess(self):
        return self.reaction(self.StateAccess)

    def getStates(self):
        return self.reaction(self.StateIterate)


class PoiViewStateSystem(CGF.System):
    PointStateActivated = CGF.ActivateReaction(CGF.ReactRo(PoiStateComponent))
    PointStateIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateComponent))
    PointStateDeactivated = CGF.DeactivateReaction(CGF.ReactRw(PoiStateComponent))
    PointStateAccess = CGF.AccessReaction(CGF.Ro(PoiStateComponent))
    BlockerVehicleStatesActivated = CGF.ActivateReaction(CGF.ReactRo(PoiCaptureBlockerStateComponent), CGF.ReactHas(PoiVehicleStateComponent))
    BlockerVehicleStatesDeactivated = CGF.DeactivateReaction(CGF.ReactRo(PoiCaptureBlockerStateComponent), CGF.ReactRo(PoiVehicleStateComponent))
    BlockerVehicleStatesIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateUIListenerComponent))
    BlockerVehicleStatesAccess = CGF.AccessReaction(CGF.Rw(PoiCaptureBlockerStateComponent))
    Reactions = CGF.Reactions(PointStateActivated, PointStateIterate, PointStateDeactivated, PointStateAccess, BlockerVehicleStatesActivated, BlockerVehicleStatesDeactivated, BlockerVehicleStatesIterate, BlockerVehicleStatesAccess)

    def __init__(self):
        super(PoiViewStateSystem, self).__init__()
        self.__pointViewState = None
        self.__vehicleViewState = None
        return

    def commonUpdate(self):
        for _, __ in self.reaction(self.BlockerVehicleStatesDeactivated):
            if self.__pointViewState:
                self.__pointViewState.clear()
                self.__pointViewState = None
            if self.__vehicleViewState:
                self.__vehicleViewState.clear()
                self.__vehicleViewState = None

        for blockerVehicleState in self.reaction(self.BlockerVehicleStatesActivated):
            self.__vehicleViewState = VehicleViewStateUpdater(blockerVehicleState.object.uuid)
            for pointState in self.reaction(self.PointStateIterate):
                if self.__pointViewStateUpdate(pointState, blockerVehicleState.id):
                    break

        if self.__vehicleViewState:
            blockerVehicleStatesAccess = self.reaction(self.BlockerVehicleStatesAccess)
            blockerVehicleState = self.__vehicleViewState.getState(blockerVehicleStatesAccess)
            for pointState in self.reaction(self.PointStateDeactivated):
                if pointState.id == blockerVehicleState.id:
                    self.__pointViewState.clear()
                    self.__pointViewState = None
                    break

            for pointState in self.reaction(self.PointStateActivated):
                if self.__pointViewStateUpdate(pointState, blockerVehicleState.id):
                    break

        return

    def periodUpdate(self):
        blockerVehicleStatesAccess = self.reaction(self.BlockerVehicleStatesAccess)
        pointStateAccess = self.reaction(self.PointStateAccess)
        for _ in self.reaction(self.BlockerVehicleStatesIterate):
            if self.__pointViewState:
                self.__pointViewState.update(pointStateAccess)
            if self.__vehicleViewState:
                self.__vehicleViewState.update(blockerVehicleStatesAccess)

    def __pointViewStateUpdate(self, pointState, captureBlockerStateID):
        if pointState.id == captureBlockerStateID:
            self.__pointViewState = PointViewStateUpdater(pointState.object.uuid)
            return True
        return False


class PoiSoundSystem(CGF.System):
    __POI_STOP_CAPTURE_BY_ENEMY = 'comp_7_siren_off'
    __POI_CAPTURED_BY_ALLY = 'comp_7_point_activated'
    __POI_CAPTURED_BY_ENEMY = 'comp_7_point_lost'
    __POI_START_CAPTURE_BY_ENEMY = 'comp_7_siren_on'
    __POI_AVAILABLE = 'comp_7_point_drone_on'
    __POI_NOT_AVAILABLE = 'comp_7_point_drone_off'
    StateActivated = CGF.ActivateReaction(CGF.ReactRo(PoiStateComponent), CGF.GameObject)
    StateDeactivated = CGF.DeactivateReaction(CGF.ReactRo(PoiStateComponent))
    StateIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PoiStateComponent), CGF.GameObject)
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    Reactions = CGF.Reactions(StateActivated, StateDeactivated, StateIterate, TransformAccess)

    def __init__(self):
        super(PoiSoundSystem, self).__init__()
        self.__poiStates = {}
        self.__soundObjects = {}

    def onMappingUnloaded(self):
        self.__poiStates.clear()
        for soundObj in self.__soundObjects.itervalues():
            soundObj.stop()
            soundObj.releaseMatrix()

        self.__soundObjects.clear()

    def commonUpdate(self):
        for poiState in self.reaction(self.StateDeactivated):
            self.__poiStates.pop(poiState, None)

        for poiState, go in self.reaction(self.StateActivated):
            self.__update(poiState, go)

        return

    def periodUpdate(self):
        for poiState, go in self.reaction(self.StateIterate):
            if poiState.updatedFields & (PoiStateUpdateMask.STATUS | PoiStateUpdateMask.INVADER):
                self.__update(poiState, go)

    @staticmethod
    def __isAllyCapture(invader):
        return bool(invader)

    @staticmethod
    def __play2d(soundName):
        SoundGroups.g_instance.playSound2D(soundName)

    def __update(self, poiState, go):
        poiID = poiState.id
        statusID = poiState.status.statusID
        invader = poiState.invader
        prevStatusID, prevInvader = self.__poiStates.get(poiID, (None, None))
        if statusID is PoiStatus.CAPTURING and (prevStatusID is not PoiStatus.CAPTURING or invader != prevInvader):
            if not self.__isAllyCapture(invader):
                self.__play3D(self.__POI_START_CAPTURE_BY_ENEMY, poiID, go)
        if prevStatusID is PoiStatus.CAPTURING and (statusID is not PoiStatus.CAPTURING or invader != prevInvader):
            if not self.__isAllyCapture(prevInvader):
                self.__play2d(self.__POI_STOP_CAPTURE_BY_ENEMY)
                self.__stop3D(self.__getSoundObjName(self.__POI_START_CAPTURE_BY_ENEMY, poiID))
        if statusID is PoiStatus.COOLDOWN and prevStatusID is PoiStatus.CAPTURING:
            if self.__isAllyCapture(prevInvader):
                self.__play2d(self.__POI_CAPTURED_BY_ALLY)
            else:
                self.__play2d(self.__POI_CAPTURED_BY_ENEMY)
        if statusID is PoiStatus.ACTIVE and prevStatusID is not PoiStatus.ACTIVE:
            self.__stop3D(self.__getSoundObjName(self.__POI_NOT_AVAILABLE, poiID))
            self.__play3D(self.__POI_AVAILABLE, poiID, go)
        elif statusID is PoiStatus.COOLDOWN and prevStatusID is PoiStatus.CAPTURING:
            self.__stop3D(self.__getSoundObjName(self.__POI_AVAILABLE, poiID))
            self.__play3D(self.__POI_NOT_AVAILABLE, poiID, go)
        self.__poiStates[poiID] = (statusID, invader)
        return None

    def __getSoundObjName(self, soundName, poiID):
        return '{}_{}'.format(soundName, poiID)

    def __play3D(self, soundName, poiID, go):
        soundObjName = self.__getSoundObjName(soundName, poiID)
        soundObj = self.__get3d(soundName, soundObjName, go)
        if soundObj is not None:
            soundObj.play()
            self.__soundObjects[soundObjName] = soundObj
        return

    def __stop3D(self, soundObjName):
        soundObj = self.__soundObjects.pop(soundObjName, None)
        if soundObj is not None:
            soundObj.stop()
            soundObj.releaseMatrix()
        return

    def __get3d(self, soundName, soundObjName, go):
        hs = self.hierarchy
        parent = hs.getTopMostParent(go)
        transformAccess = self.reaction(self.TransformAccess)
        transform = transformAccess.find(parent)
        return SoundGroups.g_instance.WWgetSoundPos(soundName, soundObjName, transform.worldPosition) if transform is not None else None
