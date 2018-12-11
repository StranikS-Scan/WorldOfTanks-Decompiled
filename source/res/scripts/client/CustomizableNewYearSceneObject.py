# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomizableNewYearSceneObject.py
import logging
import Math
from NewYearSelectableObject import NewYearSelectableObject
from new_year.ny_toy import NewYearToy
_logger = logging.getLogger(__name__)

class CustomizableNewYearSceneObject(NewYearSelectableObject):

    def __init__(self):
        self.__placedToys = {}
        super(CustomizableNewYearSceneObject, self).__init__()

    def onEnterWorld(self, prereqs):
        super(CustomizableNewYearSceneObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addCustomizableEntity(self)

    def onLeaveWorld(self):
        self.customizableObjectsMgr.removeCustomizableEntity(self)
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
            if not toy.destroy():
                self.customizableObjectsMgr.pendingEntitiesToDestroy.add(toy.entityID)
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
            toyEntityProps = {'modelName': nodeDesc.modelName,
             'outlineModelName': nodeDesc.outlineModelName,
             'edgeMode': self.edgeMode,
             'anchorName': self.anchorName,
             'isSelectable': nodeDesc.isSelectable,
             'hangingEffectName': nodeDesc.hangingEffectName,
             'regularEffectName': nodeDesc.regularEffectName,
             'animationSequence': nodeDesc.animationSequence,
             'appearanceDelay': nodeDesc.appearanceDelay}
            toy = NewYearToy(nodeWorldTransform, toyEntityProps, self.spaceID)
            self.__placedToys[nodeName] = toy
            return
