# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/prefab_effects.py
from PrefabEffectsAvailability import getDebugForceHitType, getPrefabEffectsAvailable, setPrefabEffectsEnabledForBattle
from constants import VEHICLE_HIT_EFFECT, IS_DEVELOPMENT
from items import vehicles
from items.components.component_constants import INVALID_EFFECT_INDEX

def _checkHitTypeOverride(hitType):
    if not IS_DEVELOPMENT:
        return hitType
    else:
        forced = getDebugForceHitType()
        return forced if forced is not None else hitType


def _resolveShotEffectItem(prefabEffIndex, hitType):
    shotEffect = vehicles.g_cache.prefabEffects.shot.effects[prefabEffIndex]
    item = shotEffect.groups.get(VEHICLE_HIT_EFFECT.getEffectGroup(hitType))
    if item is None or not item.prefab:
        item = shotEffect.defaultVehicleHit
    if item is None or not item.prefab:
        item = shotEffect.defaultHit
    return item


_DEFAULT_ENABLED_FOR_BATTLE = False
_cachedPrefabEffectsAvailable = _DEFAULT_ENABLED_FOR_BATTLE

def setCachePrefabEffectsEnabledForBattle(enabledForBattle):
    global _cachedPrefabEffectsAvailable
    setPrefabEffectsEnabledForBattle(enabledForBattle)
    _cachedPrefabEffectsAvailable = getPrefabEffectsAvailable()


def resetCachePrefabEffectsEnabledForBattle():
    global _cachedPrefabEffectsAvailable
    setPrefabEffectsEnabledForBattle(_DEFAULT_ENABLED_FOR_BATTLE)
    _cachedPrefabEffectsAvailable = _DEFAULT_ENABLED_FOR_BATTLE


def resolvePrefabStickerID(prefabEffIndex, hitType):
    item = _resolveShotEffectItem(prefabEffIndex, hitType)
    return INVALID_EFFECT_INDEX if item is None else item.decal


def resolveGunPrefabEffects(gunPrefabEffects):
    if not _cachedPrefabEffectsAvailable:
        return (None, None)
    elif gunPrefabEffects is None:
        return (None, None)
    else:
        excludeTags = gunPrefabEffects.replaces if gunPrefabEffects.replaces else None
        return (gunPrefabEffects, excludeTags)


def resolveShotPrefabEffect(prefabEffIndex, hitType):
    hitEffectCode = _checkHitTypeOverride(hitType)
    if not _cachedPrefabEffectsAvailable:
        return (INVALID_EFFECT_INDEX, hitEffectCode, None)
    elif prefabEffIndex == INVALID_EFFECT_INDEX:
        return (prefabEffIndex, hitEffectCode, None)
    else:
        hitItem = _resolveShotEffectItem(prefabEffIndex, hitEffectCode)
        excludeTags = hitItem.replaces if hitItem and hitItem.replaces else None
        return (prefabEffIndex, hitEffectCode, excludeTags)


def resolveDamageStickerPrefab(prefabEffIndex, hitType):
    hitEffectCode = _checkHitTypeOverride(hitType)
    return (INVALID_EFFECT_INDEX, hitEffectCode) if not _cachedPrefabEffectsAvailable else (prefabEffIndex, hitEffectCode)
