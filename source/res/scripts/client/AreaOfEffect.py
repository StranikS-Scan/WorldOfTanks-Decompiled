# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaOfEffect.py
from functools import partial
import math
import random
import BigWorld
import AnimationSequence
import CGF
import GenericComponents
import Math
import math_utils
import CombatSelectedArea
from ProjectileMover import collideDynamicAndStatic
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.battle_control import avatar_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MarkersManagerEvent
from helpers import dependency
from ids_generators import SequenceIDGenerator
from items import vehicles
from items.artefacts import AoeEffects, AreaShow, OrderTypes
from skeletons.account_helpers.settings_core import ISettingsCore
from random_utils import getValueWithDeviationInPercent
from skeletons.gui.battle_session import IBattleSessionProvider

class EffectRunner(object):
    SHOT_HEIGHT = 100.0
    RAY_CAST_HEIGHT = 2.0
    MAX_SHOTS = 1000
    GRAVITY = 9.8
    SHELL_VELOCITY = (0, -500, 0)

    def __init__(self, entity, equipment):
        self._sequences = []
        self._callbacks = {}
        self._areas = {}
        self._idGen = SequenceIDGenerator()
        self.salvo = BigWorld.PySalvo(self.MAX_SHOTS, 0, -self.SHOT_HEIGHT)
        self._entity = entity
        self._equipment = equipment

    @property
    def areaColor(self):
        return self._equipment.areaColorBlind if self.__settingsCore.getSetting(GRAPHICS.COLOR_BLIND) and self._equipment.areaColorBlind is not None else self._equipment.areaColor

    def prerequisites(self):
        prereqs = []
        if self._equipment.areaVisual:
            prereqs.append(self._equipment.areaVisual)
        for effect in self._equipment.effects.itervalues():
            if not effect:
                continue
            for sequence in effect['sequences']:
                prereqs.append(AnimationSequence.Loader(sequence, self._entity.spaceID))

        return prereqs

    def playEffect(self, effectType, position, radius):
        effect = self._equipment.effects.get(effectType)
        if not effect:
            return
        else:
            delayOffset = 0
            repeatDelay = effect['repeatDelay']
            repeatDelayDeviationPercent = effect['repeatDelayDeviationPercent']
            for _ in xrange(effect['repeatCount']):
                playID = self._idGen.next()
                play = partial(self._play, playID, effect, position)
                self._callbacks[playID] = BigWorld.callback(delayOffset, play)
                delayOffset += getValueWithDeviationInPercent(repeatDelay, repeatDelayDeviationPercent)

            if effect['areaColor']:
                area = CombatSelectedArea.CombatSelectedArea()
                area.setup(position, Math.Vector3(0, 0, 0), Math.Vector2(radius * 2, radius * 2), CombatSelectedArea.DEFAULT_RADIUS_MODEL, effect['areaColor'], None)
                areaID = self._idGen.next()
                self._areas[areaID] = area
            return

    def _play(self, playID, effect, targetPosition):
        self._callbacks.pop(playID)
        if effect['offsetDeviation']:
            radius = random.uniform(0, effect['offsetDeviation'])
            angle = random.uniform(0, 2 * math.pi)
            offset = Math.Vector3(radius * math.cos(angle), 0, radius * math.sin(angle))
            targetPosition = targetPosition + offset
        if effect['groundRaycast']:
            altitude = Math.Vector3(0, self.RAY_CAST_HEIGHT, 0)
            startPoint = targetPosition + altitude
            endPoint = targetPosition - altitude
            collisionPoint = collideDynamicAndStatic(startPoint, endPoint, (BigWorld.player().playerVehicleID,))
            if collisionPoint:
                targetPosition = collisionPoint[0]
        if effect['shotEffects']:
            altitude = Math.Vector3(0, self.SHOT_HEIGHT, 0)
            shotEffect = random.choice(effect['shotEffects'])
            effectsIndex = vehicles.g_cache.shotEffectsIndexes[shotEffect]
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            artilleryID = effectsDescr.get('artilleryID')
            if artilleryID is not None:
                self.salvo.addProjectile(artilleryID, self.GRAVITY, targetPosition + altitude, self.SHELL_VELOCITY)
        if effect['sequences']:
            sequencesOrderType = effect.get('sequencesOrderType', OrderTypes.RANDOM)
            sequencesIds = effect['sequences'].keys()
            if sequencesOrderType == OrderTypes.RANDOM:
                sequencesIds = random.sample(sequencesIds, 1)
            for sequenceID in sequencesIds:
                sequenceData = effect['sequences'][sequenceID]
                matrix = Math.Matrix()
                matrix.setRotateY(self._entity.yaw)
                matrix.setScale(sequenceData['scale'])
                matrix.translation = targetPosition
                loader = AnimationSequence.Loader(sequenceID, self._entity.spaceID)
                animator = loader.loadSync()
                animator.bindToWorld(matrix)
                animator.speed = 1
                animator.loopCount = 1
                animator.start()
                self._sequences.append(animator)

        return


