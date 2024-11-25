# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/events.py
from gui.shared.events import HasCtxEvent

class DeathZoneEvent(HasCtxEvent):
    UPDATE_DEATH_ZONE = 'deathZone/update'


class AirDropEvent(HasCtxEvent):
    AIR_DROP_SPAWNED = 'onAirDropSpawned'
    AIR_DROP_LANDED = 'onAirDropLanded'
    AIR_DROP_ENTERED = 'onAirDropEntered'
    AIR_DROP_LEFT = 'onAirDropLeft'
    AIR_DROP_NXT_SPAWNED = 'onAirDropNxtSpawned'


class LootEvent(HasCtxEvent):
    LOOT_PICKED_UP = 'onLootPickedUp'
