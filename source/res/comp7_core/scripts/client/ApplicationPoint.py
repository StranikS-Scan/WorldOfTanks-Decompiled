# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/ApplicationPoint.py
from __future__ import absolute_import, division
import weakref
import BigWorld
import CGF
import CombatSelectedArea
import Math
import SoundGroups
import math
import math_utils
from account_helpers.settings_core.settings_constants import GRAPHICS
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from items.artefacts import AoeEffects, AreaShow
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from AreaOfEffect import EffectRunner
from typing import List
from LightComponents import OmniLightComponent

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
        return self._effect.areaColor if self._effect is not None else CombatSelectedArea.COLOR_WHITE

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

    @property
    def areaColor(self):
        return self._equipment.areaColor

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
            CGF.loadAndCreatePrefabWithParent(self._equipment.areaUsedPrefab, self._entity.entityGameObject, Math.Vector3(), self._onAreaGOLoaded)

    def _clearArea(self):
        if self._area is not None:
            self._area.destroy()
            self._area = None
        if self.__areaGO is not None:
            CGF.removeGameObject(self.__areaGO)
            self.__areaGO = None
        return

    def _getEndTime(self):
        return self._entity.launchTime + self._getViewStateDuration()

    def _isEnded(self):
        return self._getEndTime() < BigWorld.serverTime()

    def _updateViewState(self):
        if self._isEnded():
            return
        state = {'endTime': self._getEndTime(),
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
        if self._isEnded():
            return False
        vInfo = self._guiSessionProvider.getArenaDP().getVehicleInfo(self._entity.vehicleID)
        return vInfo.team == avatar_getter.getObserverTeam() or vInfo.isObserver()

    def _getRadius(self):
        return self._equipment.getRadiusBasedOnSkillLevel(self._entity.level)

    def _onAreaGOLoaded(self, objects, queue):
        if self._entity.isDestroyed:
            return
        root = objects[0]
        self.__areaGO = queue.gameObject(root)
        t = queue.component(root, CGF.TransformComponent)
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


class _Comp7IlluminationFlareApplicationPointEffect(_Comp7ApplicationPointEffect):
    _APPLY_SOUND_SELF = 'comp_7_ability_flare_apply'
    _APPLY_SOUND_ALLY = 'comp_7_ability_flare_ally'
    _APPLY_SOUND_ENEMY = 'comp_7_ability_flare_enemy'
    _START_EFFECT_TIME = 2.0
    _END_EFFECT_OFFSET = 2.7
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        super(_Comp7IlluminationFlareApplicationPointEffect, self).__init__(*args, **kwargs)
        self._rocketAreaGO = None
        self._omniLightGO = None
        self._areaGO = None
        self._effectStart = None
        self._effectIdle = None
        self._effectEnd = None
        self._spaceID = None
        self._soundObj = None
        return

    @property
    def areaColor(self):
        if self._isEnemy():
            if self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND):
                return self._equipment.areaPrefabColorEnemyCB
            return self._equipment.areaPrefabColorEnemy
        return self._equipment.areaPrefabColorAlly

    def _getRadius(self):
        return self._equipment.startRadius

    def _getAreaDuration(self):
        return self._entity.launchTime + self._getViewStateDuration() - BigWorld.serverTime()

    def _getViewStateDuration(self):
        return self._equipment.delay + self._equipment.duration + self._equipment.decayPhaseDuration

    def _createMarker(self, duration):
        ctrl = self._guiSessionProvider.shared.areaMarker
        if ctrl is not None:
            symbol = 'COMP7_ILLUMINATION_FLARE_ENEMY' if self._isEnemy() else 'COMP7_ILLUMINATION_FLARE'
            marker = ctrl.createMarker(self._entity.matrix, symbol)
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

    def _clearArea(self):
        if self._soundObj is not None:
            self._soundObj.stopAll()
            self._soundObj = None
        if self._rocketAreaGO is not None:
            CGF.removeGameObject(self._rocketAreaGO)
            self._rocketAreaGO = None
        super(_Comp7IlluminationFlareApplicationPointEffect, self)._clearArea()
        return

    def onEnterWorld(self, prereqs):
        super(_Comp7IlluminationFlareApplicationPointEffect, self).onEnterWorld(prereqs)
        self._createMarker(self._getAreaDuration())
        self._callbackDelayer.delayCallback(self._equipment.delay, self._showDelayedPrefab)
        self._playApplySound()

    def _playApplySound(self):
        if self._isEnemy():
            soundName = self._APPLY_SOUND_ENEMY
        elif self._entity.vehicleID != self._guiSessionProvider.shared.vehicleState.getControllingVehicleID():
            soundName = self._APPLY_SOUND_ALLY
        else:
            soundName = self._APPLY_SOUND_SELF
        SoundGroups.g_instance.playSound2D(soundName)

    def _showDelayedPrefab(self):
        self._callbackDelayer.delayCallback(self._getAreaDuration(), self._clearArea)
        if self._equipment.areaUsedPrefab:
            CGF.loadAndCreatePrefabWithParent(self._equipment.areaUsedPrefab, self._entity.entityGameObject, Math.Vector3(), self._onAreaGOLoaded)

    def _onAreaGOLoaded(self, objects, queue):
        if self._entity.isDestroyed:
            return
        self._rocketAreaGO = queue.gameObject(objects[0])
        self._spaceID = queue.spaceID
        for pgo in objects:
            queue.deactivateGameObject(pgo)

        self._callbackDelayer.delayCallback(0.01, self._updateTransformTick)

    def _activatePrefab(self):
        go = self._rocketAreaGO
        if go is None or not go.valid:
            return
        else:
            queue = CGF.CommandQueue(self._spaceID)
            queue.activateGameObject(go)
            hierarchy = CGF.findHierarchySingleton(self._spaceID)

            def _find(name):
                node = hierarchy.findFirstNodeByName(go, name)
                return node if node is not None and node.valid else None

            self._omniLightGO = _find('Omni Light')
            self._effectStart = _find('ability_illumination_flare_start')
            self._effectIdle = _find('ability_illumination_flare_idle')
            self._effectEnd = _find('ability_illumination_flare_end')
            self._areaGO = _find('area')
            fakeLight = _find('fake_light')
            effectStartT = self._effectStart.findRead(CGF.TransformComponent)
            soundPos = effectStartT.worldPosition
            soundMatrix = Math.Matrix()
            soundMatrix.translation = soundPos
            self._soundObj = SoundGroups.g_instance.WWgetSoundObject('comp_7_ability_flare_{}'.format(self._entity.id), soundMatrix)
            if self._soundObj is not None:
                self._soundObj.play('comp_7_ability_flare_start_pc_npc')
                if self._isEnemy():
                    self._soundObj.play('comp_7_ability_flare_start_pc')
            for node in (self._omniLightGO,
             self._effectStart,
             self._areaGO,
             fakeLight):
                if node is not None:
                    queue.activateGameObject(node)

            return

    def _updateTransformTick(self):
        rocketGO = self._rocketAreaGO
        if not self._isEnded() and rocketGO is not None and rocketGO.valid and not rocketGO.isActive:
            self._activatePrefab()
        areaGO = self._areaGO
        if not self._isEnded() and areaGO is not None and areaGO.valid:
            duration = BigWorld.serverTime() - self._entity.launchTime
            activeTime = duration - self._equipment.delay
            if self._effectStart is not None and self._effectStart.isActive and duration > self._START_EFFECT_TIME:
                queue = CGF.CommandQueue(self._spaceID)
                queue.deactivateGameObject(self._effectStart)
                if self._effectIdle is not None:
                    queue.activateGameObject(self._effectIdle)
            elif self._effectIdle is not None and self._effectIdle.isActive and activeTime > self._equipment.duration - self._END_EFFECT_OFFSET:
                queue = CGF.CommandQueue(self._spaceID)
                queue.deactivateGameObject(self._effectIdle)
                if self._effectEnd is not None:
                    queue.activateGameObject(self._effectEnd)
            elif areaGO.isActive and activeTime > self._equipment.duration:
                queue = CGF.CommandQueue(self._spaceID)
                queue.deactivateGameObject(areaGO)
                if self._omniLightGO is not None:
                    queue.deactivateGameObject(self._omniLightGO)
                if self._soundObj is not None:
                    self._soundObj.play('comp_7_ability_flare_stop_pc_npc')
                    if self._isEnemy():
                        self._soundObj.play('comp_7_ability_flare_stop_pc')
            holdDuration = 0.3
            timeMul = min(1.0, max(0.0, (duration - self._equipment.delay - holdDuration) / self._equipment.duration))
            radiusDiff = self._equipment.startRadius - self._equipment.endRadius
            radius = self._equipment.startRadius - timeMul * radiusDiff
            invertTimeMul = 1.0 - timeMul
            t = areaGO.findWrite(CGF.TransformComponent)
            t.transform = math_utils.createSRTMatrix(Math.Vector3(radius, 1.0, radius), (0.0, 0.0, 0.0), (0.0, 0.001, 0.0))
            radius = max(radius, self._equipment.endRadius)
            if self._soundObj is not None:
                radiusSpan = self._equipment.startRadius - self._equipment.endRadius
                rtpcRadius = 100.0 * (radius - self._equipment.endRadius) / radiusSpan if radiusSpan > 0 else 0.0
                self._soundObj.setRTPC('RTPC_ext_lst_ability_radius', max(0.0, min(100.0, rtpcRadius)))
            effectDistance = self._equipment.startYFlare - self._equipment.endYFlare
            effectY = self._equipment.startYFlare + effectDistance * invertTimeMul
            effectMatrix = math_utils.createSRTMatrix(Math.Vector3(1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.0, effectY, 0.0))
            for effectGO in (self._effectStart, self._effectIdle, self._effectEnd):
                if effectGO is not None:
                    effectGO.findWrite(CGF.TransformComponent).transform = effectMatrix

            if activeTime <= self._equipment.duration:
                omniGO = self._omniLightGO
                if omniGO is not None and omniGO.valid:
                    omniT = omniGO.findRead(CGF.TransformComponent)
                    y = omniT.position.y
                    omniRadius = math.sqrt(y * y + radius * radius)
                    omniGO.findWrite(OmniLightComponent).updateOuterRadius(omniRadius)
        self._callbackDelayer.delayCallback(0.01, self._updateTransformTick)
        return

    def _isVisible(self):
        return False

    def _updateViewState(self):
        pass


