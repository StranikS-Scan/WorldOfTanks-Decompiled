# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/minimap/settings.py
from constants import LOOT_TYPE

class BattleRoyaleEntries(object):
    BATTLE_ROYALE_DEATH_ZONE = 'DeathZoneEntry'
    VIEW_RANGE_SECTOR = 'ViewRangeSectorEntry'
    BATTLE_ROYALE_MARKER = 'BRMarkerUI'


class ViewRangeSectorAs3Descr(object):
    AS_ADD_SECTOR = 'as_addSector'
    AS_UPDATE_SECTOR_RADIUS = 'as_updateSectorRadius'
    AS_INIT_ARENA_SIZE = 'as_initArenaSize'


class DeathZonesAs3Descr(object):
    AS_UPDATE_DEATH_ZONES = 'as_updateDeathZones'
    AS_INIT_DEATH_ZONE_SIZE = 'as_initDeathZoneSize'


class MarkersAs3Descr(object):
    AS_UPDATE_RADAR_RADIUS = 'updateRadarRadius'
    AS_PLAY_RADAR_ANIMATION = 'play'
    AS_UPDATE_MARKER = 'updateIcon'
    AS_ADD_MARKER = 'show'
    AS_REMOVE_MARKER = 'hide'
    AS_ADD_MARKER_LOOT_BY_TYPE_ID = {LOOT_TYPE.BASIC: 'loot',
     LOOT_TYPE.ADVANCED: 'improved_loot',
     LOOT_TYPE.AIRDROP: 'airdrop'}
    AS_ADD_MARKER_LOOT_BIG_BY_TYPE_ID = {LOOT_TYPE.BASIC: 'loot_big',
     LOOT_TYPE.ADVANCED: 'improved_loot_big',
     LOOT_TYPE.AIRDROP: 'airdrop_big'}
    AS_ADD_MARKER_ENEMY_VEHICLE = 'enemyVehicle'
    AS_ADD_MARKER_ENEMY_VEHICLE_BIG = 'enemyVehicle_big'
    AS_ADD_MARKER_SQUAD_VEHICLE = 'squadVehicle'
    AS_ADD_MARKER_BOT_VEHICLE = 'ally_bot_vehicle'
