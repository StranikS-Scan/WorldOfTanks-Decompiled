# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearSelectableObject.py
from functools import partial
import BigWorld
from NewYearVisualObject import NewYearVisualObject
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from vehicle_systems.tankStructure import ColliderTypes
from svarog_script.py_component_system import ComponentSystem, ComponentDescriptor
from gui.shared.selectable_object import ISelectableObject
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents

class NewYearSelectableObject(NewYearVisualObject, ComponentSystem, ISelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)
    collisions = ComponentDescriptor()

    def __init__(self):
        NewYearVisualObject.__init__(self)
        ComponentSystem.__init__(self)
        ISelectableObject.__init__(self)
        self.__enabled = True
        self.__highlighted = False
        self.__outlineEntityId = None
        return

    def prerequisites(self):
        prereqs = super(NewYearSelectableObject, self).prerequisites()
        if not prereqs:
            return []
        if self.outlineModelName or self._isVisualOnly():
            return prereqs
        collisionModels = ((0, self.modelName),)
        collisionAssembler = BigWorld.CollisionAssembler(collisionModels, self.spaceID)
        prereqs.append(collisionAssembler)
        return prereqs

    def onEnterWorld(self, prereqs):
        if self._selfDestroyCheck():
            return
        super(NewYearSelectableObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        if prereqs.has_key('collisionAssembler'):
            self.collisions = prereqs['collisionAssembler']
            collisionData = ((0, self.model.matrix),)
            self.collisions.connect(self.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
            ComponentSystem.activate(self)
            g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        if self.outlineModelName:
            self.__outlineEntityId = self.createEntity(self.spaceID, self.matrix, {'modelName': self.outlineModelName,
             'edgeMode': self.edgeMode,
             'anchorName': self.anchorName}, entityType=NewYearSelectableObject.__name__)

    def onLeaveWorld(self):
        super(NewYearSelectableObject, self).onLeaveWorld()
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        self._nyController.onStateChanged -= self.__onStateChanged
        ComponentSystem.deactivate(self)
        ComponentSystem.destroy(self)
        self.setHighlight(False)

    def destroyOutlineEntity(self):
        if self.__outlineEntityId is None:
            return
        else:
            if not self.destroyEntity(self.__outlineEntityId):
                self.customizableObjectsMgr.pendingEntitiesToDestroy.add(self.__outlineEntityId)
            self.__outlineEntityId = None
            return

    @property
    def enabled(self):
        return self.__enabled

    def setEnable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.setHighlight(False)

    def setHighlight(self, show):
        if show:
            if not self.__highlighted and self.__enabled:
                BigWorld.wgAddEdgeDetectEntity(self, 3, self.edgeMode, False)
                self.__highlighted = True
        elif self.__highlighted:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__highlighted = False

    def onMouseClick(self):
        if self.anchorName:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
            NewYearNavigation.switchByAnchorName(self.anchorName)

    def _isVisualOnly(self):
        return not self.isSelectable

    def _selfDestroyCheck(self):
        if self.id not in self.customizableObjectsMgr.pendingEntitiesToDestroy:
            return False
        self.customizableObjectsMgr.pendingEntitiesToDestroy.remove(self.id)
        BigWorld.callback(0.0, partial(BigWorld.destroyEntity, self.id))
        return True

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())

    def __onCameraEntityUpdated(self, event):
        if not self._hangarSpace.spaceInited:
            return
        if not self.isSelectable:
            return
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if not self.__isHangarVehicleEntity(entityId):
            return
        if state == CameraMovementStates.FROM_OBJECT:
            if self.enabled:
                self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if not self.enabled and self._nyController.isEnabled():
                self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId
