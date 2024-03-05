# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_prefabs.py


class Artifact(object):
    SMALL_HINT = 'content/CGFPrefabs/cosmic_event/cosmic_artifact_hint_s_zone.prefab'
    SMALL_APPEARING_EFFECT = 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_spawn_s_zone_02.prefab'
    SMALL_ZONE_PREFAB = 'content/CGFPrefabs/cosmic_event/cosmic_event_capture_zone_small.prefab'
    BIG_HINT = 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_spawn_l_zone_01.prefab'
    BIG_ZONE_PREFAB = 'content/CGFPrefabs/cosmic_event/cosmic_event_capture_zone_big.prefab'
    SMALL_APPEARANCE_RANGE = (SMALL_APPEARING_EFFECT, SMALL_ZONE_PREFAB)
    BIG_APPEARANCE_RANGE = (BIG_ZONE_PREFAB,)
    RANGE = SMALL_APPEARANCE_RANGE + BIG_APPEARANCE_RANGE + (SMALL_HINT, BIG_HINT)


class Vehicle(object):
    COLLISION_EFFECT = 'content/CGFPrefabs/cosmic_event/cosmic_event_collision_effect.prefab'
    RAMMING_FIELD = 'content/CGFPrefabs/cosmic_event/cosmic_event_ramming_field.prefab'
    RANGE = (COLLISION_EFFECT, RAMMING_FIELD)


class Loot(object):
    COSMIC_BLACK_HOLE = 'content/CGFPrefabs/cosmic_event/cosmic_event_supernova_item.prefab'
    COSMIC_SHOOTING = 'content/CGFPrefabs/cosmic_event/cosmic_event_sniper_shoot_item.prefab'
    COSMIC_GRAVITY_FIELD = 'content/CGFPrefabs/cosmic_event/cosmic_event_overcharge_item.prefab'
    COSMIC_POWER_SHOT = 'content/CGFPrefabs/cosmic_event/cosmic_event_power_shot_item.prefab'
    UNKNOWN = 'content/CGFPrefabs/cosmic_event/cosmic_event_unknown_item.prefab'
    RANGE_LOOT = (COSMIC_BLACK_HOLE,
     COSMIC_SHOOTING,
     COSMIC_GRAVITY_FIELD,
     COSMIC_POWER_SHOT,
     UNKNOWN)
