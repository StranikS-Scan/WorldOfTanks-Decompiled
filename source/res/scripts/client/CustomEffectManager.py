# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffectManager.py
import math
import Math
import material_kinds
from CustomEffect import PixieCache
from CustomEffect import EffectSettings
from svarog_script.py_component import Component
from vehicle_systems.tankStructure import TankNodeNames
from AvatarInputHandler import mathUtils
_ENABLE_VALUE_TRACKER = False
_ENABLE_VALUE_TRACKER_ENGINE = False
_ENABLE_PIXIE_TRACKER = False

class CustomEffectManager(Component):
    _LEFT_TRACK = 1
    _RIGHT_TRACK = 2
    _DRAW_ORDER_IDX = 50

    def __init__(self, appearance):
        if _ENABLE_VALUE_TRACKER or _ENABLE_VALUE_TRACKER_ENGINE or _ENABLE_PIXIE_TRACKER:
            from helpers.ValueTracker import ValueTracker
            self.__vt = ValueTracker.instance()
        else:
            self.__vt = None
        self.__selectors = []
        self.__variableArgs = dict()
        self.__vehicle = None
        self.__appearance = appearance
        self.__engineState = appearance.detailedEngineState
        self.__prevWaterHeight = None
        self.__gearUP = False
        self.__trailParticleNodes = None
        self.__engineState.setGearUpCallback(self.__gearUp)
        args = {}
        args['chassis'] = {}
        args['chassis']['model'] = appearance.compoundModel
        args['hull'] = {}
        args['hull']['model'] = appearance.compoundModel
        args['drawOrderBase'] = CustomEffectManager._DRAW_ORDER_IDX
        for desc in appearance.typeDescriptor.hull['customEffects']:
            if desc is not None:
                selector = desc.create(args)
                if selector is not None:
                    self.__selectors.append(selector)

        for desc in appearance.typeDescriptor.chassis['customEffects']:
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
        self.deactivate()
        for effectSelector in self.__selectors:
            effectSelector.destroy()

        PixieCache.decref()
        self.__engineState.delGearUpCallback()
        self.__trailParticleNodes = None
        self.__selectors = None
        self.__engineState = None
        self.__appearance = None
        self.__variableArgs = None
        if _ENABLE_PIXIE_TRACKER:
            self.__vt.addValue2('Pixie Count', PixieCache.pixiesCount)
        if _ENABLE_VALUE_TRACKER or _ENABLE_VALUE_TRACKER_ENGINE or _ENABLE_PIXIE_TRACKER:
            self.__vt = None
        return

    def enable(self, enable, settingsFlags=EffectSettings.SETTING_DUST):
        for effectSelector in self.__selectors:
            if effectSelector.settingsFlags() == settingsFlags:
                if enable:
                    effectSelector.start()
                else:
                    effectSelector.stop()

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle

    def activate(self):
        super(CustomEffectManager, self).activate()
        for effectSelector in self.__selectors:
            effectSelector.start()

    def deactivate(self):
        for effectSelector in self.__selectors:
            effectSelector.stop()

        self.__vehicle = None
        super(CustomEffectManager, self).deactivate()
        return

    def __createChassisCenterNodes(self):
        compoundModel = self.__appearance.compoundModel
        self.__trailParticleNodes = [compoundModel.node(TankNodeNames.TRACK_LEFT_MID), compoundModel.node(TankNodeNames.TRACK_RIGHT_MID)]

    def getTrackCenterNode(self, trackIdx):
        return self.__trailParticleNodes[trackIdx]

    def __gearUp(self):
        self.__gearUP = True

    def update(self):
        vehicleSpeed = self.__vehicle.speedInfo.value[2]
        appearance = self.__appearance
        self.__variableArgs['speed'] = vehicleSpeed
        self.__variableArgs['isPC'] = self.__vehicle.isPlayerVehicle
        direction = 1 if vehicleSpeed >= 0.0 else -1
        self.__variableArgs['direction'] = direction
        self.__variableArgs['rotSpeed'] = self.__vehicle.speedInfo.value[1]
        matKindsUnderTracks = getCorrectedMatKinds(appearance)
        self.__variableArgs['deltaR'], self.__variableArgs['directionR'], self.__variableArgs['matkindR'] = self.__getScrollParams(appearance.trackScrollController.rightScroll(), appearance.trackScrollController.rightContact(), matKindsUnderTracks[CustomEffectManager._RIGHT_TRACK], direction)
        self.__variableArgs['deltaL'], self.__variableArgs['directionL'], self.__variableArgs['matkindL'] = self.__getScrollParams(appearance.trackScrollController.leftScroll(), appearance.trackScrollController.leftContact(), matKindsUnderTracks[CustomEffectManager._LEFT_TRACK], direction)
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

        if _ENABLE_VALUE_TRACKER:
            self.__vt.addValue2('speed', self.__variableArgs['speed'])
            self.__vt.addValue2('direction', self.__variableArgs['direction'])
            self.__vt.addValue2('rotSpeed', self.__variableArgs['rotSpeed'])
            self.__vt.addValue2('deltaR', self.__variableArgs['deltaR'])
            self.__vt.addValue2('deltaL', self.__variableArgs['deltaL'])
            self.__vt.addValue2('hullAngle', self.__variableArgs['hullAngle'])
            self.__vt.addValue2('isUnderWater', self.__variableArgs['isUnderWater'])
            self.__vt.addValue2('directionR', self.__variableArgs['directionR'])
            self.__vt.addValue2('directionL', self.__variableArgs['directionL'])
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
        if _ENABLE_VALUE_TRACKER_ENGINE:
            self.__vt.addValue2('engineStart', self.__variableArgs['engineStart'])
            self.__vt.addValue2('gearUP', self.__variableArgs['gearUp'])
            self.__vt.addValue2('RPM', self.__variableArgs['RPM'])
            self.__vt.addValue2('engineLoad', self.__engineState.mode)
            self.__vt.addValue2('physicLoad', self.__engineState.physicLoad)
        if _ENABLE_PIXIE_TRACKER:
            self.__vt.addValue2('Pixie Count', PixieCache.pixiesCount)

    @staticmethod
    def __getScrollParams(trackScrolldelta, hasContact, matKindsUnderTrack, direction):
        matKind = -1
        scrollDelta = 0.0
        if hasContact:
            scrollDelta = trackScrolldelta
            matKind = matKindsUnderTrack
        if scrollDelta != 0.0:
            direction = 1 if scrollDelta >= 0.0 else -1
        scrollDelta = abs(scrollDelta)
        return (scrollDelta, direction, matKind)

    def __correctWaterNodes(self):
        waterHeight = 0.0 if not self.__appearance.isInWater else self.__appearance.waterHeight
        if waterHeight != self.__prevWaterHeight:
            invVehicleMatrix = Math.Matrix(self.__appearance.compoundModel.matrix)
            invVehicleMatrix.invert()
            waterShiftRel = invVehicleMatrix.applyVector(Math.Vector3(0, waterHeight, 0))
            for effectSelector in self.__selectors:
                for node in effectSelector.effectNodes:
                    if node is not None:
                        node.correctWater(waterShiftRel)

            self.__prevWaterHeight = waterHeight
        return


def getCorrectedMatKinds(vehicleAppearance):
    correctedMatKinds = [ (material_kinds.WATER_MATERIAL_KIND if vehicleAppearance.isInWater else matKind) for matKind in vehicleAppearance.terrainMatKind ]
    return correctedMatKinds
