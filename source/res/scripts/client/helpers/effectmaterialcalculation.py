# Embedded file name: scripts/client/helpers/EffectMaterialCalculation.py
from collections import namedtuple
import AreaDestructibles
import BigWorld
from DestructiblesCache import DESTR_TYPE_STRUCTURE
from constants import DESTRUCTIBLE_MATKIND
import material_kinds
SurfaceMaterial = namedtuple('SurfaceMaterial', ('point', 'surfaceNormal', 'matKind', 'effectIdx'))

def calcSurfaceMaterialNearPoint(point, normal, spaceID, defaultEffectMaterial = 'ground'):
    segStart = point - normal * 3.0
    segStop = point + normal * 2.0
    matInfo = BigWorld.wg_getMatInfoNearPoint(spaceID, segStart, segStop, point, isDestructibleBroken)
    matKind = 0
    if matInfo is None:
        effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[defaultEffectMaterial]
        hitPoint = point
        surfNormal = normal
    else:
        hitPoint, surfNormal, chunkID, itemIndex, matKind, fileName = matInfo
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
        if ctrl is None:
            return False
        return ctrl.isDestructibleBroken(itemIndex, matKind, desc['type'])
