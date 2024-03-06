# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ApplicationPoint.py
import weakref
import BigWorld
import CGF
import CombatSelectedArea
import GenericComponents
import Math
import math_utils
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from items.artefacts import AoeEffects, AreaShow
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from AreaOfEffect import EffectRunner

def _equipmentEffectFactory(entity):
    equipment = vehicles.g_cache.equipments().get(entity.equipmentID)
    effect = _EQUIPMENT_APPLICATION_POINTS.get(equipment.name)
    return effect(entity, equipment) if effect is not None else None


class ApplicationPoint(BigWorld.Entity):

    def __init__(self):
        super(ApplicationPoint, self).__init__()
        self._effect = _equipmentEffectFactory(self)

    @property
    def areaColor(self):
        return self._effect.equipment.areaColor if self._effect is not None else CombatSelectedArea.COLOR_WHITE

    def prerequisites(self):
        return self._effect.prerequisites() if isinstance(self._effect, EffectRunner) else []

    def onEnterWorld(self, prereqs):
        if self._effect is not None:
            self._effect.onEnterWorld(prereqs)
        return

    def onLeaveWorld(self):
        if self._effect is not None:
            self._effect.onLeaveWorld()
            self._effect = None
        return


class _ApplicationPointEffect(object):
    __slots__ = ('_entity', '_equipment')

    def __init__(self, entity, equipment):
        self._entity = weakref.proxy(entity)
        self._equipment = equipment

    def __del__(self):
        self._entity = None
        self._equipment = None
        return

    @property
    def equipment(self):
        return self._equipment

    def onEnterWorld(self):
        pass

    def onLeaveWorld(self):
        pass


class _Comp7ApplicationPointEffect(_ApplicationPointEffect):
    _VIEW_STATE_DURATION = 0.0
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(_Comp7ApplicationPointEffect, self).__init__(*args, **kwargs)
        self._position = None
        self._direction = None
        self._markerID = None
        self._area = None
        self._vehicle = None
        self.__areaGO = None
        self._callbackDelayer = CallbackDelayer()
        return

    def onEnterWorld(self, prereqs):
        self._updateViewState()
        self._updateCoordinates()
        self._vehicle = BigWorld.entities.get(self._entity.vehicleID)
        if self._isVisible():
            duration = self._getAreaDuration()
            if duration > 0:
                self._createArea(duration)
                self._createMarker(duration)
        equipmentsCtrl = self._guiSessionProvider.shared.equipments
        if equipmentsCtrl:
            equipmentsCtrl.onEquipmentAreaCreated(self._equipment, self._entity.position, self._entity.launchTime + self._equipment.delay, self._entity.level)

    def onLeaveWorld(self):
        self._clearArea()
        self._clearMarker()
        self._callbackDelayer.destroy()

    def _getAreaDuration(self):
        return self._entity.launchTime + self._equipment.delay - BigWorld.serverTime()

    def _getViewStateDuration(self):
        return self._VIEW_STATE_DURATION

    def _getFeedbackEventId(self):
        raise NotImplementedError

    def _createMarker(self, duration):
        pass

    def _clearMarker(self):
        pass

    def _createArea(self, duration):
        radius = self._getRadius()
        areaSize = Math.Vector2(radius * 2, radius * 2)
        self._area = BigWorld.player().createEquipmentSelectedArea(self._position, self._direction, self._equipment, areaSize)
        self._callbackDelayer.delayCallback(duration, self._clearArea)
        if self._equipment.areaUsedPrefab:
            CGF.loadGameObjectIntoHierarchy(self._equipment.areaUsedPrefab, self._entity.entityGameObject, Math.Vector3(), self.__onAreaGOLoaded)

    def _clearArea(self):
        if self._area is not None:
            self._area.destroy()
            self._area = None
        if self.__areaGO is not None:
            CGF.removeGameObject(self.__areaGO)
            self.__areaGO = None
        return

    def _updateViewState(self):
        endTime = self._entity.launchTime + self._getViewStateDuration()
        if endTime < BigWorld.serverTime():
            return
        state = {'endTime': endTime,
         'duration': self._getViewStateDuration()}
        self._guiSessionProvider.shared.feedback.invalidateBuffEffect(feedbackEventID=self._getFeedbackEventId(), vehicleID=self._entity.vehicleID, data=state)

    def _updateCoordinates(self):
        matrix = Math.Matrix(self._entity.matrix)
        self._position = matrix.translation
        self._direction = matrix.applyVector(Math.Vector3(0.0, 0.0, 1.0))

    def _isEnemy(self):
        vInfo = self._guiSessionProvider.getArenaDP().getVehicleInfo(self._entity.vehicleID)
        return vInfo.team != BigWorld.player().team

    def _isVisible(self):
        vInfo = self._guiSessionProvider.getArenaDP().getVehicleInfo(self._entity.vehicleID)
        return vInfo.team == avatar_getter.getObserverTeam() or vInfo.isObserver()

    def _getRadius(self):
        return self._equipment.getRadiusBasedOnSkillLevel(self._entity.level)

    def __onAreaGOLoaded(self, gameObject):
        if self._entity.isDestroyed:
            return
        self.__areaGO = gameObject
        t = gameObject.findComponentByType(GenericComponents.TransformComponent)
        floatEpsilon = 0.001
        t.transform = math_utils.createSRTMatrix(Math.Vector3(self._getRadius(), 1.0, self._getRadius()), (0.0, 0.0, 0.0), (0.0, floatEpsilon, 0.0))


