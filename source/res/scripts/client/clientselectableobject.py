# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import SoundGroups
from entity_constants import HighlightColors
from vehicle_systems.tankStructure import ColliderTypes
from cgf_obsolete_script.script_game_object import ScriptGameObject, ComponentDescriptor
from hangar_selectable_objects import ISelectableObject
from new_year.cgf_components.highlight_manager import HighlightComponent

class ClientSelectableObject(BigWorld.Entity, ScriptGameObject, ISelectableObject):
    collisions = ComponentDescriptor()
    _HIGHLIGHT_COLOR = HighlightColors.YELLOW

    @property
    def enabled(self):
        return self.__enabled

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID, 'ClientSelectableObject')
        ISelectableObject.__init__(self)
        self.__enabled = True
        self.__edged = False
        self.__clickSound = None
        self.model = None
        return

    def prerequisites(self):
        if not self.modelName:
            return []
        collisionModels = self._getCollisionModelsPrereqs()
        collisionAssembler = BigWorld.CollisionAssembler(collisionModels, self.spaceID)
        return [self.modelName, collisionAssembler]

    def onEnterWorld(self, prereqs):
        if self.enabled:
            self._addHighlightComponent()
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
        self.__removeHighlightComponent()
        if self.__clickSound is not None:
            if self.__clickSound.isPlaying:
                self.__clickSound.stop()
            self.__clickSound.releaseMatrix()
            self.__clickSound = None
        return

    def setEnable(self, enabled):
        if self.__enabled and not enabled:
            self.__removeHighlightComponent()
        elif enabled and not self.__enabled:
            self._addHighlightComponent()
        self.__enabled = enabled

    def onMouseClick(self):
        if self.__clickSound is None:
            if self.clickSoundName and self.__enabled:
                if self.isClick3DSound:
                    self.__clickSound = SoundGroups.g_instance.getSound3D(self.model.root, self.clickSoundName)
                else:
                    self.__clickSound = SoundGroups.g_instance.getSound2D(self.clickSoundName)
                self.__clickSound.play()
        elif self.__clickSound.isPlaying:
            self.__clickSound.stop()
        else:
            self.__clickSound.play()
        return

    def _getModelHeight(self):
        return self.model.height

    def _getCollisionModelsPrereqs(self):
        collisionModels = ((0, self.modelName),)
        return collisionModels

    def _addHighlightComponent(self):
        self.entityGameObject.createComponent(HighlightComponent, self, self._HIGHLIGHT_COLOR, self.edgeMode)

    def __removeHighlightComponent(self):
        self.entityGameObject.removeComponentByType(HighlightComponent)
