# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hover_component.py
import BigWorld
import CGF
import GUI
import Event
from GenericComponents import VSEComponent
from Physics import CameraCollideComponent
from cgf_common.cgf_helpers import getParentGameObjectByComponent
from cgf_script.managers_registrator import tickGroup, onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from constants import IS_CLIENT, CollisionFlags
from vehicle_systems.tankStructure import ColliderTypes
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
if IS_CLIENT:
    from AvatarInputHandler import cameras

@registerComponent
class SelectionComponent(object):
    editorTitle = 'Selection'
    category = 'Common'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    highlight = ComponentProperty(type=CGFMetaTypes.BOOL, value=True, editorName='highlight')

    def __init__(self):
        super(SelectionComponent, self).__init__()
        self.onClickAction = Event.Event()


@registerComponent
class IsHoveredComponent(object):
    domain = CGF.DomainOption.DomainClient


@registerComponent
class HoverGroupTrackerComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hover group tracker'
    category = 'Common'

    def __init__(self):
        super(HoverGroupTrackerComponent, self).__init__()
        self.__hoveredGOs = set()

    def addHoveredGO(self, gameObject):
        self.__hoveredGOs.add(gameObject.id)
        root = getParentGameObjectByComponent(gameObject, HoverGroupTrackerComponent)
        if root and not root.findComponentByType(IsHoveredComponent):
            root.createComponent(IsHoveredComponent)

    def removeHoveredGO(self, gameObject):
        self.__hoveredGOs.discard(gameObject.id)
        if self.__hoveredGOs:
            return
        root = getParentGameObjectByComponent(gameObject, HoverGroupTrackerComponent)
        if root and root.findComponentByType(IsHoveredComponent):
            root.removeComponentByType(IsHoveredComponent)


class HoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _hoveredQuery = CGF.QueryConfig(CGF.GameObject, IsHoveredComponent, CGF.No(HoverGroupTrackerComponent))

    @onAddedQuery(VSEComponent, IsHoveredComponent)
    def onIsHoveredAdded(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverIn()

    @onRemovedQuery(VSEComponent, IsHoveredComponent)
    def onIsHoveredRemoved(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverOut()

    @onRemovedQuery(CGF.GameObject, SelectionComponent)
    def onIsSelectableRemoved(self, gameObject, *args):
        if gameObject.findComponentByType(IsHoveredComponent):
            gameObject.removeComponentByType(IsHoveredComponent)

    @tickGroup(groupName='Simulation')
    def tick(self):
        hoveredGameObject = None
        if GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isSelectionEnabled and self._hangarSpace.isCursorOver3DScene:
            hoveredGameObject = self.__getGameObjectUnderCursor()
        if hoveredGameObject and hoveredGameObject.findComponentByType(IsHoveredComponent):
            return
        else:
            for gameObject, _ in self._hoveredQuery:
                gameObject.removeComponentByType(IsHoveredComponent)

            if hoveredGameObject and hoveredGameObject.findComponentByType(SelectionComponent):
                hoveredGameObject.createComponent(IsHoveredComponent)
            return

    def __getGameObjectUnderCursor(self):
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        skipFlags = CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE | CollisionFlags.TRIANGLE_NOCOLLIDE
        res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1500, skipFlags, -1, -1, ColliderTypes.HANGAR_FLAG)
        if res is not None and res[5] and res[5].isValid():
            gameObject = res[5]
            cameraCollideComponent = gameObject.findComponentByType(CameraCollideComponent)
            if cameraCollideComponent and cameraCollideComponent.isColliding:
                return
            return gameObject
        else:
            return
