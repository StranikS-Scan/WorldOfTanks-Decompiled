# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/physics_shared.py
import BigWorld
import ResMgr
import Math
import math
import material_kinds
import collections
from items import vehicles, vehicle_items
from items.vehicles import VEHICLE_PHYSICS_TYPE
from math import pi
from constants import IS_CLIENT, IS_CELLAPP, VEHICLE_PHYSICS_MODE, SERVER_TICK_LENGTH
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
import copy
from items.components import gun_components
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES
from gun_rotation_shared import encodeRestrictedValueToUint, decodeRestrictedValueFromUint
G = 9.81
GRAVITY_FACTOR = 1.25
WEIGHT_SCALE = 0.001
GRAVITY_FACTOR_SCALED = GRAVITY_FACTOR * WEIGHT_SCALE
SUSP_COMPRESSION_MIN = 0.85
SUSP_COMPRESSION_MIN_MASS = 60.0
SUSP_COMPRESSION_MAX = 0.88
SUSP_COMPRESSION_MAX_MASS = 30.0
BODY_HEIGHT = 1.4
SIDE_MOVEMENT_THRESHOLD = SERVER_TICK_LENGTH * 0.05
_SIMULATION_Y_BOUND = 1000.0
FREEZE_ANG_ACCEL_EPSILON = 0.35
FREEZE_ACCEL_EPSILON = 0.4
FREEZE_VEL_EPSILON = 0.15
FREEZE_ANG_VEL_EPSILON = 0.06
WIDTH_LONG = 6.2
WIDTH_VERY_LONG = 7.0
CLEARANCE_RATIO_LONG = 5.0
NUM_SPRINGS_LONG = 5
NUM_SPRINGS_NORMAL = 5
CMY_MIN = -0.15
CMY_MID = -0.2
CMY_MAX = -0.3
DYN_RATIO_MIN = 9.5
DYN_RATIO_MID = 13.0
DYN_RATIO_MAX = 21.0
CLEARANCE = 1.75
CLEARANCE_MIN = 0.55
CLEARANCE_MAX = 0.6
HARD_RATIO_MIN = 0.5
CLEARANCE_TO_LENGTH_MIN = 0.085
HARD_RATIO_MAX = 0.52
CLEARANCE_TO_LENGTH_MAX = 0.112
TRACK_LENGTH_MIN = 0.6
TRACK_LENGTH_MAX = 0.64
VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT = 1.1
_LOG_INIT_PARAMS = False
RESTITUTION = 0.5
FRICTION_RATIO = 1.0
NUM_ITERATIONS = 10
NUM_ITERATIONS_ACCURATE = 40
MID_SOLVING_ITERATIONS = 4
NUM_SUBSTEPS_IN_STANDARD_MODE = 2
USE_SSE_SOLVER_IN_STANDARD_MODE = False
NUM_SUBSTEPS_IN_DETAILED_MODE = 3
USE_SSE_SOLVER_IN_DETAILED_MODE = False
NUM_SUBSTEPS = NUM_SUBSTEPS_IN_STANDARD_MODE
WARMSTARTING_VEHICLE_VEHICLE = False
WARMSTARTING_VEHICLE_STATICS = False
WARMSTARTING_THRESHOLD = 0.1
USE_PSEUDO_CONTACTS = True
ALLOWED_PENETRATION = 0.01
CONTACT_PENETRATION = 0.1
TRACKS_PENETRATION = 0.01
CONTACT_ENERGY_POW = 3.0
CONTACT_ENERGY_POW2 = 0.75
SLOPE_FRICTION_FUNC_DEF = tuple((math.pi * ang / 180.0 for ang in (34.0, 50.0, 70.0)))
SLOPE_FRICTION_FUNC_VAL = (0.4, 2.0, 5.0)
SLOPE_FRICTION_MODELS_FUNC_VAL = (0.4, 0.45, 0.5)
CONTACT_FRICTION_TERRAIN = 1.0
CONTACT_FRICTION_STATICS = 0.05
CONTACT_FRICTION_STATICS_VERT = 0.25
CONTACT_FRICTION_DESTRUCTIBLES = 1.0
CONTACT_FRICTION_VEHICLES = 0.3
VEHICLE_ON_BODY_DEFAULT_FRICTION = 0.5
ROLLER_FRICTION_GAIN_MIN = 0.05
ROLLER_FRICTION_GAIN_MAX = 0.25
ROLLER_FRICTION_ANGLE_MIN = 20.0
ROLLER_FRICTION_ANGLE_MAX = 45.0
ANCHOR_MAX_REACTION_FACTOR = 0.5
ANCHOR_CONST_FRACTION = 0.0
ANCHOR_VEL_FACTOR = 0.0
ARENA_BOUNDS_FRICTION_HOR = 0.2
ARENA_BOUNDS_FRICTION_VERT = 1.0
_ALLOWER_RPM_EXCESS_UNBOUNDED = 1.4
_ABSOLUTE_SPEED_LIMIT = 25
g_confUpdaters = []

def _cosDeg(angle):
    return math.cos(math.radians(angle))


def _sinDeg(angle):
    return math.sin(math.radians(angle))


