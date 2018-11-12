# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleEntity.py
import BigWorld
import destructible_entities
import Math
from debug_utils import LOG_ERROR
from DestructibleStickers import DestructibleStickers
from Vehicle import SegmentCollisionResultExt
from VehicleEffects import DamageFromShotDecoder
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from vehicle_systems.tankStructure import ColliderTypes
import helpers
COLLISION_SEGMENT_LENGTH = 2

class PART_PROPERTIES(object):
    HIGHLIGHTABLE = 0


class ASSEMBLER_NAME_SUFFIXES(object):
    VISUAL = '_vis'
    PHYSICS = '_phys'


class DestructibleEntity(BigWorld.Entity):

    @property
    def isPlayerTeam(self):
        return self.team == BigWorld.player().team

    def __init__(self):
        self.publicInfo = {'team': self.team}
        self.__stateTriggers = {'alive': self.isAlive,
         'destroyed': self.isDestroyed}
        self.targetCaps = [0]
        self.model = None
        self.__properties = destructible_entities.g_destructibleEntitiesCache.getDestructibleEntityType(self.typeID)
        self.__prereqs = None
        self.__destroyEffectsList = None
        self.__activeStateResource = None
        self.__prevDamageStickers = None
        self.__stateResources = {}
        for stateName, stateProperties in self.__properties.states.iteritems():
            self.__stateResources[stateName] = DestructibleEntityState(stateName, stateProperties, self.id, self.__stateTriggers[stateName])

        return

    def __checkStateTriggers(self):
        for state in self.__stateResources.itervalues():
            if state.isTriggered():
                self.__updateState(state.name)
                return

    def prerequisites(self):
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.addDestructibleEntity(self)
        prereqs = list()
        for stateResource in self.__stateResources.itervalues():
            prereqs += stateResource.prereqs(self.spaceID)

        return prereqs

    def onEnterWorld(self, prereqs):
        self.__setPickingEnabled(self.isActive)
        for stateResource in self.__stateResources.itervalues():
            stateResource.onResourcesLoaded(prereqs)

        self.__checkStateTriggers()
        self.__prevDamageStickers = frozenset()

    def onLeaveWorld(self):
        if self.__activeStateResource is not None:
            self.__activeStateResource.deactivate()
            self.__activeStateResource = None
        for stateResource in self.__stateResources.itervalues():
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

    def showDamageFromShot(self, points, effectsIndex):
        pass

    def showDamageFromExplosion(self, attackerID, center, effectsIndex, damageFactor):
        pass

    def set_health(self, oldValue):
        self.__checkStateTriggers()

    def set_isActive(self, oldValue):
        self.__setPickingEnabled(self.isActive)
        destructibleEntityComponent = BigWorld.player().arena.componentSystem.destructibleEntityComponent
        if destructibleEntityComponent is not None:
            destructibleEntityComponent.updateDestructibleEntityActiveState(self)
        return

    def set_damageStickers(self, prev=None):
        if not self.isAlive():
            return
        else:
            prev = self.__prevDamageStickers
            curr = frozenset(self.damageStickers)
            self.__prevDamageStickers = curr
            for sticker in prev.difference(curr):
                for damageStickers in self.__activeStateResource.damageStickers.itervalues():
                    damageStickers.delDamageSticker(sticker)

            for sticker in curr.difference(prev):
                hitCompIndx, stickerID, segStart, segEnd = DamageFromShotDecoder.decodeSegment(sticker, self.__activeStateResource.collisionComponent)
                if hitCompIndx is None:
                    return
                if hitCompIndx not in self.__activeStateResource.damageStickers:
                    LOG_ERROR('component is not available for damage sticker: ', hitCompIndx)
                    continue
                segStart, segEnd = self.__activeStateResource.reduceSegmentLength(hitCompIndx, segStart, segEnd)
                self.__activeStateResource.damageStickers[hitCompIndx].addDamageSticker(sticker, stickerID, segStart, segEnd)

            return

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
        BigWorld.wgAddEdgeDetectEntity(self, colorMode, 0, False, False)

    def removeEdge(self, forceSimpleEdge=False):
        if self.model:
            BigWorld.wgDelEdgeDetectEntity(self)

    def __setPickingEnabled(self, enable):
        self.targetCaps = [1] if enable else [0]


