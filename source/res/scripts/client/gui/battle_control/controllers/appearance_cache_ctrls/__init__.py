# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/appearance_cache_ctrls/__init__.py
import BigWorld
from items import vehicles

def getWholeVehModels(vDesc):
    nationID, vehicleTypeID = vehicles.g_list.getIDsByName(vDesc.name)
    vType = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
    prereqs = set(vDesc.prerequisites())
    bspModels = set()
    index = 0
    for chassie in vType.chassis:
        prereqs.add(chassie.models.undamaged)
        splineDesc = chassie.splineDesc
        if splineDesc is not None:
            prereqs.add(splineDesc.segmentModelLeft())
            prereqs.add(splineDesc.segmentModelRight())
            prereqs.add(splineDesc.segment2ModelLeft())
            prereqs.add(splineDesc.segment2ModelRight())
        bspModels.add((index, chassie.hitTester.bspModelName))
        index += 1

    for hull in vType.hulls:
        prereqs.add(hull.models.undamaged)
        bspModels.add((index, hull.hitTester.bspModelName))
        index += 1

    for turrets in vType.turrets:
        for turret in turrets:
            prereqs.add(turret.models.undamaged)
            bspModels.add((index, turret.hitTester.bspModelName))
            index += 1
            for gun in turret.guns:
                prereqs.add(gun.models.undamaged)
                bspModels.add((index, gun.hitTester.bspModelName))
                index += 1

    prereqs.add(BigWorld.CollisionAssembler(tuple(bspModels), BigWorld.player().spaceID))
    return list(prereqs)
