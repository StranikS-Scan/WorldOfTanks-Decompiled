# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/PSFX.py
# Compiled at: 2010-05-25 20:46:16
"""This module acts as a bank for particle system effects. All effects from
this module are temporary effects that dissipate over time."""
import BigWorld
import Pixie
import particles
from Keys import *
from functools import partial
sparksList = None
bloodSprayList = None
respawnMistList = None
smokeTrailList = None
explosionList = None
arrowTraceList = None
flareTraceList = None
pchangSparkList = None
worldExplosionList = None
pchangChunkSystem = None
pchangChunkModel = None
dustStorm = None
dustStormChunks = None
dustStormFog = None
SOURCE_PSA = 1
SINK_PSA = 2
BARRIER_PSA = 3
FORCE_PSA = 4
STREAM_PSA = 5
JITTER_PSA = 6
SCALER_PSA = 7
TINT_SHADER_PSA = 8
NODE_CLAMP_PSA = 9
ORBITOR_PSA = 10
FLARE_PSA = 11

def detachEffect(model, system, store, nodeName=None):
    if nodeName:
        model.node(nodeName).detach(system)
    else:
        model.root.detach(system)
    system.clear()
    store.append(system)


def attachSparks(model, nodeName=None, numberOfSparks=1):
    global sparksList
    if sparksList == None:
        sparksList = generateSparksList(10)
    if len(sparksList) >= 1:
        sparks = sparksList.pop()
        if nodeName != None:
            model.node(nodeName).attach(sparks)
        else:
            model.root.attach(sparks)
        sparks.action(SOURCE_PSA).force(numberOfSparks)
        BigWorld.callback(sparks.action(SINK_PSA).maximumAge + 1.0, partial(detachEffect, model, sparks, sparksList, nodeName))
    return


def generateSparksList(numberOfPS):
    psList = []
    i = 0
    while 1:
        if i < numberOfPS:
            sparks = particles.createSparks()
            sparks != None and psList.append(sparks)
        i = i + 1

    return psList


def attachBloodSpray(model, direction=0, numberOfSprays=1):
    global bloodSprayList
    if bloodSprayList == None:
        bloodSprayList = generateBloodSprayList(10)
    if len(bloodSprayList) >= 1:
        bloodSpray = bloodSprayList.pop()
        model.root.attach(bloodSpray)
        src = bloodSpray.action(SOURCE_PSA)
        height = model.height * 0.8
        src.setPositionSource(['Point', (0.0, height, 0.0)])
        if direction == 0:
            src.setVelocitySource(['Sphere',
             (0.0, 4.0, 0.0),
             1.5,
             0.5])
        elif direction == 1:
            src.setVelocitySource(['Sphere',
             (-4.0, 0.0, 0.0),
             1.5,
             0.5])
        elif direction == 2:
            src.setVelocitySource(['Sphere',
             (4.0, 0.0, 0.0),
             1.5,
             0.5])
        src.force(numberOfSprays)
        BigWorld.callback(bloodSpray.action(SINK_PSA).maximumAge + 1.0, partial(detachEffect, model, bloodSpray, bloodSprayList))
    return


def generateBloodSprayList(numberOfPS):
    psList = []
    i = 0
    while 1:
        if i < numberOfPS:
            blood = particles.createBloodSpray()
            blood != None and psList.append(blood)
        i = i + 1

    return psList


def attachRespawnMist(model, density=100):
    global respawnMistList
    if respawnMistList == None:
        respawnMistList = generateRespawnMistList(10)
    if len(respawnMistList) >= 1:
        mist = respawnMistList.pop()
        model.root.attach(mist)
        BigWorld.callback(0.01, partial(mist.system(0).action(SOURCE_PSA).force, density))
        BigWorld.callback(mist.system(0).action(SINK_PSA).maximumAge + 1.0, partial(detachEffect, model, mist, respawnMistList))
    return


def generateRespawnMistList(numberOfPS):
    psList = []
    i = 0
    while 1:
        mist = i < numberOfPS and particles.createRespawnMist()
        psList.append(mist)
        i = i + 1

    return psList


