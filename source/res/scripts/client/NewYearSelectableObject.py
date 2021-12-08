# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearSelectableObject.py
from functools import partial
import BigWorld
from entity_constants import HighlightColors
from NewYearVisualObject import NewYearVisualObject
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from cgf_obsolete_script.script_game_object import ComponentDescriptor, ScriptGameObject
from uilogging.ny.mixins import SelectableObjectLoggerMixin
from vehicle_systems.tankStructure import ColliderTypes
from hangar_selectable_objects import ISelectableObject
from skeletons.gui.shared.utils import IHangarSpace
from new_year.cgf_components.highlight_manager import HighlightComponent, HighlightGroupComponent
from new_year.cgf_components.other_entity_manager import OtherEntityComponent
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates

class NewYearSelectableObject(NewYearVisualObject, ScriptGameObject, ISelectableObject, SelectableObjectLoggerMixin):
    collisions = ComponentDescriptor()
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _nyController = dependency.descriptor(INewYearController)
    __customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _HIGHLIGHT_COLOR = HighlightColors.BLUE

    def __init__(self):
        NewYearVisualObject.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID)
        ISelectableObject.__init__(self)
        self.__enabled = True

    def prerequisites(self):
        prereqs = super(NewYearSelectableObject, self).prerequisites()
        if not self.outlineModelName:
            collisionModels = ((0, self.modelName),)
            collisionAssembler = BigWorld.CollisionAssembler(collisionModels, self.spaceID)
            prereqs.append(collisionAssembler)
        return prereqs

    def onEnterWorld(self, prereqs):
        if self._selfDestroyCheck():
            return
        super(NewYearSelectableObject, self).onEnterWorld(prereqs)
        if prereqs.has_key('collisionAssembler'):
            self.collisions = self.createComponent(BigWorld.CollisionComponent, prereqs['collisionAssembler'])
            collisionData = ((0, self.matrix),)
            self.collisions.connect(self.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
            ScriptGameObject.activate(self)
        if self.outlineModelName:
            state = {'modelName': self.outlineModelName,
             'edgeMode': self.edgeMode,
             'anchorName': self.anchorName,
             'selectionGroupIdx': self.selectionGroupIdx}
            self.entityGameObject.createComponent(OtherEntityComponent, state, NewYearSelectableObject)
        if self.enabled:
            self.__addHighlightComponent()
        if self.selectionGroupIdx:
            self.entityGameObject.createComponent(HighlightGroupComponent, self.selectionGroupIdx)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()

    def onLeaveWorld(self):
        super(NewYearSelectableObject, self).onLeaveWorld()
        self.__removeHighlightComponent()
        self.entityGameObject.removeComponentByType(OtherEntityComponent)
        self.entityGameObject.removeComponentByType(HighlightGroupComponent)
        self._nyController.onStateChanged -= self.__onStateChanged
        ScriptGameObject.deactivate(self)
        ScriptGameObject.destroy(self)

    @property
    def enabled(self):
        return self.__enabled

    def setEnable(self, enabled):
        if self.__enabled and not enabled:
            self.__removeHighlightComponent()
        elif enabled and not self.__enabled:
            self.__addHighlightComponent()
        self.__enabled = enabled

    def onMouseClick(self):
        anchorName = self.anchorName
        if self.enabled and anchorName and anchorName != self.__customizableObjectsMgr.getCurrentCameraAnchor():
            self.logClick(anchorName)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
            NewYearNavigation.switchByAnchorName(anchorName)
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    cameraObject.onDeselect(None)

        return

    def _selfDestroyCheck(self):
        if self.id not in self.__customizableObjectsMgr.pendingEntitiesToDestroy:
            return False
        self.__customizableObjectsMgr.pendingEntitiesToDestroy.remove(self.id)
        BigWorld.callback(0.0, partial(BigWorld.destroyEntity, self.id))
        return True

    def __addHighlightComponent(self):
        if self.isSelectable:
            self.entityGameObject.createComponent(HighlightComponent, self, self._HIGHLIGHT_COLOR, self.edgeMode, disableDepthTest=True)

    def __removeHighlightComponent(self):
        self.entityGameObject.removeComponentByType(HighlightComponent)

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())
