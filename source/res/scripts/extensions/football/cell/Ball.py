# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/Ball.py
import random
import weakref
import ArenaType
import BigWorld
import ResMgr
import Math, math
import PhysicsWorld
import ProjectileMover
import items.vehicles
import physics_shared
from PhysicalObject import PhysicalObject
from ModelHitTester import ModelHitTester
from constants import VEHICLE_HIT_EFFECT, SERVER_TICK_LENGTH, SHELL_TYPES
from debug_utils import *
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from physics_shared import NUM_SUBSTEPS
from wotdecorators import noexcept

def init():
    pass


_g_hardnessMap = {'ground': [0.02, 0.2],
 'stone': [0.02, 0.2],
 'wood': [0.02, 0.2],
 'metal': [0.01, 0.3],
 'snow': [0.02, 0.2],
 'sand': [0.02, 0.2]}
_EFFECT_ENERGY = 45.0
_MAX_COLLISION_ENERGY = 200.0
_STATIC_SCENE_FRICTION = 3.6
FOOTBALL_IMPULSE_POWER = 50
_SHOCKWAVE_MOMENTUM_SCALE_STRIKER = 3.0
_SHOCKWAVE_MOMENTUM_SCALE_MIDFIELD = 20.0
_SHOCKWAVE_MOMENTUM_SCALE_DEFENDER = 55.0
_MAX_SPEED_CAP_SPLASH_DAMAGE = 250.0
_Z_DAMPENING_ALL_SPLASH = 0.55
_Z_DAMPENING_FOR_SPLASH_CAP = 0.4
_STRIKER_SHELL_CALIBER = 105.0
_DEFENDER_SHELL_CALIBER = 200.0
_DAMAGE_2_CALIBER3_SCALE = 15.0
_DEFENDER_IMPULSE_MULTIPLIER = 1.9
_MIDFIELD_IMPULSE_MULTIPLIER = 1.3
_CONSTANT_GRAVITY_FACTOR = 1.6
_GRAVITY_THRESHOLD = 8.0
_THRESHOLD_GRAVITY_FACTOR = 3.0 / _CONSTANT_GRAVITY_FACTOR
BALL_COLLISION = 'content/MilitaryEnvironment/mle060_HimmelBall/collision/mle060_HimmelBall_04.model'
_FOOTBALL_CONFIG_SECTION = 'scripts/dynamic_objects.xml/footballBattle'
_BALL_TELEPORT_OFFSET = (0, 100, 0)
_MIX_HALFCONE_ANGLE = 30.0
_MIX_HALFCONE_MULTIPIER = 0.5
_MIX_BORDER_MULTIPIER = 0.2

class FOOTBALL:
    BALL_GROUND_FRICTION = 0.7
    FB_BALL_STOPPED_GROUND_ROT_FRICTION = 0.9
    FB_BALL_GROUND_ROT_FRICTION_SPEED_TRHESHOLD = 0.9
    FB_BALL_MOVING_GROUND_ROT_FRICTION = 0.9
    BALL_GROUND_ROLL_FRICTION = 0.35
    BALL_GROUND_STIFFNESS = 12.0
    BALL_GROUND_DAMP = 20.0
    BALL_AIR_ROT_FRICTION = 0.03
    BALL_AIR_ROLL_FRICTION = 0.01
    BALL_MAX_LINEAR_VELOCITY = Math.Vector3((55.0, 55.0, 55.0))
    BALL_MAX_ANGULAR_VELOCITY = Math.Vector3((45.0, 45.0, 45.0))
    BALL_VEHICLE_FRICTION = 1.3
    BALL_VEHICLE_ROT_FRICTION = 0.5
    BALL_VEHICLE_ROLL_FRICTION = 0.5
    BALL_VEHICLE_STIFFNESS = 30.0
    BALL_VEHICLE_DAMP = 3.0
    BALL_SHOT_IMPULSE = 329.3
    BALL_IMPULSE_FACTOR = 0.8
    BALL_MAX_IMPULSE = 5.0
    BALL_MASS = 6.8
    FB_BALL_FAST_RESTITUTION = True


