# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/cosmic_battle_effects_ctrl.py
import BigWorld
import CGF
import cosmic_prefabs
from debug_utils import LOG_ERROR
from GenericComponents import TransformComponent
from gui.battle_control.battle_constants import BATTLE_CTRL_NAMES
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from helpers.events_handler import EventsHandler
from functools import partial
from Math import Vector3
from math_utils import createSRTMatrix, createRTMatrix
from Vehicle import Vehicle
from cosmic_event.gui.shared.events import LootEvent, CosmicVehicleEvent, MeteoriteZoneEvent, MineEvent, Teleport
from cosmic_event_common.cosmic_constants import LOOT_ITEM_ID
from cosmic_sound import CosmicBattleSounds, playVoiceover, play3DSoundEvent, play2DSoundEvent

class BattleEffectsCtrl(IBattleController):

    def __init__(self):
        super(BattleEffectsCtrl, self).__init__()
        self.__ctrls = self.__initializeCtrls()

    def startControl(self):
        for ctrl in self.__ctrls:
            ctrl.startControl()

    def stopControl(self):
        for ctrl in self.__ctrls:
            ctrl.stopControl()

        self.__ctrls = None
        return

    def getControllerID(self):
        return len(BATTLE_CTRL_NAMES) + 1

    def __initializeCtrls(self):
        return [_LootEffectCtrl(),
         _CoralEffectCtrl(),
         _MeteoriteZoneEffectCtrl(),
         _TeleportEffectCtrl(),
         _MineEffectCtrl()]


class _EffectCtrlBase(EventsHandler, IBattleController):

    def getControllerID(self):
        return None

    def startControl(self):
        self._subscribe()

    def stopControl(self):
        self._unsubscribe()

    def loadPrefabInHierarchy(self, prefabPath, parentGO, prefabStorage, offset=Vector3()):
        wrappedCb = partial(self.__onPrefabLoaded, prefabStorage, parentGO.id)
        CGF.loadGameObjectIntoHierarchy(prefabPath, parentGO, offset, wrappedCb)

    def unloadPrefab(self, prefabStorage, goID):
        if goID in prefabStorage:
            CGF.removeGameObject(prefabStorage[goID])
            prefabStorage.pop(goID)

    def _getListeners(self):
        return []

    def __onPrefabLoaded(self, prefabStorage, entityID, go):
        if entityID in prefabStorage:
            CGF.removeGameObject(prefabStorage[entityID])
            prefabStorage[entityID] = None
        prefabStorage[entityID] = go
        return


