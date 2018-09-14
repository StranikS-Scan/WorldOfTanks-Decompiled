# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/benchmark.py
import functools
import math
import BigWorld
from Math import Vector3
import Math
from Math import Matrix
from items import vehicles
from AvatarInputHandler import mathUtils
import Pixie
import DataLinks
import VehicleUtils
from vehicle_systems import model_assembler as assemblerModule
from vehicle_systems.tankStructure import ModelStates
reload(assemblerModule)
from vehicle_systems.model_assembler import prepareCompoundAssembler

def analyzeRefs(obj):
    import gc
    refs = gc.get_referrers(obj)
    print refs
    import objgraph
    import time
    objgraph.show_backrefs(obj, filename='Refs' + str(time.time()) + '.png', extra_ignore=[id(refs), id(objgraph)], refcounts=True, max_depth=15)


def simpleLoad():
    import CurrentVehicle
    a = assemblerModule.prepareCompoundAssembler(CurrentVehicle.g_currentVehicle.item.descriptor, 'undamaged', BigWorld.camera().spaceID)
    a.assemblerName = 'a'

    def f(r):
        global tanks
        tanks.append(r['a'])

    BigWorld.loadResourceListBG([a], f)


def getModelNames(vehicleDesc):
    parts = (vehicleDesc.chassis,
     vehicleDesc.hull,
     vehicleDesc.turret,
     vehicleDesc.gun)
    return [ x['models']['undamaged'] for x in parts ]


def assemblePyModels(models, position, vehicleDesc):
    chassis = BigWorld.Model(models[0])
    hull = BigWorld.Model(models[1])
    turret = BigWorld.Model(models[2])
    gun = BigWorld.Model(models[3])
    chassis.node('V').attach(hull)
    hull.node('HP_turretJoint').attach(turret)
    turret.node('HP_gunJoint').attach(gun)
    BigWorld.addModel(chassis)
    chassis.position = position
    return chassis


def assembleCompoundModel(models, position, vehicleDesc):
    tank = BigWorld.createCompoundTank()
    chassis = BigWorld.ModelLite(models[0])
    hull = BigWorld.ModelLite(models[1])
    turret = BigWorld.ModelLite(models[2])
    gun = BigWorld.ModelLite(models[3])
    matrix = Matrix()
    matrix.translation = position
    tank.attachPart(0, chassis, '', matrix)
    tank.attachPart(1, hull, 'V')
    tank.attachPart(2, turret, 'HP_turretJoint')
    tank.attachPart(3, gun, 'HP_gunJoint')
    BigWorld.addModel(tank)
    return tank


fashions = []
fakeMatrixes = []
tanks = []

def setupTank(chassisFashion, gunFashion, vehicleDesc, worldMatrix, resources):
    print resources
    tank = resources[vehicleDesc.name]
    tank.matrix = worldMatrix
    tanks.append(tank)
    effect = Pixie.create('particles/Tank/exhaust/large_gas_gear.xml')
    tank.node('HP_gunFire').attach(effect)
    tank.node('HP_gunFire').attach(BigWorld.Model('helpers/models/position_gizmo.model'))
    tank.node('HP_Track_Exhaus_1').attach(BigWorld.Model('helpers/models/unit_cube.model'))
    m = mathUtils.createTranslationMatrix(Vector3(0, 10, 5))
    fakeMatrixes.append(m)
    tank.node('gun').attach(effect.clone(), m)
    BigWorld.addModel(tank)
    recoilDescr = vehicleDesc.gun['recoil']
    recoil = BigWorld.RecoilAnimator(recoilDescr['backoffTime'], recoilDescr['returnTime'], recoilDescr['amplitude'], recoilDescr['lodDist'])
    recoil.basisMatrix = tank.node('G').localMatrix
    recoil = assemblerModule.createGunAnimator(vehicleDesc, tank.node('G').localMatrix)
    recoil.lodSetting = 10
    tank.node('G', recoil)
    gunFashion.gunLocalMatrix = recoil
    recoil.lodLink = DataLinks.createFloatLink(chassisFashion, 'lastLod')
    swingingAnimator = assemblerModule.createSwingingAnimator(vehicleDesc, tank.node('hull').localMatrix, worldMatrix)
    chassisFashion.setupSwinging(swingingAnimator, 'hull')
    swingingAnimator.lodLink = DataLinks.createFloatLink(chassisFashion, 'lastLod')
    tank.setupFashions([chassisFashion,
     None,
     None,
     gunFashion])
    fashions.append(swingingAnimator)
    tank.node('hull', swingingAnimator)
    animMatrix = Math.MatrixAnimation()
    keys = []
    for x in xrange(100):
        angle = math.pi * 0.5 * (1 if x & 1 else -1)
        keys.append((x * 3, mathUtils.createRotationMatrix((angle, 0, 0))))

    animMatrix.keyframes = tuple(keys)
    tank.node('turret', animMatrix)
    return


def assembleCompoundModel2(models, position, vehicleDesc):
    worldMatrix = mathUtils.createTranslationMatrix(position)
    chassisFashion = BigWorld.WGVehicleFashion()
    VehicleUtils.setupTracksFashion(chassisFashion, vehicleDesc)
    fashions.append(chassisFashion)
    gunFashion = BigWorld.WGGunRecoil('G')
    fashions.append(gunFashion)
    assembler = prepareCompoundAssembler(vehicleDesc, ModelStates.UNDAMAGED, BigWorld.camera().spaceID if BigWorld.player().spaceID == 0 else BigWorld.player().spaceID)
    BigWorld.loadResourceListBG((assembler,), functools.partial(setupTank, chassisFashion, gunFashion, vehicleDesc, worldMatrix))


TANK_NAMES = ['ussr:R04_T-34', 'ussr:R73_KV4']
EXAMPLE_COUNT = 1

def exhibit(tankNames=None, pivotPoint=None, shift=Vector3(0, 0, 10), assembler=assembleCompoundModel2):
    if pivotPoint is None:
        p = Vector3(BigWorld.camera().position)
        d = BigWorld.camera().direction
        spaceID = BigWorld.player().spaceID if BigWorld.player() is not None else BigWorld.camera().spaceID
        collRes = BigWorld.wg_collideSegment(spaceID, p, p + d * 1000, 18, 8)
        if collRes is None:
            pivotPoint = Vector3(0, 0, 0)
        else:
            strikePos = collRes[0]
            pivotPoint = strikePos
    if tankNames is None:
        tankNames = [ vehicles.g_cache.vehicle(0, x).name for x in xrange(EXAMPLE_COUNT) ]
    totalTanks = len(tankNames)
    shift_new = Vector3(d)
    shift_new.y = 0.0
    up = Vector3(0.0, 1.0, 0.0)
    right = up * shift_new
    shift_new.normalise()
    right.normalise()
    offset = 6.0
    shift_new = shift_new * offset
    right = right * offset
    for idx, tankName in enumerate(tankNames):
        desc = vehicles.VehicleDescr(typeName=tankName)
        if idx < totalTanks / 2:
            creationPosition = pivotPoint + shift_new * idx
        else:
            creationPosition = pivotPoint + shift_new * (idx - totalTanks / 2) + right
        assembler(getModelNames(desc), creationPosition, desc)

    return


def clear():
    global tanks
    for t in tanks:
        BigWorld.delModel(t)

    tanks = []
