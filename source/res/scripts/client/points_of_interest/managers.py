# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/managers.py
import typing
import CGF
import GenericComponents
import SoundGroups
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from points_of_interest.components import PoiStateComponent, PoiVehicleStateComponent, PoiStateUIListenerComponent, PoiCaptureBlockerStateComponent, PoiStateUpdateMask
from points_of_interest.poi_view_states import PointViewStateUpdater, VehicleViewStateUpdater
from points_of_interest_shared import PoiStatus
_UPDATE_PERIOD = 0.2

class PoiStateManager(CGF.ComponentManager):
    listenersQuery = CGF.QueryConfig(PoiStateUIListenerComponent)

    @onAddedQuery(PoiStateComponent)
    def onPoiStateAdded(self, poiState):
        for comp in self.listenersQuery:
            comp.listener.onPoiAdded(poiState)

        poiState.resetUpdatedFields()

    @onRemovedQuery(PoiStateComponent)
    def onPoiStateRemoved(self, poiState):
        for comp in self.listenersQuery:
            comp.listener.onPoiRemoved(poiState)

        poiState.resetUpdatedFields()

    @onProcessQuery(PoiStateComponent, tickGroup='PostHierarchy', updatePeriod=_UPDATE_PERIOD)
    def onProcess(self, poiState):
        for comp in self.listenersQuery:
            comp.listener.onProcessPoi(poiState)

        poiState.resetUpdatedFields()

    @onAddedQuery(PoiVehicleStateComponent)
    def onPoiVehicleStateAdded(self, vehicleState):
        for comp in self.listenersQuery:
            comp.listener.onPoiEntered(vehicleState.id)

    @onRemovedQuery(PoiVehicleStateComponent)
    def onPoiVehicleStateRemoved(self, vehicleState):
        for comp in self.listenersQuery:
            comp.listener.onPoiLeft(vehicleState.id)


class PoiViewStateManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(PoiViewStateManager, self).__init__(*args)
        self.__pointViewState = None
        self.__vehicleViewState = None
        return

    @onAddedQuery(CGF.GameObject, PoiStateComponent)
    def onPointStateAdded(self, go, pointState):
        if self.__vehicleViewState is not None:
            vehicleState = self.__vehicleViewState.state
            if pointState.id == vehicleState.id:
                vehicleState.pointState = CGF.ComponentLink(go, PoiStateComponent)
                self.__pointViewState = PointViewStateUpdater(pointState)
        return

    @onRemovedQuery(PoiStateComponent)
    def onPointStateRemoved(self, pointState):
        if self.__vehicleViewState is not None:
            vehicleState = self.__vehicleViewState.state
            if pointState.id == vehicleState.id:
                vehicleState.pointState = None
                self.__pointViewState.clear()
                self.__pointViewState = None
        return

    @onAddedQuery(PoiCaptureBlockerStateComponent, PoiVehicleStateComponent)
    def onPoiVehicleStateAdded(self, captureBlockerState, vehicleState):
        self.__vehicleViewState = VehicleViewStateUpdater(captureBlockerState)
        if vehicleState.poiState is not None:
            pointState = vehicleState.poiState()
            self.__pointViewState = PointViewStateUpdater(pointState)
        return

    @onRemovedQuery(PoiCaptureBlockerStateComponent, PoiVehicleStateComponent)
    def onPoiVehicleStateRemoved(self, captureBlockerState, vehicleState):
        if self.__pointViewState is not None:
            self.__pointViewState.clear()
            self.__pointViewState = None
        if self.__vehicleViewState is not None:
            self.__vehicleViewState.clear()
            self.__vehicleViewState = None
        return

    @onProcessQuery(PoiCaptureBlockerStateComponent, PoiVehicleStateComponent, tickGroup='PostHierarchy', updatePeriod=_UPDATE_PERIOD)
    def onProcess(self, captureBlockerState, vehicleState):
        if self.__pointViewState is not None:
            self.__pointViewState.update()
        if self.__vehicleViewState is not None:
            self.__vehicleViewState.update()
        return


class PoiSoundManager(CGF.ComponentManager):
    __POI_STOP_CAPTURE_BY_ENEMY = 'comp_7_siren_off'
    __POI_CAPTURED_BY_ALLY = 'comp_7_point_activated'
    __POI_CAPTURED_BY_ENEMY = 'comp_7_point_lost'
    __POI_START_CAPTURE_BY_ENEMY = 'comp_7_siren_on'
    __POI_AVAILABLE = 'comp_7_point_drone_on'
    __POI_NOT_AVAILABLE = 'comp_7_point_drone_off'

    def __init__(self, *args):
        super(PoiSoundManager, self).__init__(*args)
        self.__poiStates = {}
        self.__soundObjects = {}

    def deactivate(self):
        self.__poiStates.clear()
        for soundObj in self.__soundObjects.itervalues():
            soundObj.stop()
            soundObj.releaseMatrix()

        self.__soundObjects.clear()

    @onAddedQuery(PoiStateComponent, CGF.GameObject)
    def onPoiStateAdded(self, poiState, go):
        self.__update(poiState, go)

    @onRemovedQuery(PoiStateComponent)
    def onPoiStateRemoved(self, poiState):
        self.__poiStates.pop(poiState, None)
        return

    @onProcessQuery(PoiStateComponent, CGF.GameObject, updatePeriod=_UPDATE_PERIOD)
    def onProcess(self, poiState, go):
        if poiState.updatedFields & (PoiStateUpdateMask.STATUS | PoiStateUpdateMask.INVADER):
            self.__update(poiState, go)

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

    @staticmethod
    def __isAllyCapture(invader):
        return bool(invader)

    @staticmethod
    def __play2d(soundName):
        SoundGroups.g_instance.playSound2D(soundName)

    @staticmethod
    def __get3d(soundName, soundObjName, go):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        parent = hierarchy.getTopMostParent(go)
        transform = parent.findComponentByType(GenericComponents.TransformComponent)
        return SoundGroups.g_instance.WWgetSoundPos(soundName, soundObjName, transform.worldPosition) if transform is not None else None