def attachArrowTrace(model, nodeName=None, flightTime=1.0):
    global arrowTraceList
    if arrowTraceList == None:
        arrowTraceList = generateArrowTraceList(10)
    if len(arrowTraceList) >= 1:
        trace = arrowTraceList.pop()
        if nodeName != None:
            model.node(nodeName).attach(trace)
        else:
            model.root.attach(trace)
        trace.action(SOURCE_PSA).motionTriggered = True
        BigWorld.callback(flightTime + 1.0, partial(detachEffect, model, trace, arrowTraceList, nodeName))
    return


def generateArrowTraceList(numberOfPS):
    psList = []
    i = 0
    while 1:
        trace = i < numberOfPS and particles.createArrowTrace()
        psList.append(trace)
        i = i + 1

    return psList


def attachFlareTrace(model, nodeName=None, flightTime=1.0):
    global flareTraceList
    if flareTraceList == None:
        flareTraceList = generateFlareTraceList(10)
    if len(flareTraceList) >= 1:
        trace = flareTraceList.pop()
        if nodeName != None:
            model.node(nodeName).attach(trace)
        else:
            model.root.attach(trace)
        trace.action(SOURCE_PSA).motionTriggered = True
        trace.renderer.blurred = True
        BigWorld.callback(flightTime + 1.0, partial(detachEffect, model, trace, flareTraceList, nodeName))
    return


def generateFlareTraceList(numberOfPS):
    psList = []
    i = 0
    while 1:
        if i < numberOfPS:
            trace = particles.createFlareTrace()
            trace != None and psList.append(trace)
        i = i + 1

    return psList


def attachSmokeTrail(model, nodeName=None):
    global smokeTrailList
    if smokeTrailList == None:
        smokeTrailList = generateSmokeTrailList(10)
    if len(smokeTrailList) >= 1:
        trail = smokeTrailList.pop()
        if nodeName:
            model.node(nodeName).attach(trail)
        else:
            model.root.attach(trail)
        BigWorld.callback(trail.action(SINK_PSA).maximumAge + 1.0, partial(detachEffect, model, trail, smokeTrailList, nodeName))
    return


def generateSmokeTrailList(numberOfPS):
    psList = []
    i = 0
    while 1:
        mist = i < numberOfPS and particles.createSmokeTrail()
        psList.append(mist)
        i = i + 1

    return psList


def attachExplosion(model, nodeName=None, numberOfSparks=25):
    global explosionList
    if explosionList == None:
        explosionList = generateExplosionList(10)
    if len(explosionList) >= 1:
        explosion = explosionList.pop()
        if nodeName != None:
            model.node(nodeName).attach(explosion)
        else:
            model.root.attach(explosion)
        explosion.action(SOURCE_PSA).force(numberOfSparks)
        BigWorld.callback(explosion.action(SINK_PSA).maximumAge + 1.0, partial(detachEffect, model, explosion, explosionList, nodeName))
    return


def generateExplosionList(numberOfPS):
    psList = []
    i = 0
    while 1:
        if i < numberOfPS:
            explosion = particles.createSparkExplosion()
            explosion != None and psList.append(explosion)
        i = i + 1

    return psList


def attachPchangSparks(model, worldDir, worldPos, triangleFlags, number):
    global pchangSparkList
    if pchangSparkList == None:
        pchangSparkList = generatePchangSparkList(10)
    if len(pchangSparkList) >= 1:
        explosion = pchangSparkList.pop()
        model.root.attach(explosion)
        explosion.explicitPosition = worldPos
        explosion.explicitDirection = worldDir
        explosion.action(SOURCE_PSA).force(number)
        BigWorld.callback(explosion.action(SINK_PSA).maximumAge + 0.1, partial(detachEffect, model, explosion, pchangSparkList))
    return


def generatePchangSparkList(numberOfPS):
    psList = []
    i = 0
    while 1:
        if i < numberOfPS:
            pchang = particles.createPchangSparks()
            pchang != None and psList.append(pchang)
        i = i + 1

    return psList