class DestructibleEntityState(object):
    guiNode = property(lambda self: self.__guiNode)
    damageStickers = property(lambda self: self.__damageStickers)
    collisionComponent = property(lambda self: self.__collisionComponent)
    name = property(lambda self: self.__stateName)

    def __init__(self, stateName, stateProperties, entityId, trigger):
        self.__entityId = entityId
        self.__stateName = stateName
        self.__stateProperties = stateProperties
        self.__guiNode = None
        self.__active = False
        self.__collisionComponent = None
        self.__visualModel = None
        self.__damageStickers = dict()
        self.__effectsPlayer = None
        self.__trigger = trigger
        return

    def isTriggered(self):
        return self.__trigger() and not self.__active

    def reduceSegmentLength(self, hitCompIndx, segStart, segEnd):
        hitDist = self.__collisionComponent.collideLocal(hitCompIndx, segStart, segEnd)
        if hitDist is None:
            return (segStart, segEnd)
        else:
            rayDir = Math.Vector3(segEnd) - Math.Vector3(segStart)
            rayDir.normalise()
            hitPoint = segStart + rayDir * hitDist
            return (hitPoint - rayDir / 2.0 * COLLISION_SEGMENT_LENGTH, hitPoint + rayDir / 2.0 * COLLISION_SEGMENT_LENGTH)

    def prereqs(self, spaceId):
        visualModel = BigWorld.CompoundAssembler(self.__stateName + ASSEMBLER_NAME_SUFFIXES.VISUAL, spaceId)
        bspModels = []
        for componentIdx, (componentId, component) in enumerate(self.__stateProperties.components.iteritems()):
            if componentIdx == 0:
                visualModel.addRootPart(component.visualModel, 'root')
            else:
                visualModel.emplacePart(component.visualModel, 'root', componentId)
            bspModels.append((componentIdx, component.physicsModel))

        collisionComponent = BigWorld.CollisionAssembler(tuple(bspModels), spaceId)
        collisionComponent.name = self.__stateName + ASSEMBLER_NAME_SUFFIXES.PHYSICS
        return [visualModel, collisionComponent]

    def onResourcesLoaded(self, prereqs):
        assemblerName = self.__stateName + ASSEMBLER_NAME_SUFFIXES.PHYSICS
        if assemblerName not in prereqs.failedIDs:
            self.__collisionComponent = prereqs[assemblerName]
        assemblerName = self.__stateName + ASSEMBLER_NAME_SUFFIXES.VISUAL
        if assemblerName not in prereqs.failedIDs:
            self.__visualModel = prereqs[assemblerName]
            for componentIdx, component in enumerate(self.__stateProperties.components.itervalues()):
                self.__visualModel.setPartProperties(componentIdx, int(component.destructible) << PART_PROPERTIES.HIGHLIGHTABLE)
                link = self.__visualModel.getPartGeometryLink(componentIdx)
                self.__damageStickers[componentIdx] = DestructibleStickers(link, self.__visualModel.node('root'))

            nodeName = next((comp.guiNode for comp in self.__stateProperties.components.itervalues() if comp.guiNode is not None), None)
            if nodeName is not None:
                self.__guiNode = self.__visualModel.node(nodeName)
        return

    def activate(self, matrix):
        payload = []
        for componentIdx, _ in enumerate(self.__stateProperties.components):
            payload.append((componentIdx, self.__visualModel.node('root')))

        self.__collisionComponent.connect(self.__entityId, ColliderTypes.VEHICLE_COLLIDER, tuple(payload))
        self.__collisionComponent.activate()
        self.__visualModel.matrix = matrix
        self.__playEffect(self.__stateProperties.effect, self.__visualModel)
        self.__active = True
        return self.__visualModel

    def deactivate(self):
        self.__collisionComponent.deactivate()
        self.__stopEffect()
        for componentIdx in range(len(self.__stateProperties.components)):
            self.__collisionComponent.removeAttachment(componentIdx)

        self.__active = False

    def destroy(self):
        self.__effectsPlayer = None
        self.__damageStickers = None
        self.__visualModel = None
        self.__collisionComponent = None
        self.__guiNode = None
        self.__stateProperties = None
        self.__stateName = None
        return

    def collideAllWorld(self, startPoint, endPoint):
        return self.__collisionComponent.collideAllWorld(startPoint, endPoint) if self.__collisionComponent is not None else None

    def __playEffect(self, effectName, model):
        if self.__effectsPlayer is not None or None in (model, effectName):
            return
        else:
            effectsSection = destructible_entities.g_destructibleEntitiesCache.getDestroyEffectList(effectName)
            if effectsSection is None:
                return
            effects = effectsFromSection(effectsSection)
            if effects is None:
                return
            fakeModel = helpers.newFakeModel()
            BigWorld.player().addModel(fakeModel)
            tmpMatrix = Math.Matrix(self.__visualModel.matrix)
            fakeModel.position = tmpMatrix.translation
            self.__effectsPlayer = EffectsListPlayer(effects.effectsList, effects.keyPoints)
            self.__effectsPlayer.play(fakeModel, None)
            return

    def __stopEffect(self):
        if self.__effectsPlayer is None:
            return
        else:
            self.__effectsPlayer.stop()
            self.__effectsPlayer = None
            return
