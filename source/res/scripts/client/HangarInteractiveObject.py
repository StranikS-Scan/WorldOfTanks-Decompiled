# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarInteractiveObject.py
import BigWorld
import Math
import AnimationSequence
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class HangarInteractiveObject(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarInteractiveObject, self).__init__()
        self.__animator = None
        return

    def prerequisites(self):
        prereqs = super(HangarInteractiveObject, self).prerequisites()
        if not prereqs:
            return []
        if self.outlineModelName:
            assembler = BigWorld.CompoundAssembler('outline_model', self.spaceID)
            assembler.addRootPart(self.outlineModelName, 'root')
            prereqs.append(assembler)
        if self.animationSequence:
            prereqs.append(AnimationSequence.Loader(self.animationSequence, self.spaceID))
        return prereqs

    @property
    def isShowTooltip(self):
        return bool(self.selectionId)

    def onEnterWorld(self, prereqs):
        super(HangarInteractiveObject, self).onEnterWorld(prereqs)
        if self.outlineModelName:
            compoundModel = prereqs['outline_model']
            compoundModel.matrix = self.matrix
            self.addModel(compoundModel)
        if not self.animationSequence or self.animationSequence in prereqs.failedIDs:
            return
        self.__animator = prereqs[self.animationSequence]
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        self.__animator.start()

    def onLeaveWorld(self):
        super(HangarInteractiveObject, self).onLeaveWorld()
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        return

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        if self.boundingSphereSize:
            collisionModels = ((0, self.modelName, self.boundingSphereSize),)
            return collisionModels
        return super(HangarInteractiveObject, self)._getCollisionModelsPrereqs()

    def _getCollisionDataMatrix(self):
        matrix = super(HangarInteractiveObject, self)._getCollisionDataMatrix()
        if self.boundingSphereSize:
            offset = Math.Matrix()
            offset.translation = self.boundingSphereOffset
            result = Math.MatrixProduct()
            result.a = matrix
            result.b = offset
            return result
        return matrix

    def _addEdgeDetect(self):
        if self.outlineModelName and self.models:
            compoundModel = self.models[0]
            BigWorld.wgAddEdgeDetectCompoundModel(compoundModel, 0, self.edgeMode)
        else:
            super(HangarInteractiveObject, self)._addEdgeDetect()

    def _delEdgeDetect(self):
        if self.outlineModelName and self.models:
            compoundModel = self.models[0]
            BigWorld.wgDelEdgeDetectCompoundModel(compoundModel)
        else:
            super(HangarInteractiveObject, self)._delEdgeDetect()
