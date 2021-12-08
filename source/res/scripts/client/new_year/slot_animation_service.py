# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/slot_animation_service.py
import logging
import BigWorld
import Math
import AnimationSequence
from helpers import dependency
from new_year.ny_constants import ANCHOR_TO_OBJECT
from skeletons.new_year import INewYearController
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class SlotAnimation(object):

    def __init__(self, matrix, spaceID, path):
        self.__animator = None
        self.__loadAnimationSequence(path, matrix, spaceID)
        return

    def startAnimation(self):
        if self.__animator is None:
            return
        else:
            self.__animator.setEnabled(True)
            self.__animator.start()
            return

    def stopAnimation(self):
        if self.__animator is None:
            return
        else:
            self.__animator.stop()
            self.__animator.setEnabled(False)
            return

    def clear(self):
        self.stopAnimation()
        self.__animator = None
        return

    def __loadAnimationSequence(self, resourceName, matrix, spaceID):
        loader = AnimationSequence.Loader(resourceName, spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimationLoaded, resourceName, matrix))

    def __onAnimationLoaded(self, resourceName, matrix, resourceList):
        self.__animator = resourceList[resourceName]
        self.__animator.bindToWorld(matrix)


class SlotAnimationService(object):
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__animations',)

    def __init__(self):
        self.__animations = {}

    def fini(self):
        self.__clearAnimations()

    def addEntitySlots(self, entity):
        objName = ANCHOR_TO_OBJECT[entity.anchorName]
        slotsDescrs = self.__nyController.getSlotDescrs(objName)
        for descr in slotsDescrs:
            for nodeName in descr.nodes.split():
                try:
                    mNode = entity.model.node(nodeName)
                except ValueError:
                    _logger.error('Could not find hardpoint "%s" into model "%s"', nodeName, entity.model.sources)
                    continue

                nodeWorldTransform = Math.Matrix(entity.matrix)
                nodeWorldTransform.preMultiply(mNode.initialLocalMatrix)
                if not descr.hoverEffect:
                    _logger.error('No slot animation effect for %s, id: %d', descr.type, descr.id)
                    continue
                animation = SlotAnimation(nodeWorldTransform, entity.spaceID, descr.hoverEffect)
                self.__animations.setdefault(descr.id, []).append(animation)

    def changeState(self, slot, isEnabled):
        if slot.id not in self.__animations:
            return
        for animation in self.__animations[slot.id]:
            if isEnabled:
                animation.startAnimation()
            animation.stopAnimation()

    def __clearAnimations(self):
        for animationsById in self.__animations.itervalues():
            for animation in animationsById:
                animation.clear()

        self.__animations.clear()
