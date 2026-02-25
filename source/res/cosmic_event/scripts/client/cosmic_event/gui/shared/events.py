# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/shared/events.py
from gui.shared.events import HasCtxEvent

class ArtifactScanningEvent(HasCtxEvent):
    VEHICLES_IN_ZONE_CHANGED = 'artifact/vehiclesInZoneChanged'
    ANNOUNCEMENT_CREATED = 'artifact/announced'
    ARTIFACT_SCANNING_READY = 'artifact/scanningReady'
    ARTIFACT_DESTROYED = 'artifact/destroyed'


class LootEvent(HasCtxEvent):
    PREPARING = 'loot/preparing'
    SPAWNED = 'loot/spawned'
    PICKED_UP = 'loot/pickedUp'
    DESTROYED = 'loot/destroyed'


class CosmicVehicleEvent(HasCtxEvent):
    START_LOOT_RESEARCHING = 'cosmicVehicle/startLootResearching'
    STOP_LOOT_RESEARCHING = 'cosmicVehicle/stopLootResearching'
    LOOT_RESEARCHING_DONE = 'cosmicVehicle/lootResearchingDone'
    LOOT_TRANSFER = 'cosmicVehicle/lootTransfer'
    START_TELEPORT = 'cosmicVehicle/startTeleport'
    TELEPORT_PREPARED = 'cosmicVehicle/teleportPrepared'


class MeteoriteZoneEvent(HasCtxEvent):
    STATE_CHANGED = 'zone/stateChanged'
    DEACTIVATE = 'zone/deactivate'
    VEHICLE_DAMAGE = 'zone/damage'
    LOOT_PREPARING = 'zone/lootPreparing'


class MineEvent(HasCtxEvent):
    APPEAR = 'mine/appear'
    EXPLODE = 'mine/explode'


class Teleport(HasCtxEvent):
    ACTIVATED = 'teleport/activate'
    PREPARED = 'teleport/prepared'
    EXHAUSTED = 'teleport/exhausted'
