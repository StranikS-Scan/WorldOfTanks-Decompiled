# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/projectiles.py
"""This module handles different projectiles."""
import BigWorld
import PSFX
import particles
import Pixie
import math
from functools import partial
from Math import Vector3
from Keys import *
from Math import MatrixProduct
from Math import Matrix
import FX

def preload(list):
    list += ['objects/models/fx/03_pchangs/shockwave.model']


def calculateTripTime(sourcePosition, targetPosition, speed):
    disp = sourcePosition - targetPosition
    sx = math.sqrt(disp.x * disp.x + disp.z * disp.z)
    sy = disp.y
    ay = -9.8
    U = speed
    intercept = U * U * U * U - 2 * U * U * sy * ay - ay * ay * sx * sx
    if intercept < 0:
        return 0
    tsq = 2.0 / (ay * ay) * (sy * ay - U * U + math.sqrt(intercept))
    t = math.sqrt(abs(tsq))
    return t


def create(name, owner, target, projectile, colour=(1.0, 1.0, 1.0), location=None):
    if fxMap.has_key(name):
        trail, explosion, project, tracer = fxMap[name]
        if project:
            shootProjectile(owner, target, projectile, trail, partial(explosion, owner, True))
        elif explosion:
            if target:
                explosion(owner, target.model, 0)
            else:
                m = BigWorld.Model('')
                owner.addModel(m)
                m.position = location
                explosion(owner, m, 1)


projectileSpeed = 12.0

def destroyFireball(owner, fireball, fx, explosionFXName, targetHitCallback, prereqs):
    m = Matrix(fireball.motors[0].target)
    fx.detach()
    owner.delModel(fireball)
    explosion = BigWorld.Model('')
    owner.addModel(explosion)
    explosion.position = m.applyToOrigin()
    fireballfx = FX.bufferedOneShotEffect(explosionFXName, explosion, explosion, lambda : owner.delModel(explosion), 10.0, prereqs)
    if targetHitCallback != None:
        targetHitCallback(owner, m)
    return


def fireballTripTime(source, target, srcoff=Vector3(0, 1.5, 0), dstoff=Vector3(0, 1.2, 0)):
    global projectileSpeed
    if hasattr(target, 'matrix'):
        targetMatrix = target.matrix
    else:
        targetMatrix = target
    sourcePosition = Vector3(source.position) + srcoff
    targetPosition = Vector3(Matrix(targetMatrix).applyToOrigin()) + dstoff
    speed = projectileSpeed
    tripTime = calculateTripTime(sourcePosition, targetPosition, speed)
    if tripTime == 0:
        speed = speed * 2.0
        tripTime = calculateTripTime(sourcePosition, targetPosition, speed)
    if tripTime == 0:
        speed = speed * 2.0
        tripTime = calculateTripTime(sourcePosition, targetPosition, speed)
    if tripTime == 0:
        speed = speed * 2.0
        tripTime = calculateTripTime(sourcePosition, targetPosition, speed)
    if tripTime == 0:
        speed = speed * 2.0
        tripTime = calculateTripTime(sourcePosition, targetPosition, speed)
    if tripTime == 0:
        print 'No speed solution for fireball'
        return 0
    return tripTime


def createFireball(projectileFXName, explosionFXName, source, target, srcOffset=None, targetHitCallback=None, prereqs=None):
    global projectileSpeed
    fireball = BigWorld.Model('')
    fx = FX.Persistent(projectileFXName, prereqs)
    fx.attach(fireball)
    callback = partial(destroyFireball, source, fireball, fx, explosionFXName, targetHitCallback, prereqs)
    tripTime = shootProjectile(source, target, fireball, None, callback, srcOffset)
    if tripTime == 0:
        projectileSpeed = projectileSpeed * 2.0
        tripTime = shootProjectile(source, target, fireball, None, callback, srcOffset)
    if tripTime == 0:
        projectileSpeed = projectileSpeed * 2.0
        tripTime = shootProjectile(source, target, fireball, None, callback, srcOffset)
    if tripTime == 0:
        projectileSpeed = projectileSpeed * 2.0
        tripTime = shootProjectile(source, target, fireball, None, callback, srcOffset)
    if tripTime == 0:
        projectileSpeed = projectileSpeed * 2.0
        tripTime = shootProjectile(source, target, fireball, None, callback, srcOffset)
    if tripTime == 0:
        fx.detach(fireball)
        print 'No speed solution for fireball'
    projectileSpeed = 12.0
    return tripTime