class AreaOfEffect(BigWorld.Entity, EffectRunner):
    MAX_LAG = 0.5
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self._equipment = vehicles.g_cache.equipments()[self.equipmentID]
        self.__areaGO = None
        self.__mainAreaID = None
        self.__destroyGoCallback = None
        EffectRunner.__init__(self, self, self._equipment)
        return

    @property
    def areaColor(self):
        return self._equipment.areaColorBlind if self.__settingsCore.getSetting(GRAPHICS.COLOR_BLIND) and self._equipment.areaColorBlind is not None else self._equipment.areaColor or CombatSelectedArea.COLOR_WHITE

    def onEnterWorld(self, prereqs):
        timeOffset = BigWorld.serverTime() - self.launchTime
        if timeOffset < self.MAX_LAG:
            self.playEffect(AoeEffects.START, self.position, self._equipment.areaRadius)
        self._showArea()
        if self._isMarkersManagerReady:
            self._showMarker()
        else:
            g_eventBus.addListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl:
            equipmentsCtrl.onEquipmentAreaCreated(self._equipment, self.position, self._entity.launchTime + self._equipment.delay)
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged

    def onLeaveWorld(self):
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        for callbackID in self._callbacks.itervalues():
            BigWorld.cancelCallback(callbackID)

        self._callbacks = {}
        if self.__destroyGoCallback is not None:
            BigWorld.cancelCallback(self.__destroyGoCallback)
        self.__destroyGoCallback = None
        for area in self._areas.itervalues():
            area.destroy()

        self._areas = {}
        for animator in self._sequences:
            if animator:
                animator.stop()

        self._sequences = []
        self._equipment = None
        return

    def _areaDestroy(self, areaID):
        self._callbacks.pop(areaID)
        area = self._areas.pop(areaID)
        area.destroy()
        if areaID == self.__mainAreaID:
            self.__mainAreaID = None
        return

    @property
    def _isMarkersManagerReady(self):
        return self.sessionProvider.shared.areaMarker._gui.getMarkers2DPlugin()

    def _onMarkersCreated(self, event):
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self._showMarker()

    @property
    def _adjustedDelay(self):
        timeOffset = BigWorld.serverTime() - self.launchTime
        return self._equipment.delay - timeOffset

    @property
    def _direction(self):
        return Math.Matrix(self.matrix).applyToAxis(2)

    def _showArea(self):
        if not self._isAreaVisible():
            return
        else:
            areaTimeout = self._adjustedDelay
            if self._equipment.areaShow == AreaShow.ALWAYS:
                areaTimeout += self._equipment.duration
            areaVisual = self._equipment.areaVisual
            if areaVisual and areaTimeout > 0:
                areaSize = Math.Vector2(self._equipment.areaWidth, self._equipment.areaLength)
                area = CombatSelectedArea.CombatSelectedArea()
                area.setup(self.position, self._direction, areaSize, areaVisual, self.areaColor, None)
                area.enableAccurateCollision(self._equipment.areaAccurateCollision)
                area.enableWaterCollision(True)
                areaID = self._idGen.next()
                self._areas[areaID] = area
                self._callbacks[areaID] = BigWorld.callback(areaTimeout, partial(self._areaDestroy, areaID))
                self.__mainAreaID = areaID
                if self._equipment.areaUsedPrefab:
                    CGF.loadGameObjectIntoHierarchy(self._equipment.areaUsedPrefab, self.entityGameObject, Math.Vector3(), self.__onAreaGOLoaded)
                    self.__destroyGoCallback = BigWorld.callback(areaTimeout, self.__destroyAreaGO)
            return

    def _showMarker(self):
        if not self._isAreaVisible():
            return
        delay = self._adjustedDelay
        if self._equipment.areaShow == AreaShow.ALWAYS:
            delay += self._equipment.duration
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl and delay > 0:
            equipmentsCtrl.showMarker(self._equipment, self.position, self._direction, delay)

    def _isAttackerEnemy(self):
        return self.sessionProvider.getArenaDP().getVehicleInfo(self.vehicleID).team != BigWorld.player().team

    def _isAreaVisible(self):
        if self._equipment.areaVisibleToEnemies:
            return True
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(self.vehicleID)
        return vInfo.team == avatar_getter.getObserverTeam()

    def __onAreaGOLoaded(self, gameObject):
        if self.isDestroyed:
            return
        self.__areaGO = gameObject
        t = gameObject.findComponentByType(GenericComponents.TransformComponent)
        floatEpsilon = 0.001
        xScale = self._equipment.areaWidth * 0.5
        zScale = self._equipment.areaLength * 0.5
        t.transform = math_utils.createSRTMatrix(Math.Vector3(xScale, 1.0, zScale), (0.0, 0.0, 0.0), (0.0, floatEpsilon, 0.0))

    def __destroyAreaGO(self):
        if self.__areaGO is not None:
            CGF.removeGameObject(self.__areaGO)
        self.__areaGO = None
        self.__destroyGoCallback = None
        return

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            area = self._areas.get(self.__mainAreaID, None)
            if area is not None:
                area.setColor(self.areaColor)
        return
