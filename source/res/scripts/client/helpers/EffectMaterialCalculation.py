# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EffectMaterialCalculation.py
from collections import namedtuple
import AreaDestructibles
import BigWorld
from DestructiblesCache import DESTR_TYPE_STRUCTURE
from constants import DESTRUCTIBLE_MATKIND
import material_kinds
SurfaceMaterial = namedtuple('SurfaceMaterial', ('point', 'surfaceNormal', 'matKind', 'effectIdx'))

def calcSurfaceMaterialNearPoint(point, normal, spaceID, defaultEffectMaterial='ground'):
    segStart = point - normal * 3.0
    segStop = point + normal * 2.0
    collided, hitPoint, surfNormal, matKind, fileName, _, _ = BigWorld.wg_getMatInfoNearPoint(spaceID, segStart, segStop, point, isDestructibleBroken)
    if collided:
        effectIdx = None
        if DESTRUCTIBLE_MATKIND.MIN <= matKind <= DESTRUCTIBLE_MATKIND.MAX:
            desc = AreaDestructibles.g_cache.getDescByFilename(fileName)
            if desc is not None:
                type = desc['type']
                if type == DESTR_TYPE_STRUCTURE:
                    moduleDesc = desc['modules'].get(matKind)
                    if moduleDesc is not None:
                        effectIdx = moduleDesc.get('effectMtrlIdx')
        else:
            effectIdx = calcEffectMaterialIndex(matKind)
        if effectIdx is None:
            effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[defaultEffectMaterial]
    else:
        effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[defaultEffectMaterial]
        hitPoint = point
        surfNormal = normal
        if DESTRUCTIBLE_MATKIND.DAMAGED_MIN <= matKind <= DESTRUCTIBLE_MATKIND.DAMAGED_MAX:
            matKind = 101
        else:
            matKind = 0
    return SurfaceMaterial(hitPoint, surfNormal, matKind, effectIdx)


def calcEffectMaterialIndex(matKind):
    if matKind != 0:
        return material_kinds.EFFECT_MATERIAL_INDEXES_BY_IDS.get(matKind)
    else:
        effectIndex = -1
        player = BigWorld.player()
        if player.__class__.__name__ == 'PlayerAvatar':
            arenaSpecificEffect = player.arena.arenaType.defaultGroundEffect
            if arenaSpecificEffect is not None:
                if arenaSpecificEffect == 'None':
                    return
                if not isinstance(arenaSpecificEffect, int):
                    effectIndex = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES.get(arenaSpecificEffect)
                    effectIndex = -1 if effectIndex is None else effectIndex
                    player.arena.arenaType.defaultGroundEffect = effectIndex
                else:
                    effectIndex = arenaSpecificEffect
        return effectIndex
        return


def isDestructibleBroken(chunkID, itemIndex, matKind, itemFilename):
    desc = AreaDestructibles.g_cache.getDescByFilename(itemFilename)
    if desc is None:
        return False
    else:
        ctrl = AreaDestructibles.g_destructiblesManager.getController(chunkID)
        return False if ctrl is None else ctrl.isDestructibleBroken(itemIndex, matKind, desc['type'])
