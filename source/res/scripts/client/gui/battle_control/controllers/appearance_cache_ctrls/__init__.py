# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/appearance_cache_ctrls/__init__.py
from __future__ import absolute_import
from future.utils import itervalues
import BigWorld
from items import vehicles

def getWholeVehModels(vDesc):
    nationID, vehicleTypeID = vehicles.g_list.getIDsByName(vDesc.name)
    vType = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
    prereqs = set(vDesc.prerequisites())
    models = set()
    bspModels = set()
    index = 0
    for chassie in vType.chassis:
        models.add(chassie.models.undamaged)
        splinePairs = chassie.splineDesc.trackPairs if chassie.splineDesc else {}
        for splinePairDesc in itervalues(splinePairs):
            if splinePairDesc is not None:
                models.add(splinePairDesc.segmentModelLeft())
                models.add(splinePairDesc.segmentModelRight())
                models.add(splinePairDesc.segment2ModelLeft())
                models.add(splinePairDesc.segment2ModelRight())

        bspModels.add((index, chassie.hitTester.bspModelName))
        index += 1

    for hull in vType.hulls:
        prereqs.add(hull.models.undamaged)
        bspModels.add((index, hull.hitTester.bspModelName))
        index += 1

    for turrets in vType.turrets:
        for turret in turrets:
            models.add(turret.models.undamaged)
            bspModels.add((index, turret.hitTester.bspModelName))
            index += 1
            for gun in turret.guns:
                models.add(gun.models.undamaged)
                bspModels.add((index, gun.hitTester.bspModelName))
                index += 1

    result = list(prereqs)
    for model in models:
        if not model:
            continue
        compoundAssembler = BigWorld.CompoundAssembler()
        compoundAssembler.addRootPart(model, 'root')
        compoundAssembler.name = model
        compoundAssembler.spaceID = BigWorld.player().spaceID
        result.append(compoundAssembler)

    result.append(BigWorld.CollisionAssembler(tuple(bspModels), BigWorld.player().spaceID))
    return result
