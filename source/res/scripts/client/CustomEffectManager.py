# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffectManager.py
from AvatarInputHandler import mathUtils
import Math
import math
import BigWorld
import material_kinds
from CustomEffect import PixieCache
from CustomEffect import EffectSettings
from vehicle_systems.assembly_utility import Component
_ENABLE_VALUE_TRACKER = False
_ENABLE_VALUE_TRACKER_ENGINE = False
_ENABLE_PIXIE_TRACKER = False

def _calcScrollDelta(scroll, vehicleSpeed):
    scrollDelta = 0.0
    if abs(scroll) > 0.1:
        if abs(vehicleSpeed) < 0.1:
            scrollDelta = scroll
        else:
            scrollDelta = scroll - vehicleSpeed
            if scroll * vehicleSpeed > 0.0:
                if scrollDelta * scroll < 0.0:
                    scrollDelta = 0.0
    return scrollDelta


class TrackScrollingFilter(object):

    def __init__(self, weight):
        self.__value = 0.0
        self.__inputValue = 0.0
        self.__Tin = 0.1
        self.__Tout = 0.05

    def setScroll(self, scroll):
        self.__inputValue = scroll

    def output(self):
        return self.__value

    def update(self, speed, dt):
        scrollDelta = _calcScrollDelta(self.__inputValue, speed)
        self.__value += (scrollDelta - self.__value) * (dt / self.__Tout)
        self.__inputValue += -self.__inputValue * (dt / self.__Tin)


