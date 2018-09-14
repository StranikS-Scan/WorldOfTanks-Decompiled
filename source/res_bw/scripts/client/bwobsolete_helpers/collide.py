# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/collide.py
import BigWorld
import Math
import math
COLLIDE_ENTITY, COLLIDE_TERRAIN, COLLIDE_NONE, COLLIDE_OTHER = range(4)

def collide(x, y):
    player = BigWorld.player()
    if player is None:
        return (COLLIDE_OTHER, None)
    else:
        entity = BigWorld.target()
        if entity and entity != player:
            if hasattr(entity, 'intersectMouseCoordinates'):
                locationX, locationY = entity.intersectMouseCoordinates(x, y)
                if locationX != -1 or locationY != -1:
                    return (COLLIDE_ENTITY, entity)
            else:
                return (COLLIDE_ENTITY, entity)
        spaceID = player.spaceID
        src, dst = getMouseTargettingRay()
        terrain = BigWorld.collide(spaceID, src, dst)
        if terrain:
            return (COLLIDE_TERRAIN, terrain[0])
        return (COLLIDE_NONE, dst)
        return


def getMouseTargettingRay():
    mtm = Math.Matrix(BigWorld.MouseTargettingMatrix())
    src = mtm.applyToOrigin()
    far = BigWorld.projection().farPlane
    dst = src + mtm.applyToAxis(2).scale(far)
    return (src, dst)
