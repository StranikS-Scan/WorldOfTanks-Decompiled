# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AnimatedModelObject.py
import BigWorld
from svarog_script.script_game_object import ScriptGameObject
import AnimationSequence
from constants import QUEUE_TYPE
from skeletons.hb1 import ICustomizableObjectsManager
from helpers import dependency

class AnimatedModelObject(BigWorld.Entity, ScriptGameObject):
    customizableObjectManager = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID)
        self.__ssm = None
        return

    def prerequisites(self):
        ret = []
        if self.modelPath:
            ret.append(self.modelPath)
        return ret

    def onEnterWorld(self, prereqs):
        ScriptGameObject.activate(self)
        if self.modelPath not in prereqs.failedIDs:
            self.model = prereqs[self.modelPath]
            if self.stateMachinePath not in prereqs.failedIDs:
                self.__ssm = AnimationSequence.Loader(self.stateMachinePath, self.spaceID).loadSync()
                if self.__ssm:
                    self.__ssm.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
                    self.__ssm.start()
        if self.customizableObjectManager is not None:
            self.customizableObjectManager.onPrbEntityChanged += self.__onPrbEntityChanged
        return

    def onLeaveWorld(self):
        if self.customizableObjectManager is not None:
            self.customizableObjectManager.onPrbEntityChanged -= self.__onPrbEntityChanged
        ScriptGameObject.deactivate(self)
        ScriptGameObject.destroy(self)
        self.__ssm = None
        return

    def __onPrbEntityChanged(self, prbEntityType):
        if self.__ssm:
            self.__ssm.setBoolParam(self.stateMachineBoolParamName, prbEntityType != QUEUE_TYPE.EVENT_BATTLES)
