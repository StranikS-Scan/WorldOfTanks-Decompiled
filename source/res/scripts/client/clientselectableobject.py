# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
from __future__ import absolute_import
import BigWorld
import SoundGroups
from vehicle_systems.tankStructure import ColliderTypes
from cgf_obsolete_script.script_game_object import ScriptGameObject, ComponentDescriptor
from hangar_selectable_objects import ISelectableObject

class ClientSelectableObject(BigWorld.Entity, ScriptGameObject, ISelectableObject):
    collisions = ComponentDescriptor()

    @property
    def enabled(self):
        return self.__enabled

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID, 'ClientSelectableObject')
        ISelectableObject.__init__(self)
        self.__enabled = True
        self.__edged = False
        self.model = None
        return

    def prerequisites(self):
        if not self.modelName:
            return []
        collisionModels = self._getCollisionModelsPrereqs()
        collisionAssembler = BigWorld.CollisionAssembler(collisionModels, self.spaceID)
        return [self.modelName, collisionAssembler]

    def onEnterWorld(self, prereqs):
        if not self.modelName:
            return
        if self.modelName not in prereqs.failedIDs:
            model = prereqs[self.modelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            self.model.addMotor(BigWorld.Servo(self.matrix))
            self.collisions = self.createComponent(BigWorld.CollisionComponent, prereqs['collisionAssembler'])
            collisionData = ((0, self.model.matrix),)
            self.collisions.connect(self.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
        ScriptGameObject.activate(self)

    def onLeaveWorld(self):
        ScriptGameObject.deactivate(self)
        ScriptGameObject.destroy(self)
        self.setHighlight(False)

    def setEnable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.setHighlight(False)

    def setHighlight(self, show):
        if show:
            if not self.__edged and self.__enabled:
                self._addEdgeDetect()
                self.__edged = True
        elif self.__edged:
            self._delEdgeDetect()
            self.__edged = False

    def onMouseDown(self):
        pass

    def onMouseUp(self):
        pass

    def onMouseClick(self):
        if self.clickSoundName and self.__enabled:
            if self.isClick3DSound:
                SoundGroups.g_instance.playSoundPos(self.clickSoundName, self.model.position)
            else:
                SoundGroups.g_instance.playSound2D(self.clickSoundName)

    def _getModelHeight(self):
        return self.model.height

    def _getCollisionModelsPrereqs(self):
        collisionModels = ((0, self.modelName),)
        return collisionModels

    def _addEdgeDetect(self):
        BigWorld.wgAddEdgeDetectEntity(self, None, 0, False, self.edgeMode, False)
        return

    def _delEdgeDetect(self):
        BigWorld.wgDelEdgeDetectEntity(self)