def updateConf():
    simulationDT = SERVER_TICK_LENGTH / float(NUM_SUBSTEPS)
    stiff = FOOTBALL.BALL_GROUND_STIFFNESS * FOOTBALL.BALL_MASS
    damp = FOOTBALL.BALL_GROUND_DAMP * FOOTBALL.BALL_MASS
    cfm = 1.0 / (simulationDT * stiff + damp)
    rest = stiff * cfm
    BigWorld.wg_setupEventParam('FB_BALL_GROUND_FRICTION', FOOTBALL.BALL_GROUND_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_GROUND_ROLL_FRICTION', FOOTBALL.BALL_GROUND_ROLL_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_GROUND_CFM', cfm)
    BigWorld.wg_setupEventParam('FB_BALL_GROUND_RESTITUTION', rest)
    BigWorld.wg_setupEventParam('FB_BALL_AIR_ROT_FRICTION', FOOTBALL.BALL_AIR_ROT_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_AIR_ROLL_FRICTION', FOOTBALL.BALL_AIR_ROLL_FRICTION)
    stiff = FOOTBALL.BALL_VEHICLE_STIFFNESS * FOOTBALL.BALL_MASS
    damp = FOOTBALL.BALL_VEHICLE_DAMP * FOOTBALL.BALL_MASS
    cfm = 1.0 / (simulationDT * stiff + damp)
    rest = stiff * cfm
    impulseFactor = FOOTBALL.BALL_MASS * FOOTBALL.BALL_IMPULSE_FACTOR
    maxImpulse = FOOTBALL.BALL_MASS * FOOTBALL.BALL_MAX_IMPULSE
    BigWorld.wg_setupEventParam('FB_BALL_VEHICLE_FRICTION', FOOTBALL.BALL_VEHICLE_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_VEHICLE_ROT_FRICTION', FOOTBALL.BALL_VEHICLE_ROT_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_VEHICLE_ROLL_FRICTION', FOOTBALL.BALL_VEHICLE_ROLL_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_VEHICLE_CFM', cfm)
    BigWorld.wg_setupEventParam('FB_BALL_VEHICLE_RESTITUTION', rest)
    BigWorld.wg_setupEventParam('FB_BALL_IMPULSE_FACTOR', impulseFactor)
    BigWorld.wg_setupEventParam('FB_BALL_MAX_IMPULSE', maxImpulse)
    BigWorld.wg_setupEventParam('FB_BALL_FAST_RESTITUTION', FOOTBALL.FB_BALL_FAST_RESTITUTION)
    BigWorld.wg_setupEventParam('FB_BALL_STOPPED_GROUND_ROT_FRICTION', FOOTBALL.FB_BALL_STOPPED_GROUND_ROT_FRICTION)
    BigWorld.wg_setupEventParam('FB_BALL_GROUND_ROT_FRICTION_SPEED_TRHESHOLD', FOOTBALL.FB_BALL_GROUND_ROT_FRICTION_SPEED_TRHESHOLD)
    BigWorld.wg_setupEventParam('FB_BALL_MOVING_GROUND_ROT_FRICTION', FOOTBALL.FB_BALL_MOVING_GROUND_ROT_FRICTION)


class Ball(PhysicalObject):

    def __init__(self):
        updateConf()
        self.footballComponentMailbox = self.arena.components['ArenaFootballMechanics']
        self.cp = {}
        self.__hitTester = self.__readHitTester(BALL_COLLISION)
        self.direction = Math.Vector3(0, 0, 0)
        self.position = Math.Vector3(1, 10, 1)
        self.velocity = Math.Vector3(0, 0, 0)
        self.angularVelocity = Math.Vector3(0, 0, 0)
        self.isCollidingWithWorld = False
        self.lastAttackerID = 0
        self.assistID = 0
        physics = BigWorld.PyBall()
        bMin, bMax = self.__getBBox()
        radius = (bMax.x - bMin.x) / 2
        mass = FOOTBALL.BALL_MASS
        inertia = 2.0 / 3.0 * mass * radius * radius
        physics.gravity = physics_shared.G * physics_shared.GRAVITY_FACTOR
        physics.externalForce = Math.Vector3(0.0, 0.0, 0.0)
        physics.isFrozen = False
        physics.staticSceneFriction = _STATIC_SCENE_FRICTION
        self.boundingRadius = radius
        physics.setup(radius, mass, Math.Vector3(inertia, inertia, inertia))
        physics.matrix = self.__prepare_Body2World_matrix(self.position)
        physics.visibilityMask = ArenaType.getVisibilityMask(self.arenaTypeID >> 16)
        physics.owner = weakref.ref(self)
        physics.onRammingCb = self.__hitCallback
        physics.setMaxVelocity(FOOTBALL.BALL_MAX_LINEAR_VELOCITY, FOOTBALL.BALL_MAX_ANGULAR_VELOCITY)
        self.physics = physics
        PhysicsWorld.getWorld().addToCache(self)
        self.__ballExplosionDelay = 0.0
        self.__readConfig()
        self.energy = list()
        self.allowStaticEffect = True

    def __readConfig(self):
        dataSec = ResMgr.openSection(_FOOTBALL_CONFIG_SECTION)
        self.__ballExplosionDelay = dataSec.readFloat('ballExplosionDelay', 0.0)

    def waitAndExplodeBall(self):
        if self.__ballExplosionDelay > 0.0:
            BigWorld.addTimer(self.__explodeAndTeleportBall, self.__ballExplosionDelay)
        else:
            self.__explodeAndTeleportBall()

    def __explodeAndTeleportBall(self, timerID=None, _=0):
        self.allClients.explodeBall(self.position)
        self.teleportTo(self.position + _BALL_TELEPORT_OFFSET)
        self.freezeBall(True)

    def __getBBox(self):
        return self.__hitTester.bbox[:2]

    def getModel2WorldMatrix(self):
        m2b = Math.Matrix()
        m2b.setTranslate((0, 0, 0))
        m2b.postMultiply(self.physics.matrix)
        return m2b

    def __prepare_Model2World_matrix(self):
        y, p, r = self.direction[2], self.direction[1], self.direction[0]
        m2w = Math.Matrix()
        m2w.setRotateYPR((y, p, r))
        m2w.translation = self.position
        return m2w

    def __prepare_Body2World_matrix(self, com):
        b2m = Math.Matrix()
        b2m.setTranslate(com)
        m2w = self.__prepare_Model2World_matrix()
        b2m.postMultiply(m2w)
        return b2m

    def collideSegment(self, startPoint, endPoint):
        ballHitTester = self.__hitTester
        ballRes = ballHitTester.localHitTest(startPoint, endPoint)
        ballDist = min((e[0] for e in ballRes)) if ballRes else float('inf')
        dist = ballDist
        compIndex = 2
        return (dist, compIndex) if ballRes else (None, None)

    def __hitCallback(self, hitStr, *args):
        if hitStr == 'ballhit':
            self.__ballHit(args[0], bRammedBall=True)
        else:
            self.__onStaticCollision(args[0])

    def __onStaticCollision(self, energy):
        energy = min(0.5 * (energy - _EFFECT_ENERGY) + _EFFECT_ENERGY, _MAX_COLLISION_ENERGY)
        if energy >= _EFFECT_ENERGY:
            self.energy.append(energy)
        if len(self.energy) >= 2 and self.energy[-2] >= self.energy[-1]:
            if self.allowStaticEffect:
                self.allowStaticEffect = False
                self.allClients.playSoundOnCollision(int(self.energy[-2]))
        if energy < _EFFECT_ENERGY:
            if self.allowStaticEffect:
                if len(self.energy) != 0:
                    energy = max(self.energy)
                    self.allClients.playSoundOnCollision(int(energy))
            self.energy = list()
            self.allowStaticEffect = True

    def onDestroy(self):
        PhysicsWorld.getWorld().removeFromCache(self)

    def onLeavingCell(self):
        pass

    def onEnteredCell(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyBall()

    def onRestore(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyBall()

    def onDamageVehicle(self):
        pass

    def beforeSimulation(self):
        physics = self.physics
        physics.externalForce.set(0.0)
        originalGravity = physics.gravity
        if self.position[1] > _GRAVITY_THRESHOLD:
            physics.gravity = physics_shared.G * physics_shared.GRAVITY_FACTOR * _THRESHOLD_GRAVITY_FACTOR * _CONSTANT_GRAVITY_FACTOR
        else:
            physics.gravity = physics_shared.G * physics_shared.GRAVITY_FACTOR * _CONSTANT_GRAVITY_FACTOR

    def afterSimulation(self):
        self.__syncWithPhysics()
        footballSettings = ArenaType.g_cache[self.arenaTypeID].football
        curBallSide = self.__getBallSide(footballSettings.getFieldPosition)
        if 'ballSide' not in self.cp or curBallSide != self.cp['ballSide']:
            self.cp['ballSide'] = curBallSide
            self.footballComponentMailbox.receiveBallPositionUpdate(curBallSide)

    def sendGoalInfo(self, arenaMb, scoredTeam):
        pass

    def pushIfIdle(self):
        if self.lastAttackerID != 0:
            return
        xDir = 1 if bool(random.getrandbits(1)) else -1
        self.physics.applyImpulse(self.position, Math.Vector3(FOOTBALL_IMPULSE_POWER * xDir, 0, 0))

    def teleportTo(self, pos):
        physics = self.physics
        physics.velocity = Math.Vector3(0, 0, 0)
        physics.angVelocity = Math.Vector3(0, 0, 0)
        self.assistID = 0
        self.lastAttackerID = 0
        m = Math.Matrix(physics.matrix)
        m.translation = pos
        physics.matrix = m
        self.__syncWithPhysics()

    def freezeBall(self, isFrozen):
        self.physics.isFrozen = isFrozen

    @noexcept
    def receiveShot(self, attackerInfo, shotID, shellCompactDescr, hitPoint, hitDirection, shellVelocity):
        shellDescr = items.vehicles.getItemByCompactDescr(shellCompactDescr)
        m = self.getModel2WorldMatrix()
        worldHitPoint = m.applyPoint(hitPoint)
        attackerID = 0 if attackerInfo['noOwner'] else attackerInfo['baseMB'].id
        self.__ballHit(attackerID)
        physics = self.physics
        shellCaliber = shellDescr.caliber
        if shellCaliber >= _DEFENDER_SHELL_CALIBER:
            impulsePower = FOOTBALL.BALL_SHOT_IMPULSE * _DEFENDER_IMPULSE_MULTIPLIER
        elif shellCaliber > _STRIKER_SHELL_CALIBER:
            impulsePower = FOOTBALL.BALL_SHOT_IMPULSE * _MIDFIELD_IMPULSE_MULTIPLIER
        else:
            impulsePower = FOOTBALL.BALL_SHOT_IMPULSE
        impulseDirection = self.position - worldHitPoint
        impulseDirection.normalise()
        trajectoryDirection = m.applyVector(hitDirection)
        trajectoryDirection.normalise()
        cosine = max(0.0, trajectoryDirection.dot(impulseDirection))
        if cosine <= math.cos(_MIX_HALFCONE_ANGLE):
            physics.applyImpulse(worldHitPoint, impulseDirection * impulsePower)
        else:
            mixer = _MIX_HALFCONE_MULTIPIER - (math.degrees(math.acos(cosine)) - _MIX_HALFCONE_ANGLE) / (90.0 - _MIX_HALFCONE_ANGLE) * _MIX_BORDER_MULTIPIER
            physics.applyImpulse(worldHitPoint, mixer * impulseDirection * impulsePower)
            physics.applyImpulse(self.position, (1 - mixer) * trajectoryDirection * impulsePower)
        numVehiclesAffected = 0
        if shellDescr.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
            armorDamage, deviceDamage = ProjectileMover.getRandomizedShellDamage(shellDescr)
            damagedDestrs, numVehiclesAffected = ProjectileMover.damageAreaByExplosion(worldHitPoint, shellDescr.type.explosionRadius, armorDamage, deviceDamage, shellDescr.effectsIndex, attackerInfo, shotID, shellCompactDescr, self, True, False)
        if not attackerInfo['noOwner']:
            ProjectileMover.onMiss(attackerInfo['baseMB'], shotID, numVehiclesAffected)
        team = attackerInfo['team']
        self.allClients.showDamageFromShot(attackerID, hitPoint, team)

    @noexcept
    def receiveExplosion(self, hitPoint, damageRadius, armorDamage, shotEffectsIndex, shellCompactDescr, attackerID):
        shellDescr = items.vehicles.getItemByCompactDescr(shellCompactDescr)
        position = self.position
        dR = position - hitPoint
        dir_ = dR
        dir_.normalise()
        exposedArea = self.physics.getProjectionArea(dir_)
        caliber = 0.001 * _DAMAGE_2_CALIBER3_SCALE * armorDamage ** (1.0 / 3)
        distRescaled = max(1.2, dR.length / caliber)
        momentumMagnitude = exposedArea / distRescaled
        shellCaliber = shellDescr.caliber
        if shellCaliber <= _STRIKER_SHELL_CALIBER:
            dist = position - hitPoint
            momentumMagnitude *= _SHOCKWAVE_MOMENTUM_SCALE_STRIKER
        elif shellCaliber > _STRIKER_SHELL_CALIBER and shellCaliber < _DEFENDER_SHELL_CALIBER:
            dist = position - hitPoint
            momentumMagnitude *= _SHOCKWAVE_MOMENTUM_SCALE_MIDFIELD
        elif shellCaliber >= _DEFENDER_SHELL_CALIBER:
            dist = position - hitPoint
            momentumMagnitude *= _SHOCKWAVE_MOMENTUM_SCALE_DEFENDER
        momentum = dir_ * momentumMagnitude * (1 + dist.length / damageRadius)
        physics = self.physics
        if momentum.length > _MAX_SPEED_CAP_SPLASH_DAMAGE * dir_.length:
            physics.velocity = Math.Vector3(0, 0, 0)
            self.velocity = Math.Vector3(0, 0, 0)
            physics.angVelocity = Math.Vector3(0, 0, 0)
            self.angularVelocity = Math.Vector3(0, 0, 0)
            momentum = _MAX_SPEED_CAP_SPLASH_DAMAGE * dir_
            momentum[1] = momentum[1] * _Z_DAMPENING_FOR_SPLASH_CAP
        else:
            momentum[1] = momentum[1] * _Z_DAMPENING_ALL_SPLASH
        self.physics.applyImpulse(position, momentum)
        self.__ballHit(attackerID, bSplash=True)

    def applyForceToCOM(self, force):
        self.physics.externalForce += force

    def __syncWithPhysics(self):
        p = self.physics
        m = self.getModel2WorldMatrix()
        self.position = Math.Vector3(m.translation)
        self.direction = Math.Vector3(m.roll, m.pitch, m.yaw)
        self.velocity = Math.Vector3(p.velocity)
        self.angularVelocity = Math.Vector3(p.angVelocity)

    def __ballHit(self, attackerID, bRammedBall=False, bSplash=False):
        if attackerID != self.lastAttackerID:
            self.assistID = self.lastAttackerID
            self.lastAttackerID = attackerID
        speed = 0
        velocityDir = Math.Vector3()
        if bRammedBall:
            v = BigWorld.entities.get(attackerID)
            vehMoverPhysics = v.mover.physics
            velocityDir = Math.Vector3(vehMoverPhysics.velocity)
            speed = velocityDir.length
            velocityDir.normalise()
        self.footballComponentMailbox.updateGameplayIDs(self.lastAttackerID, self.assistID, bRammedBall, bSplash, speed, velocityDir)

    def onCollisionWithVehicle(self, otherID, selfPt, otherPt, normal, impulse, kineticEnergy, stress, selfSpeed, otherSpeed):
        energy = max(0, min(kineticEnergy, _MAX_COLLISION_ENERGY))
        if energy >= _EFFECT_ENERGY:
            self.allClients.playSoundOnCollision(int(energy))
            vehicle = BigWorld.entities.get(otherID, None)
            if vehicle is not None:
                vehiclePosition = vehicle.mover.matrix.translation
                directionToVehicle = vehiclePosition - self.position
                directionToVehicle.normalise()
                self.allClients.showRam(directionToVehicle.scale(self.boundingRadius) + self.position)
        return

    def __getBallSide(self, fieldPos):
        fieldX = fieldPos[0]
        x = self.position[0]
        if abs(x - fieldX) < 0.1:
            return 0
        return 1 if x < fieldX else 2

    def __readHitTester(self, bspModelName):
        try:
            hitTester = ModelHitTester()
            hitTester.bspModelName = bspModelName
            hitTester.loadBspModel()
            return hitTester
        except Exception as x:
            LOG_CURRENT_EXCEPTION()