g_defaultChassisXPhysicsCfg = {'wheelRadius': 0.4,
 'wheelRestitution': 0.9,
 'wheelPenetration': 0.02,
 'wheelUsePseudoContacts': True,
 'wheelFwdInertiaFactor': 3.0,
 'sideFrictionConstantRatio': 0.0,
 'flatSideFriction': True,
 'wheelDetachOnRoll': False,
 'trackToBeLockedDelay': 1.0,
 'trackGaugeFactor': 0.96,
 'slopeResistTerrain': (1.5, _cosDeg(15.0), _sinDeg(29.0)),
 'slopeResistStaticObject': (1.5, _cosDeg(15.0), _sinDeg(20.0)),
 'slopeResistDynamicObject': (1.5, _cosDeg(15.0), _sinDeg(20.0)),
 'slopeGripLngTerrain': (_cosDeg(27.5),
                         1.0,
                         _cosDeg(32.0),
                         0.1),
 'slopeGripSdwTerrain': (_cosDeg(24.5),
                         1.0,
                         _cosDeg(29.0),
                         0.1),
 'slopeGripLngStaticObject': (_cosDeg(20),
                              1.0,
                              _cosDeg(25),
                              0.1),
 'slopeGripSdwStaticObject': (_cosDeg(20),
                              1.0,
                              _cosDeg(25),
                              0.1),
 'slopeGripLngDynamicObject': (_cosDeg(20),
                               1.0,
                               _cosDeg(25),
                               0.1),
 'slopeGripSdwDynamicObject': (_cosDeg(20),
                               1.0,
                               _cosDeg(25),
                               0.1),
 'stiffnessFactors': (1.0, 1.0, 1.0, 1.0, 1.0),
 'angVelocityFactor': 1.0,
 'angVelocityFactor0': 1.0,
 'gimletGoalWOnSpot': 1.0,
 'gimletGoalWOnMove': 1.0,
 'isRotationAroundCenter': False,
 'centerRotationFwdSpeed': 1.0,
 'movementRevertSpeed': 1.0,
 'fwLagRatio': 1.0,
 'bkLagRatio': 1.0,
 'rotFritionFactor': 1.0,
 'comFrictionYOffs': 1.0,
 'comSideFriction': 1.0,
 'pushStop': 1.0,
 'gimletPushOnSpotInit': 1.0,
 'gimletPushOnSpotFinal': 1.0,
 'gimletPushOnMoveInit': 1.0,
 'gimletPushOnMoveFinal': 1.0,
 'gimletVelScaleMin': 1.0,
 'gimletVelScaleMax': 1.0,
 'pushRotOnSpotFixedPeriod': 1.0,
 'pushRotOnMoveFixedPeriod': 1.0,
 'pushRotOnSpotGrowPeriod': 1.0,
 'pushRotOnMoveGrowPeriod': 1.0,
 'bodyHeight': 2.5,
 'hullCOMShiftY': -0.25,
 'hullInertiaFactors': (1.0, 1.0, 1.0),
 'clearance': 0.25,
 'rotationByLockChoker': 1.0,
 'chassisMassFraction': 0.3,
 'wheelSinkageResistFactor': 0.2,
 'wheelInertiaFactor': 1.5,
 'stiffness0': 1.0,
 'stiffness1': 1.0,
 'damping': 0.2,
 'brake': 1000.0,
 'rotationBrake': 1000.0,
 'roadWheelPositions': (-2.5, -1.25, 0.0, 1.25, 2.5)}
g_defaultWheeledChassisXPhysicsCfg = copy.deepcopy(g_defaultChassisXPhysicsCfg)
g_defaultWheeledChassisXPhysicsCfg.update({'axleSteeringLockAngles': (0.0, 0.0, 0.0, 30.0),
 'axleSteeringAngles': (0.0, 0.0, 0.0, 15.0),
 'axleSteeringSpeed': (0.0, 0.0, 0.0, 90.0),
 'fwdFrictionOnAxisModifiers': (1.0, 1.0, 1.0, 1.0),
 'sideFrictionOnAxisModifiers': (1.0, 1.0, 1.0, 1.0),
 'sideFrictionConstantRatioOnAxis': (0.0, 0.0, 0.0, 0.0),
 'sinkageResistOnAxis': (0.0, 0.0, 0.0, 0.0),
 'axleIsLeading': (True,
                   True,
                   True,
                   True),
 'axleCanBeRised': (False,
                    True,
                    True,
                    False),
 'wheelRiseHeight': 0.2,
 'wheelRiseSpeed': 1.0,
 'enableRail': True,
 'handbrakeBrakeForce': 10.0,
 'brokenWheelRollingFrictionModifier': 10.0,
 'noSignalBrakeForce': 10.0,
 'afterDeathBrakeForce': 10.0,
 'afterDeathMinSpeedForImpulse': 29.0,
 'afterDeathImpulse': 1.0,
 'jumpingFactor': 30.0,
 'jumpingMinForce': 70.0,
 'slowTurnChocker': 0.5,
 'airPitchReduction': 0.0,
 'wheelToHullRollTransmission': 1.0,
 'steeringSpeedInTurnMultiplier': 1.0,
 'burnout': {'preparationTime': 3.0,
             'activityTime': 1.0,
             'engineDamageMin': 100.0,
             'engineDamageMax': 200.0,
             'warningMaxHealth': 100.0,
             'warningMaxHealthCritEngine': 50.0,
             'power': 1.0,
             'impulse': 0.0}})