class _Comp7RedLineApplicationPointEffect(_Comp7ApplicationPointEffect, EffectRunner):
    _VIEW_STATE_DURATION = 5.0

    def __init__(self, *args, **kwargs):
        super(_Comp7RedLineApplicationPointEffect, self).__init__(*args, **kwargs)
        EffectRunner.__init__(self, self._entity, self._equipment)

    def _getFeedbackEventId(self):
        return FEEDBACK_EVENT_ID.VEHICLE_RED_LINE

    def onEnterWorld(self, prereqs):
        super(_Comp7RedLineApplicationPointEffect, self).onEnterWorld(prereqs)
        if self._isEnded():
            return
        self._playEffect(self._getAreaDuration())

    def _createMarker(self, duration):
        ctrl = self._guiSessionProvider.shared.equipments
        delay = self._getAreaDuration()
        if ctrl is not None and delay > 0:
            ctrl.showMarker(self._equipment, self._position, self._direction, delay)
        return

    def _playEffect(self, duration):
        equipmentDelay = self._equipment.delay
        timeSinceLaunch = BigWorld.serverTime() - self._entity.launchTime
        if timeSinceLaunch > equipmentDelay:
            return
        if self._equipment.areaShow == AreaShow.ALWAYS:
            duration += self._equipment.duration
        radius = self._getRadius()
        self.playEffect(AoeEffects.START, self._position, radius)
        self._callbackDelayer.delayCallback(max(0.0, equipmentDelay - timeSinceLaunch), self.playEffect, AoeEffects.ACTION, self._position, radius)


class _PoiArtilleryAoeApplicationPointEffect(_Comp7RedLineApplicationPointEffect):

    def _getRadius(self):
        return self._equipment.radius


_EQUIPMENT_APPLICATION_POINTS = {'poi_artillery_aoe': _PoiArtilleryAoeApplicationPointEffect}