class _LootEffectCtrl(_EffectCtrlBase):

    def __init__(self):
        super(_LootEffectCtrl, self).__init__()
        self.__lootPrefabs = {}
        self.__portalPrefabs = {}

    def stopControl(self):
        for go in self.__lootPrefabs.itervalues():
            CGF.removeGameObject(go)

        self.__lootPrefabs.clear()
        for go in self.__portalPrefabs.itervalues():
            CGF.removeGameObject(go)

        self.__portalPrefabs.clear()
        super(_LootEffectCtrl, self).stopControl()

    def _getListeners(self):
        return [(LootEvent.SPAWNED,
          self.__onLootSpawn,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (LootEvent.PREPARING,
          self.__onPreparing,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (LootEvent.PICKED_UP,
          self.__onPickedUp,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]

    def __onLootSpawn(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            LOG_ERROR('[cosmic_battle]: invalid loot')
            return
        prefabPath = cosmic_prefabs.LOOT_SPAWNED_PREFABS.get(loot.itemID, cosmic_prefabs.Loot.UNKNOWN)
        offset = Vector3(0, -6, 0) if loot.itemID == LOOT_ITEM_ID.COSMIC_CORAL else Vector3()
        self.loadPrefabInHierarchy(prefabPath, loot.entityGameObject, self.__lootPrefabs, offset=offset)
        if loot.itemID != LOOT_ITEM_ID.COSMIC_CORAL:
            CosmicBattleSounds.playDronAppear(loot.position)
            self.loadPrefabInHierarchy(cosmic_prefabs.Loot.COSMIC_LOOT_PORTAL, loot.entityGameObject, self.__portalPrefabs)

    def __onPreparing(self, event):
        loot = event.ctx.get('loot')
        if loot.itemID == LOOT_ITEM_ID.COSMIC_CORAL:
            return
        if not loot:
            LOG_ERROR('[cosmic_battle]: invalid loot')
            return
        prefabPath = cosmic_prefabs.LOOT_PREPARING_PREFABS.get(loot.itemID, cosmic_prefabs.Loot.UNKNOWN)
        self.loadPrefabInHierarchy(prefabPath, loot.entityGameObject, self.__lootPrefabs)

    def __onPickedUp(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            LOG_ERROR('[cosmic_battle]: invalid loot')
            return
        self.unloadPrefab(self.__lootPrefabs, loot.entityGameObject.id)
        if loot.itemID != LOOT_ITEM_ID.COSMIC_CORAL:
            CosmicBattleSounds.playDronDisappear(loot.position)
            self.loadPrefabInHierarchy(cosmic_prefabs.Loot.COSMIC_LOOT_PORTAL, loot.entityGameObject, self.__portalPrefabs)


class _CoralEffectCtrl(_EffectCtrlBase):

    def __init__(self):
        super(_CoralEffectCtrl, self).__init__()
        self.__researchPrefabs = {}
        self.__coralTransferPrefabs = {}
        self.__isMusicStateOn = False

    def stopControl(self):
        for go in self.__researchPrefabs.itervalues():
            CGF.removeGameObject(go)

        for go in self.__coralTransferPrefabs.itervalues():
            CGF.removeGameObject(go)

        self.__researchPrefabs.clear()
        self.__coralTransferPrefabs.clear()
        super(_CoralEffectCtrl, self).stopControl()

    def _getListeners(self):
        return [(CosmicVehicleEvent.START_LOOT_RESEARCHING,
          self.__onCoralResearchStart,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT),
         (CosmicVehicleEvent.STOP_LOOT_RESEARCHING,
          self.__onCoralResearchStop,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT),
         (CosmicVehicleEvent.LOOT_TRANSFER,
          self.__onCoralTransfered,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT),
         (CosmicVehicleEvent.LOOT_RESEARCHING_DONE,
          self.__onCoralResearchDone,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT),
         (LootEvent.SPAWNED,
          self.__onLootSpawned,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT),
         (LootEvent.DESTROYED,
          self.__onLootDestroyed,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT)]

    def __onCoralResearchStart(self, event):
        vehicleGO = event.ctx['vehicleGO']
        ownerID = event.ctx['ownerID']
        if ownerID == BigWorld.player().playerVehicleID:
            prefabPath = cosmic_prefabs.Loot.COSMIC_CORAL_RESEARCH_PC
        else:
            prefabPath = cosmic_prefabs.Loot.COSMIC_CORAL_RESEARCH_NPC
        self.loadPrefabInHierarchy(prefabPath, vehicleGO, self.__researchPrefabs, offset=Vector3(0, -1, 0))

    def __onCoralResearchStop(self, event):
        vehicleGO = event.ctx['vehicleGO']
        self.unloadPrefab(self.__researchPrefabs, vehicleGO.id)

    def __onCoralTransfered(self, event):
        entityFromID = event.ctx['fromEntityID']
        entityDestID = event.ctx['destEntityID']
        entityFrom = BigWorld.entities[entityFromID]
        entityDest = BigWorld.entities[entityDestID]
        self.loadPrefabInHierarchy(cosmic_prefabs.Loot.COSMIC_CORAL_WASTER, entityFrom.entityGameObject, self.__coralTransferPrefabs, offset=Vector3())
        self.loadPrefabInHierarchy(cosmic_prefabs.Loot.COSMIC_CORAL_OBTAINER, entityDest.entityGameObject, self.__coralTransferPrefabs, offset=Vector3())
        if not isinstance(entityFrom, Vehicle):
            return
        if entityFromID == BigWorld.player().playerVehicleID:
            play3DSoundEvent(CosmicBattleSounds.CORAL_LOSE_PC, entityFrom.position)
        else:
            play3DSoundEvent(CosmicBattleSounds.CORAL_LOSE_NPC, entityFrom.position)

    def __onCoralResearchDone(self, event):
        isPC = event.ctx['isPC']
        position = event.ctx['position']
        sound = CosmicBattleSounds.CORAL_RESEARCH_DONE_PC if isPC else CosmicBattleSounds.CORAL_RESEARCH_DONE_NPC
        play3DSoundEvent(sound, position)

    def __onLootSpawned(self, event):
        loot = event.ctx['loot']
        if loot.itemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        if not self.__isMusicStateOn:
            self.__isMusicStateOn = True
            play2DSoundEvent(CosmicBattleSounds.CORAL_SPAWNED_STATE_TRIGGER)

    def __onLootDestroyed(self, event):
        loot = event.ctx['loot']
        if loot.itemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        play2DSoundEvent(CosmicBattleSounds.CORAL_DISAPPEARED_STATE_TRIGGER)
        self.__isMusicStateOn = False


class _MeteoriteZoneEffectCtrl(_EffectCtrlBase):

    def __init__(self):
        super(_MeteoriteZoneEffectCtrl, self).__init__()
        self.__entities = {}
        self.__prefabs = {}

    def stopControl(self):
        for go in self.__prefabs.itervalues():
            CGF.removeGameObject(go)

        self.__prefabs.clear()
        self.__entities.clear()
        super(_MeteoriteZoneEffectCtrl, self).stopControl()

    def _getListeners(self):
        return [(MeteoriteZoneEvent.VEHICLE_DAMAGE,
          self.__onDamage,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT), (MeteoriteZoneEvent.STATE_CHANGED,
          self.__onStateChanged,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT)]

    def __loadMeteoriteZone(self, entityId, go):
        if entityId not in self.__entities:
            LOG_ERROR('Try to load unregistered prefab in the hierarchy of ', entityId)
        if self.__entities[entityId].isActive:
            self.__prefabs[entityId] = go
        else:
            CGF.removeGameObject(go)

    def __onStateChanged(self, event):
        entity = event.ctx['entity']
        self.__entities[entity.entityGameObject.id] = entity
        goId = entity.entityGameObject.id
        if entity.isActive:
            playVoiceover(CosmicBattleSounds.ScanningZone.SCANNING_ZONE_PREPARING)
            offset = Vector3(0, -6, 0)
            wrappedCb = partial(self.__loadMeteoriteZone, goId)
            CGF.loadGameObjectIntoHierarchy(cosmic_prefabs.Loot.COSMIC_CORAL_PREPARING, entity.entityGameObject, offset, wrappedCb)
        elif goId in self.__prefabs:
            go = self.__prefabs.pop(goId)
            CGF.removeGameObject(go)

    def __onDamage(self, event):
        vehicles = event.ctx['vehicles']
        for vehID in vehicles:
            vehicle = BigWorld.entities[vehID]
            vehGO = vehicle.entityGameObject
            CosmicBattleSounds.playRammingSound(vehicle.position)
            self.loadPrefabInHierarchy(cosmic_prefabs.MeteoriteZone.DAMAGE, vehGO, self.__prefabs, offset=Vector3(0, 2, 0))


class _TeleportEffectCtrl(_EffectCtrlBase):
    __TP_MARKER_SCALE = Vector3(1, 1, 1)
    __TELEPORT_EFFECT_OFFSET = Vector3(0, 3.5, 0)

    def __init__(self):
        super(_TeleportEffectCtrl, self).__init__()
        self.__prefabs = {}
        self.__markerGO = None
        return

    def stopControl(self):
        self.__removeMarker()
        for go in self.__prefabs.itervalues():
            CGF.removeGameObject(go)

        self.__prefabs.clear()
        super(_TeleportEffectCtrl, self).stopControl()

    def _getListeners(self):
        return [(Teleport.PREPARED,
          self.__onPrepared,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT), (Teleport.ACTIVATED,
          self.__onActivated,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT), (Teleport.EXHAUSTED,
          self.__onExhausted,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT)]

    def __onPrepared(self, event):
        teleportPosition = event.ctx['position']
        self.__markerGO = CGF.GameObject(BigWorld.player().spaceID)
        matrix = createSRTMatrix(self.__TP_MARKER_SCALE, Vector3(), teleportPosition)
        self.__markerGO.createComponent(TransformComponent, matrix)
        CGF.loadGameObjectIntoHierarchy(cosmic_prefabs.Marker.TELEPORT, self.__markerGO, self.__TELEPORT_EFFECT_OFFSET)
        self.__markerGO.activate()

    def __onActivated(self, event):
        self.__removeMarker()
        go = event.ctx['go']
        CGF.loadGameObject(cosmic_prefabs.Vehicle.TELEPORT_ACTIVATED, BigWorld.player().spaceID, go + self.__TELEPORT_EFFECT_OFFSET)

    def __onExhausted(self, event):
        self.__removeMarker()

    def __removeMarker(self):
        if self.__markerGO:
            CGF.removeGameObject(self.__markerGO)
            self.__markerGO = None
        return


class _MineEffectCtrl(_EffectCtrlBase):
    __EXPLOSION_REMOVE_DELAY = 2.0

    def __init__(self):
        super(_MineEffectCtrl, self).__init__()
        self.__minePrefabs = {}
        self.__mineExplosionPrefabs = {}
        self.__cbIDs = {}

    def stopControl(self):
        for go in self.__minePrefabs.itervalues():
            CGF.removeGameObject(go)

        self.__minePrefabs.clear()
        for go in self.__mineExplosionPrefabs.itervalues():
            CGF.removeGameObject(go)

        self.__mineExplosionPrefabs.clear()
        self.__mineExplosionPrefabs = None
        for cbID in self.__cbIDs.itervalues():
            BigWorld.cancelCallback(cbID)

        self.__cbIDs.clear()
        self.__cbIDs = None
        super(_MineEffectCtrl, self).stopControl()
        return

    def _getListeners(self):
        return [(MineEvent.APPEAR,
          self.__onAppear,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT), (MineEvent.EXPLODE,
          self.__onExplode,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.DEFAULT)]

    def __onAppear(self, event):
        mine = event.ctx['entity']
        self.loadPrefabInHierarchy(cosmic_prefabs.Mine.MODEL, mine.entityGameObject, self.__minePrefabs)

    def __onExplode(self, event):
        mine = event.ctx['entity']
        self.unloadPrefab(self.__minePrefabs, mine.entityGameObject.id)
        go = CGF.GameObject(BigWorld.player().spaceID)
        go.createComponent(TransformComponent, createRTMatrix(Vector3(), mine.position))
        CGF.loadGameObjectIntoHierarchy(cosmic_prefabs.Mine.EXPLOSION, go, Vector3())
        go.activate()
        self.__mineExplosionPrefabs[go.id] = go
        cbID = BigWorld.callback(self.__EXPLOSION_REMOVE_DELAY, partial(self.__destroyExplosionPrefab, go.id, mine.id))
        self.__cbIDs[mine.id] = cbID

    def __destroyExplosionPrefab(self, goID, entityID):
        self.unloadPrefab(self.__mineExplosionPrefabs, goID)
        if goID in self.__mineExplosionPrefabs:
            del self.__mineExplosionPrefabs[goID]
        if entityID in self.__cbIDs:
            del self.__cbIDs[entityID]
