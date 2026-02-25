# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_prefabs.py
from cosmic_event_common.cosmic_constants import LOOT_ITEM_ID

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
    TELEPORT_ACTIVATED = 'content/CGFPrefabs/cosmic_event/cosmic_event_teleport_activated.prefab'
    RANGE = (COLLISION_EFFECT, RAMMING_FIELD, TELEPORT_ACTIVATED)


class Debuf(object):
    STUN_DEBUF = 'content/CGFPrefabs/cosmic_event/cosmic_event_stun_debuff.prefab'
    RANGE = (STUN_DEBUF,)


class Loot(object):
    COSMIC_BLACK_HOLE = 'content/CGFPrefabs/cosmic_event/cosmic_event_supernova_item.prefab'
    COSMIC_SHOOTING = 'content/CGFPrefabs/cosmic_event/cosmic_event_sniper_shoot_item.prefab'
    COSMIC_GRAVITY_FIELD = 'content/CGFPrefabs/cosmic_event/cosmic_event_overcharge_item.prefab'
    COSMIC_POWER_SHOT = 'content/CGFPrefabs/cosmic_event/cosmic_event_power_shot_item.prefab'
    COSMIC_TELEPORT = 'content/CGFPrefabs/cosmic_event/cosmic_event_teleport_item.prefab'
    COSMIC_CORAL_PREPARING = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_preparing.prefab'
    COSMIC_CORAL_SPAWNED = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_spawned.prefab'
    COSMIC_CORAL_RESEARCH_PC = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_research_pc.prefab'
    COSMIC_CORAL_RESEARCH_NPC = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_research_npc.prefab'
    COSMIC_CORAL_OBTAINER = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_obtainer.prefab'
    COSMIC_CORAL_WASTER = 'content/CGFPrefabs/cosmic_event/cosmic_event_coral_waster.prefab'
    COSMIC_LOOT_PORTAL = 'content/CGFPrefabs/cosmic_event/cosmic_event_portal_flash.prefab'
    UNKNOWN = 'content/CGFPrefabs/cosmic_event/cosmic_event_unknown_item.prefab'
    RANGE_LOOT = (COSMIC_BLACK_HOLE,
     COSMIC_SHOOTING,
     COSMIC_GRAVITY_FIELD,
     COSMIC_POWER_SHOT,
     COSMIC_TELEPORT,
     COSMIC_CORAL_PREPARING,
     COSMIC_CORAL_SPAWNED,
     COSMIC_CORAL_RESEARCH_PC,
     COSMIC_CORAL_RESEARCH_NPC,
     COSMIC_CORAL_OBTAINER,
     COSMIC_CORAL_WASTER,
     COSMIC_LOOT_PORTAL,
     UNKNOWN)


class Marker(object):
    TELEPORT = 'content/CGFPrefabs/cosmic_event/cosmic_event_teleport_marker.prefab'
    RANGE = (TELEPORT,)


class MeteoriteZone(object):
    ACTIVE = 'content/CGFPrefabs/cosmic_event/cosmic_meteorite_zone_active.prefab'
    DAMAGE = 'content/CGFPrefabs/cosmic_event/cosmic_event_vehicle_in_meteorite_zone.prefab'
    RANGE = (ACTIVE, DAMAGE)


class Mine(object):
    MODEL = 'content/CGFPrefabs/cosmic_event/cosmic_event_repulsion_mine.prefab'
    EXPLOSION = 'content/CGFPrefabs/cosmic_event/cosmic_event_mine_explosion.prefab'
    RANGE = (MODEL, EXPLOSION)


LOOT_SPAWNED_PREFABS = {LOOT_ITEM_ID.COSMIC_BLACK_HOLE: Loot.COSMIC_BLACK_HOLE,
 LOOT_ITEM_ID.COSMIC_SHOOTING: Loot.COSMIC_SHOOTING,
 LOOT_ITEM_ID.COSMIC_GRAVITY_FIELD: Loot.COSMIC_GRAVITY_FIELD,
 LOOT_ITEM_ID.COSMIC_POWER_SHOT: Loot.COSMIC_POWER_SHOT,
 LOOT_ITEM_ID.COSMIC_CORAL: Loot.COSMIC_CORAL_SPAWNED,
 LOOT_ITEM_ID.COSMIC_TELEPORT: Loot.COSMIC_TELEPORT}
LOOT_PREPARING_PREFABS = {LOOT_ITEM_ID.COSMIC_BLACK_HOLE: Loot.UNKNOWN,
 LOOT_ITEM_ID.COSMIC_SHOOTING: Loot.UNKNOWN,
 LOOT_ITEM_ID.COSMIC_GRAVITY_FIELD: Loot.UNKNOWN,
 LOOT_ITEM_ID.COSMIC_POWER_SHOT: Loot.UNKNOWN,
 LOOT_ITEM_ID.COSMIC_TELEPORT: Loot.UNKNOWN,
 LOOT_ITEM_ID.COSMIC_CORAL: Loot.COSMIC_CORAL_PREPARING}