class _Comp7ReconApplicationPointEffect(_Comp7ApplicationPointEffect):
    _VIEW_STATE_DURATION = 5.0
    _COMP7_RECON_MARKER = 'COMP7_RECON'

    def _getFeedbackEventId(self):
        return FEEDBACK_EVENT_ID.VEHICLE_POINT_RECON

    def _createMarker(self, duration):
        ctrl = self._guiSessionProvider.shared.areaMarker
        if ctrl is not None:
            marker = ctrl.createMarker(self._entity.matrix, self._COMP7_RECON_MARKER)
            self._markerID = ctrl.addMarker(marker)
            self._callbackDelayer.delayCallback(duration, self._clearMarker)
        return

    def _clearMarker(self):
        ctrl = self._guiSessionProvider.shared.areaMarker
        if ctrl is not None:
            if self._markerID is not None:
                ctrl.removeMarker(self._markerID)
                self._markerID = None
        return


class _Comp7RedLineApplicationPointEffect(_Comp7ApplicationPointEffect, EffectRunner):
    _VIEW_STATE_DURATION = 5.0

    def __init__(self, *args, **kwargs):
        super(_Comp7RedLineApplicationPointEffect, self).__init__(*args, **kwargs)
        EffectRunner.__init__(self, self._entity, self._equipment)

    def _getFeedbackEventId(self):
        return FEEDBACK_EVENT_ID.VEHICLE_RED_LINE

    def onEnterWorld(self, prereqs):
        super(_Comp7RedLineApplicationPointEffect, self).onEnterWorld(prereqs)
        self._playEffect(self._getAreaDuration())

    def _createMarker(self, duration):
        ctrl = self._guiSessionProvider.shared.equipments
        delay = self._getAreaDuration()
        if ctrl is not None and delay > 0:
            ctrl.showMarker(self._equipment, self._position, self._direction, delay)
        return

    def _playEffect(self, duration):
        if self._equipment.areaShow == AreaShow.ALWAYS:
            duration += self._equipment.duration
        radius = self._getRadius()
        self.playEffect(AoeEffects.START, self._position, radius)
        self._callbackDelayer.delayCallback(self._equipment.delay, self.playEffect, AoeEffects.ACTION, self._position, radius)


_EQUIPMENT_APPLICATION_POINTS = {'comp7_recon': _Comp7ReconApplicationPointEffect,
 'comp7_redline': _Comp7RedLineApplicationPointEffect}