g_defaultVehicleXPhysicsCfg = {'mode_index': 0,
 'gravity': 9.81,
 'hullCOMShiftY': 0.0,
 'clearance': 0.7,
 'overspeedResistBaseFactor': 0.5,
 'allowedRPMExcessUnbounded': 1.4,
 'absoluteSpeedLimit': 25.0,
 'shape': {'useComplexForm': False,
           'isParametricShape': True,
           'terrAftChamferFraction': 0.5,
           'terrFrontChamferFraction': 0.5,
           'terrBoardAngle': 0.0,
           'tankAftChamferFraction': 0.25,
           'tankFrontChamferFraction': 0.25,
           'tankBoardAngle': 0.0,
           'auxClearance': 0.8},
 'engine': {'engineTorque': ((500.0, 2.0),
                             (1000.0, 3.0),
                             (2000.0, 2.5),
                             (2500.0, 2.0)),
            'smplEngPower': 800.0,
            'smplMinRPM': 150.0,
            'smplEnginePower': 1.0,
            'rotationChoker': 1.0,
            'smplFwMaxSpeed': 15.0,
            'smplBkMaxSpeed': 10.0,
            'powerFactor': 1.0,
            'rotationFactor': 1.0,
            'engineLoses': (0.5, 0.8),
            'engineInertia': 0.02,
            'idleChoker': 0.2,
            'idleRPM': 800.0,
            'startRPM': 1000.0},
 'comFrictionYOffs': 0.7,
 'smplFwMaxSpeed': 10.0,
 'smplBkMaxSpeed': 5.5,
 'pushStop': 0.3,
 'rail': {'railFactorInContact': 0.5},
 'anchor': {'anchorMaxReactionFactor': ANCHOR_MAX_REACTION_FACTOR,
            'anchorConstFraction': ANCHOR_CONST_FRACTION,
            'anchorVelFactor': ANCHOR_VEL_FACTOR},
 'gimlet': {'pushInContact': 2.5},
 'gimletVelScaleMin': 1.0,
 'gimletVelScaleMax': 5.0,
 'pushRotOnSpotFixedPeriod': 0.2,
 'pushRotOnMoveFixedPeriod': 0.2,
 'pushRotOnSpotGrowPeriod': 2.0,
 'pushRotOnMoveGrowPeriod': 2.0,
 'swingCompensatorCollisionExtend': 0.2,
 'swingCompensatorStiffnesFactor0': 1.0,
 'swingCompensatorStiffnesFactor1': 1.0,
 'swingCompensatorDampingFactor': 1.0,
 'swingCompensatorMaxPitchDeviation': 0.1,
 'swingCompensatorMaxRollDeviation': 0.1,
 'swingCompensatorRestitution': 0.8,
 'swingCompensatorStabilisationCenter': (0.0, 0.0, 0.0),
 'powerFactor': 1.0,
 'angVelocityFactor': 1.0,
 'angVelocityFactor0': 1.0,
 'gimletGoalWOnSpot': 0.0,
 'gimletGoalWOnMove': 0.0,
 'rotationFactor': 1.0,
 'hullAiming': {'pitch': {'correctionCenterZ': 0.0,
                          'correctionSpeed': 0.3,
                          'pitchMin': -0.2,
                          'pitchMax': 0.2,
                          'correctionStiffness': 30.0,
                          'correctionDamping': 0.25,
                          'correctionScale': 0.5},
                'yaw': {'gimletForce': 4.0,
                        'stiffness': 8000.0,
                        'damping': 400.0,
                        'preciseRestitution': 0.3,
                        'dampingYawDist': 0.03,
                        'preciseYawDist': 0.03}},
 'hullInertiaFactors': (1.0, 1.0, 1.8),
 'engineLoses': (0.5, 0.8),
 'enableSabilization': True,
 'modes': {'siegeMode': {'mode_index': 1,
                         'engine': {'smplEnginePower': 1.0},
                         'powerFactor': 1.0,
                         'angVelocityFactor': 1.0,
                         'angVelocityFactor0': 1.0,
                         'gimletGoalWOnSpot': 0.0,
                         'gimletGoalWOnMove': 0.0,
                         'rotationFactor': 1.0}}}
g_defaultTankXPhysicsCfg = copy.deepcopy(g_defaultVehicleXPhysicsCfg)
g_defaultTankXPhysicsCfg.update({'vehiclePhysicsType': VEHICLE_PHYSICS_TYPE.TANK,
 'chassis': g_defaultChassisXPhysicsCfg})
g_defaultWheeledTechXPhysicsCfg = copy.deepcopy(g_defaultVehicleXPhysicsCfg)
g_defaultWheeledTechXPhysicsCfg.update({'vehiclePhysicsType': VEHICLE_PHYSICS_TYPE.WHEELED_TECH,
 'chassis': g_defaultWheeledChassisXPhysicsCfg})

def init():
    updateCommonConf()


def updateCommonConf():
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW', CONTACT_ENERGY_POW)
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW2', CONTACT_ENERGY_POW2)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_DEF', SLOPE_FRICTION_FUNC_DEF)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_VAL', SLOPE_FRICTION_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_MODELS_FUNC_VAL', SLOPE_FRICTION_MODELS_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_TERRAIN', CONTACT_FRICTION_TERRAIN)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_STATICS', CONTACT_FRICTION_STATICS)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_STATICS_VERT', CONTACT_FRICTION_STATICS_VERT)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_DESTRUCTIBLES', CONTACT_FRICTION_DESTRUCTIBLES)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_VEHICLES', CONTACT_FRICTION_VEHICLES)
    BigWorld.wg_setupPhysicsParam('VEHICLE_ON_BODY_DEFAULT_FRICTION', VEHICLE_ON_BODY_DEFAULT_FRICTION)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_GAIN_MIN', ROLLER_FRICTION_GAIN_MIN)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_GAIN_MAX', ROLLER_FRICTION_GAIN_MAX)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_ANGLE_MIN', ROLLER_FRICTION_ANGLE_MIN)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_ANGLE_MAX', ROLLER_FRICTION_ANGLE_MAX)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_HOR', ARENA_BOUNDS_FRICTION_HOR)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_VERT', ARENA_BOUNDS_FRICTION_VERT)
    BigWorld.wg_setupPhysicsParam('USE_PSEUDO_CONTACTS', USE_PSEUDO_CONTACTS)
    BigWorld.wg_setupPhysicsParam('CONTACT_PENETRATION', CONTACT_PENETRATION)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_VEHICLE', WARMSTARTING_VEHICLE_VEHICLE)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_STATICS', WARMSTARTING_VEHICLE_STATICS)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_THRESHOLD', WARMSTARTING_THRESHOLD)


def updateConf():
    for e in BigWorld.entities.values():
        if e.className == 'Vehicle':
            initVehiclePhysicsServer(e.mover.physics, e.typeDescriptor)

    updateCommonConf()
    for updater in g_confUpdaters:
        updater()


def updatePhysicsCfg(baseCfg, typeDesc, cfg):
    if typeDesc.type.xphysics['detailed'] != baseCfg:
        typeDesc.type.xphysics['detailed'].update(baseCfg)
    engName = typeDesc.engine.name
    engCfg = baseCfg['engines'].get(engName)
    if engCfg:
        cfg.setdefault('engine', {}).update(engCfg)
    chsName = typeDesc.chassis.name
    chsCfg = baseCfg['chassis'].get(chsName)
    if chsCfg:
        cfg.setdefault('chassis', {}).update(chsCfg)
        groundsSrc = cfg['chassis']['grounds'].copy()
        softCfg = groundsSrc['soft']
        del groundsSrc['soft']
        idMap = EFFECT_MATERIAL_INDEXES_BY_NAMES
        cfg['chassis']['grounds'] = dict(((idMap[nm], dict(sub.items() + [('soft', softCfg)])) for nm, sub in groundsSrc.iteritems()))
    fakeGearBox = baseCfg.get('fakegearbox')
    if fakeGearBox is not None:
        cfg['fakegearbox'] = fakeGearBox
    return