def shootProjectile(owner, target, projectile, trail=None, boom=None, srcoff=Vector3(0, 1.5, 0), dstoff=Vector3(0, 1.2, 0), motor=None):
    if hasattr(target, 'matrix'):
        targetMatrix = target.matrix
    else:
        targetMatrix = target
    if not boom and dstoff:
        dstoff.y = 1.8
    if not dstoff:
        dstoff = Vector3(0, 0, 0)
    owner.addModel(projectile)
    projectile.position = Vector3(owner.position) + srcoff
    if not motor:
        motor = BigWorld.Homer()
        motor.speed = projectileSpeed
        motor.turnRate = 10
    if dstoff.lengthSquared == 0:
        motor.target = targetMatrix
    else:
        motor.target = MatrixProduct()
        motor.target.a = targetMatrix
        motor.target.b = Matrix()
        motor.target.b.setTranslate(dstoff)
    if motor.tripTime <= 0.0:
        sourcePosition = Vector3(owner.position) + srcoff
        targetPosition = Vector3(Matrix(targetMatrix).applyToOrigin()) + dstoff
        speed = motor.speed
        t = calculateTripTime(sourcePosition, targetPosition, speed)
        if t == 0:
            owner.delModel(projectile)
            return 0
        motor.tripTime = t
    projectile.addMotor(motor)
    if trail:
        trail(projectile, None, motor.tripTime)
    motor.proximity = 1.0
    if boom:
        motor.proximityCallback = boom
    else:
        motor.proximityCallback = partial(owner.delModel, projectile)
    return motor.tripTime


def standardTrail(projectile, node, tripTime):
    PSFX.attachFlareTrace(projectile, node, tripTime)


def smokeTrail(projectile, node, tripTime):
    PSFX.attachFlareTrace(projectile, node, tripTime)
    PSFX.attachSmokeTrail(projectile, node)


def standardExplosion(owner, model, delModel):
    PSFX.attachExplosion(model)
    if delModel:
        BigWorld.callback(0.5, partial(owner.delModel, model))


def empExplosion(owner, model, delModel):
    PSFX.attachExplosion(model)
    if delModel:
        BigWorld.callback(0.5, partial(owner.delModel, model))


def shake(targetModel):
    dist = Vector3(targetModel.position - BigWorld.player().position).length
    if dist < 100:
        BigWorld.player()
        try:
            BigWorld.rumble(100 - dist, 0)
            BigWorld.callback(0.1, partial(BigWorld.rumble, 0, 0))
        except:
            pass

        shDist = 0.25 - dist / 250
        try:
            BigWorld.camera().shake(0.1, (shDist, shDist, shDist / 2))
        except:
            pass


def plasmaImplode(duration, targetModel):
    warpEffect = PSFX.beginPlasmaWarp(targetModel)
    BigWorld.callback(duration, partial(PSFX.endPlasmaWarp, warpEffect))


def plasmaExplode(owner, targetModel, delTargetModel):
    m = BigWorld.Model('objects/models/fx/03_pchangs/shockwave.model')
    targetModel.root.attach(m)
    m.Go()
    BigWorld.callback(1.0, partial(targetModel.root.detach, m))
    m = targetModel.root
    m2 = Matrix()
    m2.setScale((5, 5, 5))
    m2.postMultiply(m)
    v1 = Vector4(1.0, 100000, 0, 0)
    v2 = Vector4(0.0, 0, 0, 0)
    v = Vector4Animation()
    v.keyframes = [(0, v1), (0.5, v2)]
    v.duration = 1
    v.time = 0
    try:
        BigWorld.addWarp(0.5, m2, v)
    except:
        pass

    shake(targetModel)
    ps2 = Pixie.create('particles/plasma_blow.xml')
    targetModel.root.attach(ps2)
    ps2.system(0).actions[0].force(1)
    BigWorld.callback(5.0, partial(targetModel.root.detach, ps2))
    if delTargetModel:
        BigWorld.callback(5.0, partial(owner.delModel, targetModel))
    if BigWorld.player().flashBangCount == 0:
        fba = Vector4Animation()
        fba.keyframes = [(0, Vector4(0, 0, 0, 0)), (0.1, Vector4(0.1, 0.1, 0.2, 0.5)), (0.3, Vector4(0, 0, 0, 0))]
        fba.duration = 0.3
        try:
            BigWorld.flashBangAnimation(fba)
        except:
            pass

        BigWorld.callback(fba.duration, partial(BigWorld.flashBangAnimation, None))
    return


def plasmaExplosion(owner, targetModel, delModel):
    plasmaImplode(1.0, targetModel)
    BigWorld.callback(1.5, partial(plasmaExplode, owner, targetModel, delModel))


fxMap = {'cannon': (smokeTrail,
            standardExplosion,
            1,
            1),
 'cannon_he': (smokeTrail,
               standardExplosion,
               1,
               1),
 'cannon_emp': (smokeTrail,
                empExplosion,
                1,
                1),
 'cannon_plasma': (standardTrail,
                   plasmaExplosion,
                   0,
                   0),
 'throw': (standardTrail,
           None,
           1,
           1)}