class CustomEffectManager(Component):
    _LEFT_TRACK = 1
    _RIGHT_TRACK = 2
    _DRAW_ORDER_IDX = 50
    _SCROLL_TICK = 0.05

    def __init__(self, vehicle, engineState):
        if _ENABLE_VALUE_TRACKER or _ENABLE_VALUE_TRACKER_ENGINE or _ENABLE_PIXIE_TRACKER:
            from helpers.ValueTracker import ValueTracker
            self.__vt = ValueTracker.instance()
        else:
            self.__vt = None
        self.__selectors = []
        self.__variableArgs = dict()
        self.__vehicle = vehicle
        self.__engineState = engineState
        self.__prevWaterHeight = None
        self.__gearUP = False
        self.__engineState.setGearUpCallback(self.__gearUp)
        weight = self.__vehicle.typeDescriptor.physics['weight']
        self.__leftScroll = TrackScrollingFilter(weight)
        self.__rightScroll = TrackScrollingFilter(weight)
        self.__scrollUpdateID = BigWorld.callback(self._SCROLL_TICK, self.__scrollTick)
        args = {}
        args['chassis'] = {}
        args['chassis']['model'] = self.__vehicle.appearance.modelsDesc['chassis']['model']
        args['hull'] = {}
        args['hull']['model'] = self.__vehicle.appearance.modelsDesc['hull']['model']
        args['drawOrderBase'] = CustomEffectManager._DRAW_ORDER_IDX
        for desc in self.__vehicle.typeDescriptor.hull['customEffects']:
            if desc is not None:
                selector = desc.create(args)
                if selector is not None:
                    self.__selectors.append(selector)

        for desc in self.__vehicle.typeDescriptor.chassis['customEffects']:
            if desc is not None:
                selector = desc.create(args)
                if selector is not None:
                    self.__selectors.append(selector)

        self.__createChassisCenterNodes()
        PixieCache.incref()
        return

    def getParameter(self, name):
        return self.__variableArgs.get(name, 0.0)

    def destroy(self):
        if self.__scrollUpdateID is None:
            return
        else:
            for effectSelector in self.__selectors:
                effectSelector.destroy()

            PixieCache.decref()
            BigWorld.cancelCallback(self.__scrollUpdateID)
            self.__scrollUpdateID = None
            self.__engineState.delGearUpCallback()
            self.__engineState = None
            if _ENABLE_PIXIE_TRACKER and self.__vehicle.isPlayerVehicle:
                self.__vt.addValue2('Pixie Count', PixieCache.pixiesCount)
            return

    def enable(self, enable, settingsFlags=EffectSettings.SETTING_DUST):
        for effectSelector in self.__selectors:
            if effectSelector.settingsFlags() == settingsFlags:
                if enable:
                    effectSelector.start()
                else:
                    effectSelector.stop()

    def stop(self):
        for effectSelector in self.__selectors:
            effectSelector.stop()

    def __scrollTick(self):
        vehicleSpeed = self.__vehicle.filter.speedInfo.value[2]
        self.__leftScroll.update(vehicleSpeed, self._SCROLL_TICK)
        self.__rightScroll.update(vehicleSpeed, self._SCROLL_TICK)
        self.__scrollUpdateID = BigWorld.callback(self._SCROLL_TICK, self.__scrollTick)

    def __createChassisCenterNodes(self):
        chassisModel = self.__vehicle.appearance.modelsDesc['chassis']['model']
        topRightCarryingPoint = self.__vehicle.typeDescriptor.chassis['topRightCarryingPoint']
        self.__trailParticleNodes = []
        self.__trailParticles = {}
        mMidLeft = Math.Matrix()
        mMidLeft.setTranslate((-topRightCarryingPoint[0], 0.0, 0.0))
        mMidRight = Math.Matrix()
        mMidRight.setTranslate((topRightCarryingPoint[0], 0.0, 0.0))
        self.__trailParticleNodes = [chassisModel.node('', mMidLeft), chassisModel.node('', mMidRight)]

    def getTrackCenterNode(self, trackIdx):
        return self.__trailParticleNodes[trackIdx]

    def updateTrackScroll(self, leftScroll, rightScroll):
        self.__leftScroll.setScroll(leftScroll)
        self.__rightScroll.setScroll(rightScroll)

    def __gearUp(self):
        self.__gearUP = True

    def update(self):
        appearance = self.__vehicle.appearance
        vehicleSpeed = self.__vehicle.filter.speedInfo.value[2]
        self.__variableArgs['speed'] = vehicleSpeed
        direction = 1 if vehicleSpeed >= 0.0 else -1
        self.__variableArgs['direction'] = direction
        self.__variableArgs['rotSpeed'] = self.__vehicle.filter.speedInfo.value[1]
        if self.__vehicle.filter.placingOnGround:
            leftHasContact = self.__vehicle.filter.numLeftTrackContacts > 0
            rightHasContact = self.__vehicle.filter.numRightTrackContacts > 0
        else:
            leftHasContact = not appearance.fashion.isFlyingLeft
            rightHasContact = not appearance.fashion.isFlyingRight
        matKindsUnderTracks = getCorrectedMatKinds(appearance)
        self.__variableArgs['deltaR'], self.__variableArgs['directionR'], self.__variableArgs['matkindR'] = self.__getScrollParams(self.__rightScroll.output(), rightHasContact, matKindsUnderTracks[CustomEffectManager._RIGHT_TRACK])
        self.__variableArgs['deltaL'], self.__variableArgs['directionL'], self.__variableArgs['matkindL'] = self.__getScrollParams(self.__leftScroll.output(), leftHasContact, matKindsUnderTracks[CustomEffectManager._LEFT_TRACK])
        matInv = Math.Matrix(self.__vehicle.matrix)
        matInv.invert()
        velocityLocal = matInv.applyVector(self.__vehicle.filter.velocity)
        velLen = velocityLocal.length
        if velLen > 1.0:
            vehicleDir = Math.Vector3(0.0, 0.0, 1.0)
            velocityLocal = Math.Vector2(velocityLocal.z, velocityLocal.x)
            cosA = velocityLocal.dot(Math.Vector2(vehicleDir.z, vehicleDir.x)) / velLen
            self.__variableArgs['hullAngle'] = math.acos(mathUtils.clamp(0.0, 1.0, math.fabs(cosA)))
        else:
            self.__variableArgs['hullAngle'] = 0.0
        self.__variableArgs['isUnderWater'] = 1 if appearance.isUnderwater else 0
        self.__correctWaterNodes()
        self.__variableArgs['gearUp'] = self.__gearUP
        self.__variableArgs['RPM'] = self.__engineState.relativeRPM
        self.__gearUP = False
        self.__variableArgs['engineLoad'] = self.__engineState.mode
        self.__variableArgs['engineStart'] = self.__engineState.starting
        self.__variableArgs['physicLoad'] = self.__engineState.physicLoad
        for effectSelector in self.__selectors:
            effectSelector.update(self.__variableArgs)

        if _ENABLE_VALUE_TRACKER and self.__vehicle.isPlayerVehicle:
            self.__vt.addValue2('speed', self.__variableArgs['speed'])
            self.__vt.addValue2('direction', self.__variableArgs['direction'])
            self.__vt.addValue2('rotSpeed', self.__variableArgs['rotSpeed'])
            self.__vt.addValue2('deltaR', self.__variableArgs['deltaR'])
            self.__vt.addValue2('deltaL', self.__variableArgs['deltaL'])
            self.__vt.addValue2('hullAngle', self.__variableArgs['hullAngle'])
            self.__vt.addValue2('isUnderWater', self.__variableArgs['isUnderWater'])
            if self.__variableArgs['matkindL'] > -1:
                materialL = material_kinds.EFFECT_MATERIAL_INDEXES_BY_IDS[self.__variableArgs['matkindL']]
                self.__vt.addValue('materialL', material_kinds.EFFECT_MATERIALS[materialL])
            else:
                self.__vt.addValue('materialL', 'No')
            if self.__variableArgs['matkindR'] > -1:
                materialR = material_kinds.EFFECT_MATERIAL_INDEXES_BY_IDS[self.__variableArgs['matkindR']]
                self.__vt.addValue('materialR', material_kinds.EFFECT_MATERIALS[materialR])
            else:
                self.__vt.addValue('materialR', 'No')
        if _ENABLE_VALUE_TRACKER_ENGINE and self.__vehicle.isPlayerVehicle:
            self.__vt.addValue2('engineStart', self.__variableArgs['engineStart'])
            self.__vt.addValue2('gearUP', self.__variableArgs['gearUp'])
            self.__vt.addValue2('RPM', self.__variableArgs['RPM'])
            self.__vt.addValue2('engineLoad', self.__engineState.mode)
            self.__vt.addValue2('physicLoad', self.__engineState.physicLoad)
        if _ENABLE_PIXIE_TRACKER and self.__vehicle.isPlayerVehicle:
            self.__vt.addValue2('Pixie Count', PixieCache.pixiesCount)

    @staticmethod
    def __getScrollParams(trackScrolldelta, hasContact, matKindsUnderTrack):
        matKind = -1
        scrollDelta = 0.0
        if hasContact:
            scrollDelta = trackScrolldelta
            matKind = matKindsUnderTrack
        direction = 1 if scrollDelta >= 0.0 else -1
        scrollDelta = abs(scrollDelta)
        return (scrollDelta, direction, matKind)

    def __correctWaterNodes(self):
        waterHeight = 0.0 if not self.__vehicle.appearance.isInWater else self.__vehicle.appearance.waterHeight
        if waterHeight != self.__prevWaterHeight:
            position = self.__vehicle.position
            for effectSelector in self.__selectors:
                for node in effectSelector.effectNodes:
                    if node is not None:
                        node.correctWater(position, waterHeight)

            self.__prevWaterHeight = waterHeight
        return


def getCorrectedMatKinds(vehicleAppearance):
    correctedMatKinds = [ (material_kinds.WATER_MATERIAL_KIND if vehicleAppearance.isInWater else matKind) for matKind in vehicleAppearance.terrainMatKind ]
    return correctedMatKinds
