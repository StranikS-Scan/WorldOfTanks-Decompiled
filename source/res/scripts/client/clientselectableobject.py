# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import SoundGroups
from vehicle_systems.tankStructure import ColliderTypes
from svarog_script.py_component_system import ComponentSystem, ComponentDescriptor

class ClientSelectableObject(BigWorld.Entity, ComponentSystem):
    collisions = ComponentDescriptor()

    @property
    def enabled(self):
        return self.__enabled

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ComponentSystem.__init__(self)
        self.__enabled = True
        self.__edged = False
        self.__clickSound = None
        self.model = None
        return

    def prerequisites(self):
        if self.modelName != '':
            bspModels = ((0, self.modelName),)
            collisionAssembler = BigWorld.CollisionAssembler(bspModels, self.spaceID)
            return [self.modelName, collisionAssembler]
        return []

    def onEnterWorld(self, prereqs):
        if self.modelName == '':
            return
        if self.modelName not in prereqs.failedIDs:
            model = prereqs[self.modelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            self.model.addMotor(BigWorld.Servo(self.matrix))
            self.collisions = prereqs['collisionAssembler']
            collisionData = ((0, self.model.matrix),)
            self.collisions.connect(self.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
        ComponentSystem.activate(self)

    def onLeaveWorld(self):
        ComponentSystem.deactivate(self)
        ComponentSystem.destroy(self)
        if self.__clickSound is not None:
            if self.__clickSound.isPlaying:
                self.__clickSound.stop()
            self.__clickSound.releaseMatrix()
            self.__clickSound = None
        self.highlight(False)
        return

    def enable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.highlight(False)

    def highlight(self, show):
        if show:
            if not self.__edged and self.__enabled:
                BigWorld.wgAddEdgeDetectEntity(self, 0, self.edgeMode, False)
                self.__edged = True
        elif self.__edged:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__edged = False

    def onClicked(self):
        if self.__clickSound is None:
            if self.clickSoundName:
                self.__clickSound = SoundGroups.g_instance.getSound3D(self.model.root, self.clickSoundName)
                self.__clickSound.play()
        elif self.__clickSound.isPlaying:
            self.__clickSound.stop()
        else:
            self.__clickSound.play()
        return

    def _getModelHeight(self):
        return self.model.height
