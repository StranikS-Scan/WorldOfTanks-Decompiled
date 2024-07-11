# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races_prefabs.py


class Loot(object):
    RACES_RAPIDSHELLING = 'content/CGFPrefabs/races/races_burst_fire.prefab'
    RACES_SHIELD = 'content/CGFPrefabs/races/races_shield.prefab'
    RACES_ROCKET_BOOSTER = 'content/CGFPrefabs/races/races_boost.prefab'
    RACES_POWER_IMPULSE = 'content/CGFPrefabs/races/races_impulse.prefab'
    UNKNOWN = 'content/CGFPrefabs/cosmic_event/cosmic_event_unknown_item.prefab'
    RANGE_LOOT = (RACES_RAPIDSHELLING,
     RACES_SHIELD,
     RACES_ROCKET_BOOSTER,
     RACES_POWER_IMPULSE,
     UNKNOWN)


class Vehicle(object):
    COLLISION_EFFECT = 'content/CGFPrefabs/races/races_collision_effect.prefab'
    RAMMING_FIELD = 'content/CGFPrefabs/races/races_ramming_field.prefab'
    RANGE = (COLLISION_EFFECT, RAMMING_FIELD)


LINK_DETECTOR = 'content/CGFPrefabs/races/runtimeLoad/link_detector.prefab'
