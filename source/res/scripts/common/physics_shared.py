# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/physics_shared.py
# Compiled at: 2011-11-22 15:17:12
import BigWorld
import Math
import math
from math import pi
from constants import IS_CLIENT
GRAVITY = 1.3
FORWARD_FRICTION = 0.07
MIN_SIDE_FRICTION = 0.75
MIN_SIDE_FRICTION_SPEED = 4.2
MAX_SIDE_FRICTION = 1.8
MAX_SIDE_FRICTION_SPEED = 11.1
CONTINUUM_RESIST_SPEED = 1.0
CONTINUUM_RESIST = 1.0
SUSP_WEIGHT = 0.2
MIN_SPEED_AFFECT_ROT = 11.1
MAX_SPEED_AFFECT_ROT = 22.2
SPEED_AFFECT_ROT_DECREASE = 0.0
COHESION = 1.0
ROTATION_POWER_FRACTION = 0.85
BKWD_POWER_FRACTION = 0.85
ANG_ACCELERATION_TIME = 0.05
ROLL_TRACTION = 1.41
ROLL_TRACTION_BOUND = 1.05
BROKEN_TRACK_SIDE_FRICTION = 0.75
BROKEN_TRACK_FWD_FRICTION = 0.7
RISE_FRICTION_Y = 0.906
RISE_FRICTION = 2.0
SUSP_BALANCE_COMPRESSION = 0.93
SUSP_BALANCE_HEIGHT = 0.7
SUSP_HARD_RATIO = 0.65
SUSP_DAMP = 0.065
BODY_HEIGHT = 0.6
CENTER_OF_MASS_Y = 0.0
TRACKS_PENETRATION = 0.01
TRACK_RESTITUTION = 0.1
FWD_FRICTION_Y = 1.41
LIFT_SPRING_STIFFNES = 1.5
LIFT_SPRING_SIZE = 0.5
SUSP_SOFT_FRICTION = 0.2
TRACK_FWD_FRICTION = 0.0
TRACK_SIDE_FRICTION = 0.0
SUSP_SLUMP_FRICTION = 0.04
SUSP_SLUMP_FRICTION_BOUND = 1.0
_COH_DECAY_Y = 0.259
_COH_DECAY_FACTOR = 5.0
_COH_DECAY_POW = 1.5
_COH_DECAY_BOUND = 0.5

def applyGlobalConfig():
    for e in BigWorld.entities.values():
        if e.className == 'Vehicle':
            initVehiclePhysics(e.mover.physics, e.typeDescriptor)


def computeRotationFriction(enginePower, localFrocePt, fwdFriction, mg, wlim, rotRad):
    rotVel = wlim * rotRad
    fwdPart = (localFrocePt * Math.Vector3((0, 0, fwdFriction * mg))).length
    rotationRatio = max(0.1, 1.0 - fwdFriction * mg * rotVel / enginePower)
    rotationalFriction = (enginePower / wlim - fwdPart) / mg
    return (rotationRatio, rotationalFriction)