def configurePhysics(physics, baseCfg, typeDesc, gravityFactor, updateSiegeModeFromCfg):
    vehiclePhysicsType = typeDesc.type.xphysics['detailed'].get('vehiclePhysicsType', VEHICLE_PHYSICS_TYPE.TANK)
    isTank = vehiclePhysicsType == VEHICLE_PHYSICS_TYPE.TANK
    cfg = copy.deepcopy(g_defaultTankXPhysicsCfg if isTank else g_defaultWheeledTechXPhysicsCfg)
    if typeDesc.hasSiegeMode:
        defaultVehicleDescr = typeDesc.defaultVehicleDescr
        siegeVehicleDescr = typeDesc.siegeVehicleDescr
    else:
        defaultVehicleDescr = typeDesc
    try:
        cfg['fakegearbox'] = typeDesc.type.xphysics['detailed']['fakegearbox']
    except:
        cfg['fakegearbox'] = {'fwdgears': {'switchSpeed': (2, 5, 15),
                      'switchHysteresis': (1, 2, 3),
                      'lowRpm': (0.2, 0.2, 0.2),
                      'highRpm': (0.9, 0.9, 0.9)},
         'bkwdgears': {'switchSpeed': (2, 5, 15),
                       'switchHysteresis': (1, 2, 3),
                       'lowRpm': (0.2, 0.2, 0.2),
                       'highRpm': (0.9, 0.9, 0.9)}}

    if baseCfg:
        updatePhysicsCfg(baseCfg, defaultVehicleDescr, cfg)
        if typeDesc.hasSiegeMode:
            if updateSiegeModeFromCfg and 'modes' in baseCfg and 'siegeMode' in baseCfg['modes']:
                siegeBaseCfg = baseCfg['modes']['siegeMode']
            else:
                siegeBaseCfg = siegeVehicleDescr.type.xphysics['detailed']
            updatePhysicsCfg(siegeBaseCfg, siegeVehicleDescr, cfg['modes']['siegeMode'])
    cfg = __buildConfigurations(cfg)
    for name, mode in cfg['modes'].iteritems():
        configurePhysicsMode(mode, typeDesc, gravityFactor)

    if not physics.configure(cfg):
        LOG_ERROR('configureXPhysics: configure failed')
    physics.centerOfMass = Math.Vector3((0.0, cfg['modes']['normal']['clearance'] + cfg['modes']['normal']['bodyHeight'] * 0.5 + cfg['modes']['normal']['hullCOMShiftY'], physics.hullCOMZ))
    physics.isFrozen = False
    physics.movementSignals = 0
    physics.freezeAccelEpsilon = FREEZE_ACCEL_EPSILON
    physics.freezeAngAccelEpsilon = FREEZE_ANG_ACCEL_EPSILON
    physics.freezeVelEpsilon = FREEZE_VEL_EPSILON
    physics.freezeAngVelEpsilon = FREEZE_ANG_VEL_EPSILON
    physics.simulationYBound = _SIMULATION_Y_BOUND
    return cfg


