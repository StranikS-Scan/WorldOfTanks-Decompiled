# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleEntity.py
from __future__ import absolute_import
import logging
from future.utils import viewitems, viewvalues
import BigWorld
import destructible_entities
import Math
from DestructibleEntityState import DestructibleEntityState
from DestructibleStickers import DestructibleStickers
from helpers.collisions import SegmentCollisionResultExt
from VehicleEffects import DamageFromShotDecoder
from constants import VEHICLE_HIT_EFFECT
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from shared_utils import nextTick
_logger = logging.getLogger(__name__)

class DestructibleEntity(BigWorld.Entity):

    @property
    def isPlayerTeam(self):
        return self.team == BigWorld.player().team

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.publicInfo = {'team': self.team}
        self.__stateTriggers = {'alive': self.isAlive,
         'destroyed': self.isDestroyed}
        self.targetCaps = [0]
        self.model = None
        self.__properties = destructible_entities.g_destructibleEntitiesCache.getDestructibleEntityType(self.typeID)
        self.__prereqs = None
        self.__destroyEffectsList = None
        self.__activeStateResource = None
        self.__prevDamageStickerCodes = None
        self.__stateResources = {}
        for stateName, stateProperties in viewitems(self.__properties.states):
            self.__stateResources[stateName] = DestructibleEntityState(stateName, stateProperties, self.id, self.__stateTriggers[stateName], self.spaceID)

        return

    def __checkStateTriggers(self):
        for state in viewvalues(self.__stateResources):
            if state.isTriggered():
                self.__updateState(state.name)
                return

    def prerequisites(self):
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.addDestructibleEntity(self)
        prereqs = []
        for stateResource in viewvalues(self.__stateResources):
            prereqs += stateResource.prereqs(self.spaceID)

        return prereqs

    def onEnterWorld(self, prereqs):
        self.__setPickingEnabled(self.isActive)
        for stateResource in viewvalues(self.__stateResources):
            stateResource.onResourcesLoaded(prereqs)
            stateResource.setParent(self.entityGameObject)

        self.__checkStateTriggers()
        self.__prevDamageStickerCodes = frozenset()
        self.__setDamageStickersDelayed(False)

    def onLeaveWorld(self):
        if self.__activeStateResource is not None:
            self.__activeStateResource.deactivate()
            self.__activeStateResource = None
        for stateResource in viewvalues(self.__stateResources):
            stateResource.destroy()

        self.__stateResources.clear()
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.removeDestructibleEntity(self)
        self.__stateTriggers.clear()
        return

    def onHealthChanged(self, newHealth, attackerID, attackReasonID, hitFlags):
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.updateDestructibleEntityHealth(self, self.health, attackerID, attackReasonID, hitFlags)
        return

    def showDamageFromShot(self, attackerID, hitEffectCode, damage, gunInstallationIndex):
        if hitEffectCode is None or not self.isAlive() or attackerID != BigWorld.player().playerVehicleID:
            return
        else:
            hasPiercedHit = DamageFromShotDecoder.hasDamaged(hitEffectCode)
            if hitEffectCode in VEHICLE_HIT_EFFECT.RICOCHETS:
                eventID = _FET.VEHICLE_RICOCHET
            elif hitEffectCode == VEHICLE_HIT_EFFECT.CRITICAL_HIT:
                eventID = _FET.VEHICLE_CRITICAL_HIT
            elif hasPiercedHit:
                eventID = _FET.VEHICLE_ARMOR_PIERCED
            else:
                eventID = _FET.VEHICLE_HIT
            destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
            if destructibleEntityComponent is not None:
                destructibleEntityComponent.updateDestructibleEntityFeedback(self, eventID, gunInstallationIndex, damage)
            return

    def showDamageFromExplosion(self, attackerID, damage, gunInstallationIndex):
        if not self.isAlive() or attackerID != BigWorld.player().playerVehicleID:
            return
        else:
            destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
            if destructibleEntityComponent is not None:
                destructibleEntityComponent.updateDestructibleEntityFeedback(self, _FET.VEHICLE_ARMOR_PIERCED, gunInstallationIndex, damage)
            return

    def set_health(self, oldValue):
        self.__checkStateTriggers()

    def set_isActive(self, oldValue):
        self.__setPickingEnabled(self.isActive)
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.updateDestructibleEntityActiveState(self)
        return

    def set_damageStickers(self, prev=None):
        self.__setDamageStickers(True)

    def __setDamageStickers(self, isActive):
        if not self.isAlive():
            return
        else:
            prev = self.__prevDamageStickerCodes
            stickerMap = {DamageFromShotDecoder.encodeHitPoint(hitPoint):hitPoint for hitPoint in self.damageStickers}
            curr = set(stickerMap.keys())
            for code in prev.difference(curr):
                for damageStickers in viewvalues(self.__activeStateResource.damageStickers):
                    damageStickers.delDamageSticker(code)

            collisionComponent = self.__activeStateResource.collisionComponent
            for code in curr.difference(prev):
                parsedHitPoint = DamageFromShotDecoder.parseDamageStickerHitPoint(stickerMap[code], collisionComponent)
                if parsedHitPoint is None:
                    curr.discard(code)
                stickerID, prefabEffIndex, data = parsedHitPoint
                if data.componentIdx not in self.__activeStateResource.damageStickers:
                    _logger.error('component is not available for damage sticker: %d', data.componentIdx)
                    continue
                segStart, segEnd = self.__activeStateResource.reduceSegmentLength(data.componentIdx, data.segStart, data.segEnd)
                data._replace(segStart=segStart, segEnd=segEnd)
                stickers = self.__activeStateResource.damageStickers[data.componentIdx]
                stickers.addDamageSticker(code, stickerID, prefabEffIndex, data, collisionComponent, isActive)

            self.__prevDamageStickerCodes = frozenset(curr)
            return

    @nextTick
    def __setDamageStickersDelayed(self, isActive):
        self.__setDamageStickers(isActive)

    def collideSegmentExt(self, startPoint, endPoint):
        if self.__activeStateResource is not None:
            collisions = self.__activeStateResource.collideAllWorld(startPoint, endPoint)
            if collisions:
                res = []
                for collision in collisions:
                    matInfo = self.getMatinfo(collision[3], collision[2])
                    res.append(SegmentCollisionResultExt(collision[0], collision[1], matInfo, collision[3]))

                return res
        return

    def getMatinfo(self, partIndex, matKind):
        return self.__properties.materials.get(matKind, None)

    def isDestructibleComponent(self, componentID):
        return self.__activeStateResource.isDestructibleComponent(componentID) if self.__activeStateResource is not None else False

    def __updateState(self, stateName):
        if self.__activeStateResource is not None:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.model.matrix = None
            self.model = None
            self.__activeStateResource.deactivate()
        self.__activeStateResource = self.__stateResources.get(stateName, None)
        if self.__activeStateResource is not None:
            visualModel = self.__activeStateResource.activate(self.matrix)
            self.model = visualModel
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.updateDestructibleEntityDestructionState(self)
        return

    def getGuiNode(self):
        return self.__activeStateResource.guiNode if self.__activeStateResource is not None else None

    def isAlive(self):
        return self.health > 0

    def isDestroyed(self):
        return not self.isAlive()

    def drawEdge(self, forceSimpleEdge=False):
        if not self.model or not self.model.visible:
            return
        colorMode = 2 if self.isPlayerTeam else 1
        BigWorld.wgAddEdgeDetectEntity(self, self.__activeStateResource.collisionComponent, colorMode, False, 0, False, False)

    def removeEdge(self, forceSimpleEdge=False):
        if self.model:
            BigWorld.wgDelEdgeDetectEntity(self)

    def getStateBounds(self, stateName, partIndex):
        state = self.__stateResources.get(stateName, None)
        return (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0) if not state else state.collisionComponent.getBoundingBox(partIndex)

    def __setPickingEnabled(self, enable):
        self.targetCaps = [1] if enable else [0]