def initVehiclePhysics(physics, typeDesc, **kwargs):
    physDescr = typeDesc.physics
    hullMin, hullMax, _ = typeDesc.hull['hitTester'].bbox
    hullCenter = (hullMin + hullMax) * 0.5
    hullY = hullCenter.y + typeDesc.chassis['hullPosition'].y
    hullHeight = hullMax.y - hullMin.y
    bmin, bmax, _ = typeDesc.chassis['hitTester'].bbox
    blen = bmax[2] - bmin[2]
    width = bmax[0] - bmin[0]
    height = bmax[1] - bmin[1]
    fullMass = physDescr['weight'] / 1000.0
    suspMass = SUSP_WEIGHT * fullMass
    if IS_CLIENT:
        hullMass = fullMass
    else:
        hullMass = fullMass - suspMass
    g = 9.81 * GRAVITY
    suspBalanceHeight = SUSP_BALANCE_HEIGHT * height
    if not IS_CLIENT:
        carringSpringLength = (suspBalanceHeight + TRACKS_PENETRATION) / SUSP_BALANCE_COMPRESSION
    else:
        carringSpringLength = suspBalanceHeight / SUSP_BALANCE_COMPRESSION
    hmg = hullMass * g
    mg = fullMass * g
    physics.centerOfMass = Math.Vector3((0.0, hullY + CENTER_OF_MASS_Y * hullHeight, 0.0))
    forcePtX = 0.5
    if IS_CLIENT:
        forcePtY = 0.0
    else:
        forcePtY = -physics.centerOfMass.y * suspMass / fullMass
    boxHeight = height * BODY_HEIGHT
    globalBoxY = suspBalanceHeight + boxHeight / 2
    boxCenter = Math.Vector3((0, globalBoxY - hullY, 0))
    imp = hullMass / 12.0
    inertia = Math.Vector3((imp * (height * height + blen * blen), imp * (width * width + blen * blen), imp * (width * width + height * height)))
    boxSize = Math.Vector3((width, boxHeight, blen))
    boxSize2 = Math.Vector3(boxSize)
    box2YExpand = SUSP_BALANCE_COMPRESSION * carringSpringLength
    boxSize2.y += box2YExpand
    boxCenter2 = Math.Vector3(boxCenter)
    boxCenter2.y -= box2YExpand * 0.5
    physics.setupBody(boxSize, boxCenter, boxSize2, boxCenter2, hullMass, inertia)
    fwdSpeedLimit, bkwdSpeedLimit = physDescr['speedLimits']
    physics.fwdSpeedLimit = fwdSpeedLimit
    physics.bkwdSpeedLimit = bkwdSpeedLimit
    physics.brakeFriction = COHESION
    physics.forwardFriction = FORWARD_FRICTION * kwargs.get('fwdFrictionFactor', 1.0)
    physics.sideFrictionX = forcePtX * width
    physics.sideFrictionYMin = -forcePtY
    physics.sideFrictionYMax = ROLL_TRACTION_BOUND * physics.centerOfMass.y
    physics.sideFrictionYSpeed = ROLL_TRACTION * abs(physics.sideFrictionYMax - physics.sideFrictionYMin)
    physics.leftForcePt = Math.Vector3((-forcePtX * width, forcePtY, 0.0))
    physics.rightForcePt = Math.Vector3((forcePtX * width, forcePtY, 0.0))
    rotRad = 0.0 if physDescr['rotationIsAroundCenter'] else width * forcePtX
    wlim = physDescr['rotationSpeedLimit']
    physics.enginePower = physDescr['enginePower'] * GRAVITY / 1000.0
    rotationRatio, rotationalFriction = computeRotationFriction(physics.enginePower, physics.rightForcePt, physics.forwardFriction, mg, wlim, rotRad)
    physics.rotationRatio = rotationRatio
    physics.rotationalFriction = rotationalFriction
    physics.minSideFriction = MIN_SIDE_FRICTION
    physics.minSideFrictionSpeed = MIN_SIDE_FRICTION_SPEED
    physics.maxSideFriction = MAX_SIDE_FRICTION
    physics.maxSideFrictionSpeed = MAX_SIDE_FRICTION_SPEED
    physics.brokenTrackSideFriction = BROKEN_TRACK_SIDE_FRICTION
    physics.brokenTrackFwdFriction = BROKEN_TRACK_FWD_FRICTION
    physics.rotationPowerFactor = 1.0
    physics.rotationPowerFraction = ROTATION_POWER_FRACTION
    physics.bkwdPowerFraction = BKWD_POWER_FRACTION
    physics.gravity = g
    physics.cohesion = COHESION
    physics.riseFriction = RISE_FRICTION
    physics.riseFrictionY = RISE_FRICTION_Y
    physics.suspSlumpFriction = SUSP_SLUMP_FRICTION
    physics.slumpFrictionBound = SUSP_SLUMP_FRICTION_BOUND
    physics.fwdWrictionY = FWD_FRICTION_Y
    physics.movementSignals = 0
    physics.leftFwdFrictionPt = Math.Vector3((-forcePtX * width, forcePtY, 0.0))
    physics.rightFwdFrictionPt = Math.Vector3((forcePtX * width, forcePtY, 0.0))
    wAccelTime = ANG_ACCELERATION_TIME
    physics.rotationalCohesion = (wlim * inertia.y / wAccelTime + physics.enginePower / wlim) / mg
    physics.linMinPowerDivider = 1.0
    physics.rotMinPowerDivider = wlim * 0.25
    physics.springsHardFriction = TRACK_SIDE_FRICTION
    physics.springFwdFriction = TRACK_FWD_FRICTION
    physics.destructibleDamageFactor = 10
    physics.movementSignals = 0
    physics.tracksRestitution = TRACK_RESTITUTION
    physics.continuumResistSpeed = CONTINUUM_RESIST_SPEED * fwdSpeedLimit
    physics.continuumResist = CONTINUUM_RESIST / fwdSpeedLimit
    physics.minSpeedAffectRot = MIN_SPEED_AFFECT_ROT
    physics.speedAffectRotBound = wlim * SPEED_AFFECT_ROT_DECREASE
    physics.speedAffectRot = physics.speedAffectRotBound / (MAX_SPEED_AFFECT_ROT - MIN_SPEED_AFFECT_ROT)
    terrRes = physDescr['terrainResistance']
    groundResistances = Math.Vector4(terrRes[0], terrRes[0], terrRes[1], terrRes[2])
    physics.groundResistances = groundResistances
    if not IS_CLIENT:
        physics.cohDecayY = _COH_DECAY_Y
        physics.cohDecayFactor = _COH_DECAY_FACTOR
        physics.cohDecayPow = _COH_DECAY_POW
        physics.cohDecayBound = _COH_DECAY_BOUND
    physics.removeAllDamperSprings()
    carrierSpringPairs = 4
    length = carringSpringLength
    stiffnes = hmg / (carrierSpringPairs * 2 * length * (1.0 - SUSP_BALANCE_COMPRESSION))
    damp = SUSP_DAMP * stiffnes
    hardRatio = SUSP_HARD_RATIO
    indent = boxHeight / 2
    sdir = Math.Vector3((0, -1, 0))
    stepZ = blen / (carrierSpringPairs + 1)
    begZ = -blen * 0.5 + stepZ
    leftX = -width * 0.45
    rightX = width * 0.45
    y = -boxHeight / 2 + boxCenter.y
    rollerMass = suspMass / (carrierSpringPairs * 2)
    side = Math.Vector3((1, 0, 0))
    pen = TRACKS_PENETRATION
    rollerMode = False if IS_CLIENT else True
    for i in xrange(0, carrierSpringPairs):
        mountPoint = Math.Vector3((leftX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         sdir,
         side,
         length,
         indent,
         hardRatio,
         stiffnes,
         damp,
         rollerMass,
         True,
         pen,
         rollerMode))
        mountPoint = Math.Vector3((rightX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         sdir,
         side,
         length,
         indent,
         hardRatio,
         stiffnes,
         damp,
         rollerMass,
         False,
         pen,
         rollerMode))


def encodeAngleToUint(angle, bits):
    return int(((1 << bits) - 1) * (angle + pi) / (pi * 2.0))


def decodeAngleFromUint(code, bits):
    return pi * 2.0 * code / ((1 << bits) - 1) - pi
