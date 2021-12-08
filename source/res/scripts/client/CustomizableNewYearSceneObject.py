# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomizableNewYearSceneObject.py
import logging
import Math
import CGF
from GenericComponents import TransformComponent
from helpers import dependency
from NewYearSelectableObject import NewYearSelectableObject
from items.new_year import g_cache
from NewYearToyObject import NewYearToyObject
from new_year.cgf_components.other_entity_manager import OtherEntityComponent
from skeletons.new_year import ICustomizableObjectsManager
_logger = logging.getLogger(__name__)

class CustomizableNewYearSceneObject(NewYearSelectableObject):
    __customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        self.__placedToys = {}
        super(CustomizableNewYearSceneObject, self).__init__()

    def onEnterWorld(self, prereqs):
        super(CustomizableNewYearSceneObject, self).onEnterWorld(prereqs)
        self.__customizableObjectsMgr.addCustomizableEntity(self)

    def onLeaveWorld(self):
        self.__customizableObjectsMgr.removeCustomizableEntity(self)
        self.__clearToys()
        super(CustomizableNewYearSceneObject, self).onLeaveWorld()

    def updateNode(self, nodeName, nodeDesc):
        if nodeDesc:
            self.__placeToy(nodeName, nodeDesc)
        else:
            self.__removeToy(nodeName)

    def clearToys(self):
        self.__clearToys()

    def __clearToys(self):
        for node, toy in self.__placedToys.iteritems():
            self.__removeToy(node, toy=toy)

        self.__placedToys.clear()

    def __removeToy(self, nodeName, toy=None):
        if toy is None:
            toy = self.__placedToys.pop(nodeName, None)
        if toy:
            toy.deactivate()
            toy.destroy()
        return

    def __placeToy(self, nodeName, nodeDesc):
        self.__removeToy(nodeName)
        if nodeDesc is None:
            return
        else:
            try:
                mNode = self.model.node(nodeName)
            except ValueError:
                _logger.error('Could not find hardpoint "%s" into model "%s"', nodeName, self.modelName)
                return

            nodeWorldTransform = Math.Matrix(self.matrix)
            nodeWorldTransform.preMultiply(mNode.initialLocalMatrix)
            localTransformMatrix = self._getLocalTransformMatrix(nodeName, nodeDesc.modelName)
            if localTransformMatrix is not None:
                nodeWorldTransform.preMultiply(localTransformMatrix)
            toyEntityProps = {'modelName': nodeDesc.modelName,
             'outlineModelName': nodeDesc.outlineModelName,
             'edgeMode': self.edgeMode,
             'anchorName': self.anchorName,
             'selectionGroupIdx': self.selectionGroupIdx,
             'isSelectable': nodeDesc.isSelectable and not nodeDesc.outlineModelName,
             'hangingEffectName': nodeDesc.hangingEffectName,
             'regularEffectName': nodeDesc.regularEffectName,
             'animationSequence': nodeDesc.animationSequence,
             'hangingAnimationSequence': nodeDesc.hangingAnimationSequence,
             'appearanceDelay': nodeDesc.appearanceDelay}
            toyModelOverride = self._getModelOverride(nodeName, nodeDesc.modelName)
            if toyModelOverride is not None:
                toyEntityProps.update(toyModelOverride.getUpdateDict())
            toy = CGF.GameObject(self.spaceID)
            toy.createComponent(TransformComponent, nodeWorldTransform)
            toy.createComponent(OtherEntityComponent, toyEntityProps, NewYearToyObject)
            toy.activate()
            self.__placedToys[nodeName] = toy
            return

    def _getLocalTransformMatrix(self, nodeName, modelName):
        modelTransformation = self._getModelTransformation(nodeName, modelName)
        return modelTransformation.transform if modelTransformation is not None and modelTransformation.transform else None

    def _getModelOverride(self, nodeName, modelName):
        modelTransformation = self._getModelTransformation(nodeName, modelName)
        return modelTransformation.modelOverride if modelTransformation is not None and modelTransformation.modelOverride else None

    def _getModelTransformation(self, nodeName, modelName):
        nodeKey = (self.anchorName, nodeName)
        return g_cache.toysTransformations[modelName][nodeKey] if modelName in g_cache.toysTransformations and nodeKey in g_cache.toysTransformations[modelName] else None