def configurePhysicsMode(cfg, typeDesc, gravityFactor):
    cfg['angVelocityFactor'] = cfg['chassis']['angVelocityFactor']
    cfg['angVelocityFactor0'] = cfg['chassis']['angVelocityFactor0']
    cfg['axleCount'] = cfg['chassis']['axleCount']
    if cfg['vehiclePhysicsType'] == VEHICLE_PHYSICS_TYPE.WHEELED_TECH:
        for key in ('axleSteeringLockAngles', 'axleSteeringAngles', 'axleSteeringSpeed', 'fwdFrictionOnAxisModifiers', 'sideFrictionOnAxisModifiers', 'sideFrictionConstantRatioOnAxis', 'sinkageResistOnAxis', 'axleIsLeading', 'axleCanBeRised', 'wheelRiseHeight', 'wheelRiseSpeed', 'enableRail', 'handbrakeBrakeForce', 'brokenWheelRollingFrictionModifier', 'noSignalBrakeForce', 'afterDeathBrakeForce', 'afterDeathMinSpeedForImpulse', 'afterDeathImpulse', 'jumpingFactor', 'jumpingMinForce', 'slowTurnChocker', 'airPitchReduction', 'wheelToHullRollTransmission', 'steeringSpeedInTurnMultiplier'):
            cfg[key] = cfg['chassis'][key]

    cfg['gimletGoalWOnSpot'] = cfg['chassis']['gimletGoalWOnSpot']
    cfg['gimletGoalWOnMove'] = cfg['chassis']['gimletGoalWOnMove']
    cfg['isRotationAroundCenter'] = cfg['chassis']['isRotationAroundCenter']
    cfg['centerRotationFwdSpeed'] = cfg['chassis']['centerRotationFwdSpeed']
    cfg['movementRevertSpeed'] = cfg['chassis']['movementRevertSpeed']
    cfg['fwLagRatio'] = cfg['chassis']['fwLagRatio']
    cfg['bkLagRatio'] = cfg['chassis']['bkLagRatio']
    cfg['rotFritionFactor'] = cfg['chassis']['rotFritionFactor']
    cfg['comFrictionYOffs'] = cfg['chassis']['comFrictionYOffs']
    cfg['comSideFriction'] = cfg['chassis']['comSideFriction']
    cfg['pushStop'] = cfg['chassis']['pushStop']
    cfg['gimletPushOnSpotInit'] = cfg['chassis']['gimletPushOnSpotInit']
    cfg['gimletPushOnSpotFinal'] = cfg['chassis']['gimletPushOnSpotFinal']
    cfg['gimletPushOnMoveInit'] = cfg['chassis']['gimletPushOnMoveInit']
    cfg['gimletPushOnMoveFinal'] = cfg['chassis']['gimletPushOnMoveFinal']
    cfg['gimletVelScaleMin'] = cfg['chassis']['gimletVelScaleMin']
    cfg['gimletVelScaleMax'] = cfg['chassis']['gimletVelScaleMax']
    cfg['pushRotOnSpotFixedPeriod'] = cfg['chassis']['pushRotOnSpotFixedPeriod']
    cfg['pushRotOnMoveFixedPeriod'] = cfg['chassis']['pushRotOnMoveFixedPeriod']
    cfg['pushRotOnSpotGrowPeriod'] = cfg['chassis']['pushRotOnSpotGrowPeriod']
    cfg['pushRotOnMoveGrowPeriod'] = cfg['chassis']['pushRotOnMoveGrowPeriod']
    cfg['smplFwMaxSpeed'] = cfg['engine']['smplFwMaxSpeed']
    cfg['smplBkMaxSpeed'] = cfg['engine']['smplBkMaxSpeed']
    cfg['powerFactor'] = cfg['engine']['powerFactor']
    cfg['rotationFactor'] = cfg['engine']['rotationFactor']
    cfg['bodyHeight'] = cfg['chassis']['bodyHeight']
    cfg['hullCOMShiftY'] = cfg['chassis']['hullCOMShiftY']
    cfg['hullInertiaFactors'] = cfg['chassis']['hullInertiaFactors']
    cfg['clearance'] = cfg['chassis']['clearance']
    cfg['fullMass'] = typeDesc.physics['weight'] * WEIGHT_SCALE
    selfDrivenMaxSpeed = max(cfg['smplFwMaxSpeed'], cfg['smplBkMaxSpeed'])
    speedLimit = min(cfg['absoluteSpeedLimit'], selfDrivenMaxSpeed * cfg['allowedRPMExcessUnbounded'])
    cfg['allowedRPMExcess'] = max(1.0, speedLimit / selfDrivenMaxSpeed)
    cfg['overspeedResistFactor'] = cfg['overspeedResistBaseFactor'] / selfDrivenMaxSpeed
    cfg['useComplexForm'] = typeDesc.type.name == 'sweden:S11_Strv_103B'
    bmin, bmax, _ = typeDesc.chassis.hitTester.bbox
    sizeX = bmax[0] - bmin[0]
    if typeDesc.hasSiegeMode and typeDesc.type.useHullZ:
        bmin_, bmax_, _ = typeDesc.hull.hitTester.bbox
        sizeZ = bmax_[2] - bmin_[2]
    else:
        sizeZ = bmax[2] - bmin[2]
    hullCenter = (bmin + bmax) * 0.5
    if typeDesc.isWheeledVehicle:
        wheelBbMin, wheelBbMax, _ = typeDesc.chassis.wheels.wheels[-1].hitTester.bbox
        wheelX = wheelBbMax[0] - wheelBbMin[0]
        wheelZ = wheelBbMax[2] - wheelBbMin[2]
        sizeX += wheelX * 2.0
        sizeZ += wheelZ * 0.5
    cfg['hullSize'] = Math.Vector3((sizeX, cfg['bodyHeight'], sizeZ))
    cfg['shape']['useComplexForm'] = typeDesc.type.name == 'sweden:S11_Strv_103B'
    cfg['gravity'] = cfg['gravity'] * gravityFactor
    cfg['engine']['engineTorque'] = tuple(((arg, val * gravityFactor) for arg, val in cfg['engine']['engineTorque']))
    offsZ = hullCenter[2]
    cfg['hullBoxOffsetZ'] = offsZ
    turretMin, turretMax, _ = typeDesc.turret.hitTester.bbox
    _, gunMax, _ = typeDesc.gun.hitTester.bbox
    hullPos = typeDesc.chassis.hullPosition
    turretPos = typeDesc.hull.turretPositions[0]
    topPos = hullPos + turretPos
    turretTopOffset = max(turretMax[1], typeDesc.turret.gunPosition[1] + gunMax[1])
    topPos.y += turretTopOffset - cfg['clearance'] - cfg['bodyHeight']
    topPos.y = max(0.1, topPos.y * 0.8)
    topPos.y += cfg['bodyHeight'] * 0.5
    cfg['turretTopPos'] = topPos
    cfg['turretTopWidth'] = max(sizeX * 0.25, (turretMax[0] - turretMin[0]) * 0.7)
    cfg['pushHB'] = cfg.get('gimletPushOnSpotFinal', 0.0)
    cfg['engine']['smplEngJoinRatio'] = 0.020000000000000004 / cfg['chassis']['wheelRadius']
    applyRotationAndPowerFactors(cfg)
    cfg['siegeModeAvailable'] = typeDesc.hasSiegeMode
    cfg['isWheeledVehicle'] = typeDesc.isWheeledVehicle
    hullAimingParams = typeDesc.type.hullAimingParams
    hullAimingParamsPitch = hullAimingParams['pitch']
    hullAimingPitchCfg = cfg['hullAiming']['pitch']
    hullAimingPitchCfg['correctionCenterZ'] = hullAimingParamsPitch['wheelCorrectionCenterZ']
    hullAimingPitchCfg['correctionSpeed'] = hullAimingParamsPitch['wheelsCorrectionSpeed']
    hullAimingPitchCfg['pitchMin'] = -hullAimingParamsPitch['wheelsCorrectionAngles']['pitchMax']
    hullAimingPitchCfg['pitchMax'] = -hullAimingParamsPitch['wheelsCorrectionAngles']['pitchMin']
    withHullAiming = hullAimingParams['yaw']['isAvailable'] or hullAimingParamsPitch['isAvailable']
    cfg['enableSabilization'] = not withHullAiming
    cfg['gimlet']['wPushedRot'] = cfg['wPushedRot']
    cfg['gimlet']['wPushedDiag'] = cfg['wPushedDiag']
    cfg['gimlet']['wPushedHB'] = cfg['wPushedHB']
    cfg['gimlet']['pushHB'] = cfg['pushHB']
    cfg['gimlet']['pushStop'] = cfg['pushStop']
    cfg['gimlet']['gimletPushOnSpotInit'] = cfg['gimletPushOnSpotInit']
    cfg['gimlet']['gimletPushOnSpotFinal'] = cfg['gimletPushOnSpotFinal']
    cfg['gimlet']['gimletPushOnMoveInit'] = cfg['gimletPushOnMoveInit']
    cfg['gimlet']['gimletPushOnMoveFinal'] = cfg['gimletPushOnMoveFinal']
    cfg['gimlet']['gimletVelScaleMin'] = cfg['gimletVelScaleMin']
    cfg['gimlet']['gimletVelScaleMax'] = cfg['gimletVelScaleMax']
    cfg['gimlet']['pushRotOnSpotFixedPeriod'] = cfg['pushRotOnSpotFixedPeriod']
    cfg['gimlet']['pushRotOnMoveFixedPeriod'] = cfg['pushRotOnMoveFixedPeriod']
    cfg['gimlet']['pushRotOnSpotGrowPeriod'] = cfg['pushRotOnSpotGrowPeriod']
    cfg['gimlet']['pushRotOnMoveGrowPeriod'] = cfg['pushRotOnMoveGrowPeriod']
    cfg['engine']['rotationByLockChoker'] = cfg['chassis']['rotationByLockChoker']
    del cfg['chassis']['rotationByLockChoker']
    cfg['engine']['engVelMax'] = cfg['smplFwMaxSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['engine']['engVelBkMax'] = cfg['smplBkMaxSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['engine']['engVelRot'] = cfg['smplRotSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['chassis']['chassisMass'] = cfg['fullMass'] * cfg['chassis']['chassisMassFraction']
    cfg['chassis']['hullAiming'] = cfg['hullAiming']


def applyRotationAndPowerFactors(cfg):
    try:
        cfg['engine']['smplEnginePower'] = cfg['engine']['smplEnginePower'] * cfg['powerFactor']
        cfg['angVelocityFactor'] = cfg['angVelocityFactor'] * cfg['rotationFactor']
        arm = cfg['hullSize'][0]
        cfg['smplRotSpeed'] = arm * cfg['angVelocityFactor0'] * cfg['rotationFactor']
        cfg['gimletGoalWOnSpot'] = cfg['gimletGoalWOnSpot'] * cfg['rotationFactor']
        cfg['gimletGoalWOnMove'] = cfg['gimletGoalWOnMove'] * cfg['rotationFactor']
        cfg['wPushedRot'] = cfg['gimletGoalWOnSpot']
        cfg['wPushedHB'] = cfg['wPushedRot'] * 0.98
        cfg['wPushedDiag'] = cfg['gimletGoalWOnMove']
    except:
        LOG_CURRENT_EXCEPTION()


def initVehiclePhysicsServer(physics, typeDesc):
    baseCfg = typeDesc.type.xphysics['detailed']
    gravityFactor = baseCfg['gravityFactor']
    configurePhysics(physics, baseCfg, typeDesc, gravityFactor, False)


def initVehiclePhysicsForced(physics, typeDesc, forcedCfg):
    baseCfg = forcedCfg
    gravityFactor = forcedCfg['gravityFactor']
    configurePhysics(physics, baseCfg, typeDesc, gravityFactor, True)


def initVehiclePhysicsEditor(physics, typeDesc):
    if not hasattr(typeDesc.type.xphysics, 'detailed'):
        typeDesc.type.xphysics['detailed'] = {'engines': {typeDesc.engine.name: {'startRPM': 1500,
                                            'powerFactor': 1,
                                            'rotationFactor': 0.857143,
                                            'engineTorque': ((500, 2.7),
                                                             (1000, 3.15),
                                                             (1500, 3.45),
                                                             (2500, 2.55)),
                                            'engineLoses': (0.13229, 6.614494),
                                            'engineSupression': (0, 1, 1, 1),
                                            'engineInertia': 0.01777,
                                            'idleRPM': 1000,
                                            'idleChoker': 0.1,
                                            'smplEnginePower': 634.3687,
                                            'smplFwMaxSpeed': 34,
                                            'smplBkMaxSpeed': 14,
                                            'rotationChoker': 0.9}},
         'chassis': {typeDesc.chassis.name: {'angVelocityFactor0': 0.847066,
                                             'hullCOM': (0, 1.118153, -0.00721),
                                             'chassisMassFraction': 0.3,
                                             'hullCOMShiftY': -0.1,
                                             'wheelRadius': 0.4,
                                             'bodyHeight': 1.136306,
                                             'clearance': 0.65,
                                             'wheelStroke': 0.3,
                                             'roadWheelPositions': (-2.702271, -1.35474, -0.00721, 1.340321, 2.687851),
                                             'rearDriveWheelPosition': (-3.211225, 1.786306),
                                             'frontDriveWheelPosition': (3.218897, 1.786306),
                                             'stiffness0': 243.6666,
                                             'stiffness1': 263.4825,
                                             'stiffnessFactors': (1, 1, 1, 1, 1),
                                             'damping': 26.34825,
                                             'movementRevertSpeed': 2,
                                             'isRotationAroundCenter': False,
                                             'comSideFriction': 1.5,
                                             'comFrictionYOffs': 0,
                                             'hullInertiaFactors': (1.8, 2, 1.6),
                                             'rotationBrake': 30.04625,
                                             'brake': 46225,
                                             'wheelInertiaFactor': 1,
                                             'angVelocityFactor': 0.720007,
                                             'wheelSinkageResistFactor': 0,
                                             'rotFritionFactor': 0,
                                             'pushStop': 0.116733,
                                             'sideFrictionConstantRatio': 0,
                                             'centerRotationFwdSpeed': 7.462401,
                                             'rotationByLockChoker': 0.8,
                                             'fwLagRatio': 0.6,
                                             'bkLagRatio': 0.4,
                                             'grounds': {'soft': {'dirtCumulationRate': 4,
                                                                  'dirtReleaseRate': 4,
                                                                  'dirtSideVelocity': 32.4,
                                                                  'maxDirt': 1,
                                                                  'sideFriction': 1.1,
                                                                  'fwdFriction': 1.3,
                                                                  'rollingFriction': 0.2093,
                                                                  'hbComSideFriction': 0,
                                                                  'hbSideFrictionAddition': 0,
                                                                  'rotationFactor': 0.405392}},
                                             'gimletGoalWOnSpot': 0.65159,
                                             'gimletPushOnSpotInit': 0.1,
                                             'gimletPushOnSpotFinal': 4,
                                             'pushRotOnSpotFixedPeriod': 0.13,
                                             'pushRotOnSpotGrowPeriod': 0.433333,
                                             'gimletGoalWOnMove': 0.553851,
                                             'gimletPushOnMoveInit': 0.391833,
                                             'gimletPushOnMoveFinal': 4,
                                             'pushRotOnMoveFixedPeriod': 0.03,
                                             'pushRotOnMoveGrowPeriod': 0.4,
                                             'gimletVelScaleMin': 0.1,
                                             'gimletVelScaleMax': 2,
                                             'chsDmgMultiplier': 1,
                                             'axleCount': 5}},
         'gravityFactor': 1.25,
         'fakegearbox': {'fwdgears': {'switchSpeed': (2.833334, 4.722222, 7.555556),
                                      'switchHysteresis': (0.5, 0.472222, 0.755556),
                                      'lowRpm': (0.4, 0.3, 0.3),
                                      'highRpm': (1.2, 1, 1)},
                         'bkwdgears': {'switchSpeed': (1.166667, 2.333333),
                                       'switchHysteresis': (1, 1),
                                       'lowRpm': (0.4, 0.4),
                                       'highRpm': (1, 1)}}}
    baseCfg = typeDesc.type.xphysics['detailed']
    gravityFactor = 1.0
    configurePhysics(physics, baseCfg, typeDesc, gravityFactor, False)


def initVehiclePhysicsClient(physics, typeDesc):
    physDescr = typeDesc.physics
    hullMin, hullMax, _ = typeDesc.hull.hitTester.bbox
    hullCenter = (hullMin + hullMax) * 0.5
    hullY = hullCenter.y + typeDesc.chassis.hullPosition.y
    hullHeight = hullMax.y - hullMin.y
    bmin, bmax, _ = typeDesc.chassis.hitTester.bbox
    chassisCenter = (bmin + bmax) * 0.5
    blen = bmax[2] - bmin[2]
    width = bmax[0] - bmin[0]
    height = bmax[1] - bmin[1]
    if blen == 0.0 and width == 0.0 and height == 0.0:
        LOG_ERROR('Invalid bounding box for', typeDesc.name)
        blen = width = height = 1.0
    srcEnginePower = physDescr['enginePower']
    srcMass = physDescr['weight']
    fullMass = physDescr['weight'] * WEIGHT_SCALE
    clearance = (typeDesc.chassis.hullPosition.y + hullMin.y) * CLEARANCE
    clearance = _clamp(CLEARANCE_MIN * height, clearance, CLEARANCE_MAX * height)
    suspCompression = _computeSuspCompression(fullMass)
    carringSpringLength = clearance / suspCompression
    cmShift = _computeCenterOfMassShift(srcMass, srcEnginePower)
    physics.centerOfMass = Math.Vector3((0.0, hullY + cmShift * hullHeight, 0.0))
    chassisMaxY = bmax[1]
    hullPosY = typeDesc.chassis.hullPosition[1]
    hullMaxY = hullPosY + hullMax[1]
    turretPosY = typeDesc.hull.turretPositions[0][1]
    turretMaxY = hullPosY + turretPosY + typeDesc.turret.hitTester.bbox[1][1]
    commonBoxMaxY = max(chassisMaxY, hullMaxY, turretMaxY)
    gunPosY = hullPosY + turretPosY + typeDesc.turret.gunPosition[1]
    hullUpperBound = typeDesc.chassis.hullPosition.y + hullMax.y
    boxHeight = min(commonBoxMaxY, gunPosY, hullUpperBound * BODY_HEIGHT) - clearance
    boxHeight = max(chassisMaxY * 0.7, boxHeight, VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT)
    globalBoxY = clearance + boxHeight / 2
    boxCenter = Math.Vector3(chassisCenter)
    boxCenter[1] = globalBoxY - physics.centerOfMass.y
    physics.removeAllDamperSprings()
    if clearance != 0.0:
        clearanceRatio = width / clearance
    else:
        LOG_ERROR('Clearance is null')
        clearanceRatio = CLEARANCE_RATIO_LONG
    if width < WIDTH_VERY_LONG and (width < WIDTH_LONG or clearanceRatio < CLEARANCE_RATIO_LONG):
        carrierSpringPairs = NUM_SPRINGS_NORMAL
    else:
        carrierSpringPairs = NUM_SPRINGS_LONG
    length = carringSpringLength
    hullAimingLength = carringSpringLength
    trackLen = _computeTrackLength(clearance, blen)
    indent = boxHeight / 2
    hardRatio = _computeHardRatio(clearance, blen)
    if IS_CLIENT and typeDesc.isPitchHullAimingAvailable:
        hardRatio = 0
        hullAngleMin = typeDesc.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMin']
        hullAngleMax = typeDesc.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMax']
        backSpringLength = blen * math.sin(abs(hullAngleMax)) * 1.25
        frontSpringLength = blen * math.sin(abs(hullAngleMin)) * 1.25
        hullAimingLength = max(backSpringLength, frontSpringLength)
    if IS_CLIENT and typeDesc.hasSiegeMode and typeDesc.isPitchHullAimingAvailable:
        springsLengthList = tuple((length for _ in xrange(0, carrierSpringPairs)))
        hullAimingSpringsLengthList = tuple((hullAimingLength for _ in xrange(0, carrierSpringPairs)))
        for descriptor in [typeDesc.defaultVehicleDescr, typeDesc.siegeVehicleDescr]:
            if descriptor.chassis.suspensionSpringsLength is not None:
                break
            hullAimingEnabled = descriptor.type.hullAimingParams['pitch']['isEnabled']
            descriptor.chassis.suspensionSpringsLength = {'left': hullAimingSpringsLengthList if hullAimingEnabled else springsLengthList,
             'right': hullAimingSpringsLengthList if hullAimingEnabled else springsLengthList}

    stepZ = trackLen / (carrierSpringPairs - 1)
    begZ = -trackLen * 0.5
    leftX = -width * 0.45
    rightX = width * 0.45
    y = -boxHeight / 2 + boxCenter.y
    for i in xrange(0, carrierSpringPairs):
        mountPoint = Math.Vector3((leftX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         length,
         indent,
         True,
         hardRatio))
        mountPoint = Math.Vector3((rightX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         length,
         indent,
         False,
         hardRatio))

    if _LOG_INIT_PARAMS:
        LOG_DEBUG('initVehiclePhysics: clearance %f' % (clearance / height))
        LOG_DEBUG('initVehiclePhysics: clearanceRatio %f' % (clearance / blen))
        LOG_DEBUG('initVehiclePhysics: cmShift %f' % cmShift)
        LOG_DEBUG('initVehiclePhysics: suspCompression: %f' % suspCompression)
    return


def computeBarrelLocalPoint(vehDescr, turretYaw, gunPitch):
    maxGunZ = vehDescr.gun.hitTester.bbox[1][2]
    m = Math.Matrix()
    m.setRotateX(gunPitch)
    pt = m.applyVector((0.0, 0.0, maxGunZ)) + vehDescr.turret.gunPosition
    m.setRotateY(turretYaw)
    pt = m.applyVector(pt)
    pt += vehDescr.hull.turretPositions[vehDescr.activeTurretPosition]
    pt += vehDescr.chassis.hullPosition
    return pt


def linearInterpolate(arg, argMin, argMax, valMin, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    valRange = valMax - valMin
    val = narg * valRange + valMin
    return val


def _computeCenterOfMassShift(mass, enginePower):
    dr = enginePower / mass
    cmy = _powerCurve(dr, DYN_RATIO_MIN, DYN_RATIO_MID, DYN_RATIO_MAX, CMY_MIN, CMY_MID, CMY_MAX)
    return cmy


def _computeSuspCompression(mass):
    suspCompression = linearInterpolate(mass, SUSP_COMPRESSION_MIN_MASS, SUSP_COMPRESSION_MAX_MASS, SUSP_COMPRESSION_MIN, SUSP_COMPRESSION_MAX)
    return suspCompression


def _computeTrackLength(clearance, length):
    r = clearance / length
    lenRatio = linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, TRACK_LENGTH_MAX, TRACK_LENGTH_MIN)
    return lenRatio * length


def _computeHardRatio(clearance, length):
    r = clearance / length
    return linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, HARD_RATIO_MIN, HARD_RATIO_MAX)


def _powerCurve(arg, argMin, argMid, argMax, valMin, valMid, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    nargMid = (argMid - argMin) / argRange
    valRange = valMax - valMin
    nvalMid = (valMid - valMin) / valRange
    pow = math.log(nvalMid, nargMid)
    nval = math.pow(narg, pow)
    val = nval * valRange + valMin
    return val


def _clamp(minBound, arg, maxBound):
    return max(minBound, min(maxBound, arg))


def initVehiclePhysicsFromParams(physics, params, xmlPath):

    class _SimpleObject(object):
        pass

    typeDesc = _SimpleObject()
    typeDesc.physics = {}
    typeDesc.physics['weight'] = params['weight']
    typeDesc.physics['enginePower'] = params['enginePower']
    typeDesc.physics['speedLimits'] = params['speedLimits']
    typeDesc.physics['rotationIsAroundCenter'] = params['rotationIsAroundCenter']
    typeDesc.physics['rotationSpeedLimit'] = params['rotationSpeedLimit']
    typeDesc.physics['terrainResistance'] = params['terrainResistance']
    typeDesc.physics['trackCenterOffset'] = params['trackCenterOffset']
    typeDesc.hull = vehicle_items.Hull()
    typeDesc.hull.hitTester = _SimpleObject()
    typeDesc.hull.hitTester.bbox = (params['hullHitTesterMin'], params['hullHitTesterMax'], None)
    typeDesc.hull.turretPositions = (params['turretPosition'],)
    typeDesc.turret = vehicle_items.createTurret(0, 0, 'Turret')
    typeDesc.turret.hitTester = _SimpleObject()
    typeDesc.turret.hitTester.bbox = (params['turretHitTesterMin'], params['turretHitTesterMax'], None)
    typeDesc.turret.gunPosition = params['gunPosition']
    typeDesc.type = _SimpleObject()
    typeDesc.type.name = ''
    section = ResMgr.openSection(xmlPath)
    try:
        typeDesc.type.xphysics = vehicles._readXPhysics((None, xmlPath), section, 'physics')
        chassisName = xphysics['detailed']['chassis'].keys()[0]
        engineName = xphysics['detailed']['engines'].keys()[0]
    except:
        typeDesc.type.xphysics = {'mode': 1}
        chassisName = 'Chassis'
        engineName = 'Engine'

    typeDesc.chassis = vehicle_items.createChassis(0, 0, chassisName)
    typeDesc.chassis.hullPosition = params['hullPosition']
    typeDesc.chassis.hitTester = _SimpleObject()
    typeDesc.chassis.hitTester.bbox = (params['chassisHitTesterMin'], params['chassisHitTesterMax'], None)
    typeDesc.engine = vehicle_items.createEngine(0, 0, engineName)
    typeDesc.shot = gun_components.GunShot(None, 1.0, (10.0, 10.0), 100.0, 9.8, 500.0, 1000000.0)
    typeDesc.gun = vehicle_items.createGun(0, 0, 'Gun')
    typeDesc.gun.staticTurretYaw = None
    typeDesc.hasSiegeMode = False
    typeDesc.isWheeledVehicle = False
    typeDesc.type.isRotationStill = False
    typeDesc.type.useHullZ = False
    typeDesc.type.hullAimingParams = {'pitch': {'isAvailable': False,
               'wheelCorrectionCenterZ': 0.0,
               'wheelsCorrectionSpeed': 0.2,
               'wheelsCorrectionAngles': {'pitchMax': 1.0,
                                          'pitchMin': 1.0}},
     'yaw': {'isAvailable': False}}
    initVehiclePhysicsEditor(physics, typeDesc)
    physics.visibilityMask = 4294967295L
    return


TRACK_SCROLL_LIMITS = (-15.0, 30.0)

def encodeTrackScrolling(leftScroll, rightScroll):
    return encodeRestrictedValueToUint(leftScroll, 8, *TRACK_SCROLL_LIMITS) | encodeRestrictedValueToUint(rightScroll, 8, *TRACK_SCROLL_LIMITS) << 8


def decodeTrackScrolling(code):
    return (decodeRestrictedValueFromUint((code & 255), 8, *TRACK_SCROLL_LIMITS), decodeRestrictedValueFromUint((code >> 8), 8, *TRACK_SCROLL_LIMITS))


def __deepUpdate(orig_dict, new_dict):
    if orig_dict is new_dict:
        return
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = __deepUpdate(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        orig_dict[key] = new_dict[key]

    return orig_dict


def __buildConfigurations(configuration):
    configurations = {'normal': copy.deepcopy(configuration)}
    modes = configuration.get('modes')
    if modes is not None:
        del configurations['normal']['modes']
        for key, value in modes.iteritems():
            basic = copy.deepcopy(configuration)
            modified = __deepUpdate(basic, value)
            configurations[key] = copy.deepcopy(modified)

    return {'vehiclePhysicsType': configuration['vehiclePhysicsType'],
     'modes': configurations}