def detachPchangChunks(model):
    global pchangChunkSystem
    global pchangChunkModel
    if model == pchangChunkModel:
        pchangChunkModel.root.detach(pchangChunkSystem)
        pchangChunkModel = None
    return


def attachPchangChunks(model, worldDir, worldPos, triangleFlags, number):
    global pchangChunkSystem
    global pchangChunkModel
    if pchangChunkSystem == None:
        pchangChunkSystem = particles.createDirectedChunks()
        pchangChunkModel = None
    if pchangChunkModel:
        pchangChunkModel.root.detach(pchangChunkSystem)
    pchangChunkModel = model
    if pchangChunkSystem != None:
        model.root.attach(pchangChunkSystem)
        pchangChunkSystem.explicitDirection = worldDir
        pchangChunkSystem.explicitPosition = worldPos
        pchangChunkSystem.action(SOURCE_PSA).force(number)
        BigWorld.callback(pchangChunkSystem.action(SINK_PSA).maximumAge + 0.1, partial(detachPchangChunks, model))
    return


def worldExplosion(model, worldDir, worldPos, triangleFlags, number):
    global worldExplosionList
    if worldExplosionList == None:
        worldExplosionList = generateWorldExplosionList(10)
    if len(worldExplosionList) >= 1:
        explosion = worldExplosionList.pop()
        model.root.attach(explosion)
        time = 0.0
        for i in xrange(0, explosion.nSystems()):
            system = explosion.system(i)
            system.explicitPosition = worldPos
            system.explicitDirection = worldDir
            system.action(SOURCE_PSA).force(number)
            sink = system.action(SINK_PSA)
            time = max(time, sink.maximumAge + 0.1)

        BigWorld.callback(time, partial(detachEffect, model, explosion, worldExplosionList))
    return


def generateWorldExplosionList(numberOfPS):
    psList = []
    i = 0
    while 1:
        explosion = i < numberOfPS and particles.createDirectedSparks()
        psList.append(explosion)
        i = i + 1

    return psList


def beginDustStorm():
    global dustStormFog
    global dustStorm
    global dustStormChunks
    if not dustStorm:
        dustStorm = particles.createDustStorm()
        dustStormChunks = particles.createDustStormChunks()
    pos = BigWorld.player().position
    BigWorld.player().model.root.attach(dustStorm)
    BigWorld.player().model.root.attach(dustStormChunks)
    dustStormFog = BigWorld.addFogEmitter((0, 0, 0), 4, 0, 100, 4286586912L, 0)


def endDustStorm():
    BigWorld.player().model.root.detach(dustStorm)
    BigWorld.player().model.root.detach(dustStormChunks)
    BigWorld.delFogEmitter(dustStormFog)


warpEffects = []

def beginPlasmaWarp(target):
    global warpEffects
    allFinished = 1
    for finished, i, s, t in warpEffects:
        if not finished:
            allFinished = 0

    if allFinished:
        warpEffects = []
    ps = Pixie.create('particles/plasma_suck.xml')
    try:
        target.node('biped Head').attach(ps)
    except:
        target.root.attach(ps)

    m = target.root
    m2 = Matrix()
    m2.setScale((1, 1, 1))
    m2.postMultiply(m)
    v1 = Vector4(3.0, -100000, 0, 0)
    v2 = Vector4(0.0, 0, 0, 0)
    v = Vector4Animation()
    v.keyframes = [(0, v2), (3, v1)]
    v.duration = 1000000
    v.time = 0
    warpEffects.append([0,
     v,
     ps,
     target])
    try:
        BigWorld.addWarp(100000, m2, v)
    except:
        pass

    return len(warpEffects) - 1


def endPlasmaWarp(idx):
    ps = warpEffects[idx][2]
    target = warpEffects[idx][3]
    try:
        target.node('biped Head').detach(ps)
    except:
        target.root.detach(ps)

    warpEffects[idx][1].keyframes = [(0, Vector4(0.0, 0.0, 1.0, 0.0))]
    warpEffects[idx][0] = 1
