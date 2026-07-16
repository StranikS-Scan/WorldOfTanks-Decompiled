# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleEntityState.py
from __future__ import absolute_import
from future.utils import viewitems, viewvalues
import typing
import BigWorld
import CGF
import GenericComponents
import Math
import destructible_entities
import helpers
from DestructibleStickers import DestructibleStickers
from cgf_client_common.game_object_holder import GameObjectHolder
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from vehicle_systems.tankStructure import ColliderTypes
COLLISION_SEGMENT_LENGTH = 2

class ASSEMBLER_NAME_SUFFIXES(object):
    VISUAL = '_vis'
    PHYSICS = '_phys'


class PART_PROPERTIES(object):
    HIGHLIGHTABLE = 0
    HIGHLIGHTBYVISUAL = 2


class DestructibleEntityState(GameObjectHolder):
    guiNode = property(lambda self: self.__guiNode)
    damageStickers = property(lambda self: self.__damageStickers)
    name = property(lambda self: self.__stateName)

    class DestructibleEntityStateComponent(object):

        def __init__(self, state):
            self.state = state

    def __init__(self, stateName, stateProperties, entityId, trigger, spaceID):
        super(DestructibleEntityState, self).__init__(spaceID, 'DestructibleEntityState')
        self.__entityId = entityId
        self.__stateName = stateName
        self.__stateProperties = stateProperties
        self.__guiNode = None
        self.__active = False
        self.__visualModel = None
        self.__damageStickers = {}
        self.__gameObjects = {}
        self.__effectsPlayer = None
        self.__trigger = trigger
        self.collisionComponent = CGF.ComponentLink(self._gameObject, BigWorld.CollisionComponent)
        return

    def isTriggered(self):
        return self.__trigger() and not self.__active

    def reduceSegmentLength(self, hitCompIndx, segStart, segEnd):
        hitDist, _, _, _ = self.collisionComponent.collideLocal(hitCompIndx, segStart, segEnd)
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
        for componentIdx, (componentId, component) in enumerate(viewitems(self.__stateProperties.components)):
            if componentIdx == 0:
                visualModel.addRootPart(component.visualModel, 'root')
            else:
                visualModel.emplacePart(component.visualModel, 'root', componentId)
            bspModels.append((componentIdx, component.physicsModel))

        collisionAssembler = BigWorld.CollisionAssembler(tuple(bspModels), self._spaceID)
        collisionAssembler.name = self.__stateName + ASSEMBLER_NAME_SUFFIXES.PHYSICS
        return [visualModel, collisionAssembler]

    def onResourcesLoaded(self, prereqs):
        cgfQueue = CGF.CommandQueue(self._spaceID)
        assemblerName = self.__stateName + ASSEMBLER_NAME_SUFFIXES.PHYSICS
        if assemblerName not in prereqs.failedIDs:
            cgfQueue.createComponent(self._gameObject, BigWorld.CollisionComponent, self._spaceID, prereqs[assemblerName])
        selfComponent = self.DestructibleEntityStateComponent(self)
        cgfQueue.assignComponent(self._gameObject, selfComponent)
        cgfQueue.createComponent(self._gameObject, CGF.TransformComponent)
        assemblerName = self.__stateName + ASSEMBLER_NAME_SUFFIXES.VISUAL
        if assemblerName not in prereqs.failedIDs:
            self.__visualModel = prereqs[assemblerName]
            for componentIdx, component in enumerate(viewvalues(self.__stateProperties.components)):
                self.__visualModel.setPartProperties(componentIdx, int(component.destructible) << PART_PROPERTIES.HIGHLIGHTABLE | PART_PROPERTIES.HIGHLIGHTBYVISUAL)
                fashion = BigWorld.WGVehicleFashion()
                self.__visualModel.setupPartFashion(componentIdx, fashion)
                self.__gameObjects[componentIdx] = go = cgfQueue.createGameObject()
                cgfQueue.createComponent(go, CGF.TransformComponent, Math.Matrix())
                cgfQueue.createComponent(go, CGF.HierarchyComponent, self._gameObject)
                cgfQueue.createComponent(go, GenericComponents.DynamicModelComponent, self.__visualModel)
                cgfQueue.createComponent(go, GenericComponents.FashionComponent, fashion, componentIdx)
                self.__damageStickers[componentIdx] = DestructibleStickers(self._spaceID, self.__visualModel, componentIdx, go)

            nodeName = next((comp.guiNode for comp in viewvalues(self.__stateProperties.components) if comp.guiNode is not None), None)
            if nodeName is not None:
                self.__guiNode = self.__visualModel.node(nodeName)
        return

    def setParent(self, parent):
        cgfQueue = CGF.CommandQueue(self._spaceID)
        cgfQueue.createComponent(self._gameObject, CGF.HierarchyComponent, parent)

    def activate(self, matrix):
        self.__visualModel.matrix = matrix
        self.__playEffect(self.__stateProperties.effect, self.__visualModel)
        self.__active = True
        self._gameObject.activate()
        return self.__visualModel

    def onActivate(self, collisionComponent):
        payload = []
        for componentIdx, _ in enumerate(self.__stateProperties.components):
            payload.append((componentIdx, self.__visualModel.node('root')))

        collisionComponent.connect(self.__entityId, ColliderTypes.VEHICLE_COLLIDER, tuple(payload))

    def deactivate(self):
        for componentIdx in range(len(self.__stateProperties.components)):
            self.collisionComponent.removeAttachment(componentIdx)

        self._gameObject.deactivate()
        self.__stopEffect()
        self.__active = False

    def destroy(self):
        self._gameObject.destroy()
        self.__effectsPlayer = None
        for damageSticker in viewvalues(self.__damageStickers):
            damageSticker.destroy()

        self.__damageStickers = {}
        self.__gameObjects = {}
        self.__visualModel = None
        self.__guiNode = None
        self.__stateProperties = None
        self.__stateName = None
        return

    def collideAllWorld(self, startPoint, endPoint):
        return self.collisionComponent.collideAllWorld(startPoint, endPoint) if self.collisionComponent else None

    def isDestructibleComponent(self, componentID):
        component = next((c for cIDx, c in enumerate(viewvalues(self.__stateProperties.components)) if cIDx == componentID), None)
        return component.destructible if component is not None else False

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


class DestructibleEntityStatesSystem(CGF.System):
    Activate = CGF.ActivateReaction(CGF.ReactRo(DestructibleEntityState.DestructibleEntityStateComponent), CGF.Rw(BigWorld.CollisionComponent))
    Reactions = CGF.Reactions(Activate)

    def update(self):
        for destructibleEntity, collision in self.reaction(self.Activate):
            destructibleEntity.state.onActivate(collision)
