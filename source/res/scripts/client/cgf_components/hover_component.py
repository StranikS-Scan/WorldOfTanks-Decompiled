# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hover_component.py
from __future__ import absolute_import
import BigWorld
import CGF
import GUI
import Event
from GenericComponents import VSEComponent
from Physics import CameraCollideComponent
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT, CollisionFlags
from vehicle_systems.tankStructure import ColliderTypes
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
if IS_CLIENT:
    from AvatarInputHandler import cameras

@registerComponent
class SelectionComponent(object):
    group = 'Common'
    editorTitle = 'Selection'
    domain = CGF.Domain.ClientEditor
    highlight = ComponentProperty(type=CGF.PropertyType.Bool, value=True, editorName='highlight')

    def __init__(self):
        super(SelectionComponent, self).__init__()
        self.onClickAction = Event.Event()


@registerComponent
class IsHoveredComponent(object):
    editorTitle = 'Is Hovered'
    domain = CGF.Domain.Client


@registerComponent
class HoverGroupTrackerComponent(object):
    group = 'Common'
    editorTitle = 'Hover group tracker'
    domain = CGF.Domain.ClientEditor

    def __init__(self):
        super(HoverGroupTrackerComponent, self).__init__()
        self.__hoveredGOs = set()

    def addHoveredGO(self, gameObject):
        self.__hoveredGOs.add(gameObject.id)
        root, _ = CGF.findParentWithComponent(gameObject, HoverGroupTrackerComponent)
        if root and not root.hasComponent(IsHoveredComponent):
            queue = CGF.CommandQueue(root.spaceID)
            queue.createComponent(root, IsHoveredComponent)

    def removeHoveredGO(self, gameObject):
        self.__hoveredGOs.discard(gameObject.id)
        if self.__hoveredGOs:
            return
        root, _ = CGF.findParentWithComponent(gameObject, HoverGroupTrackerComponent)
        if root and root.hasComponent(IsHoveredComponent):
            root.removeComponent(IsHoveredComponent)


class HoverSystem(CGF.System):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    HoveredActivated = CGF.ActivateReaction(VSEComponent, CGF.ReactRo(IsHoveredComponent))
    HoveredDeactivated = CGF.DeactivateReaction(VSEComponent, CGF.ReactRo(IsHoveredComponent))
    SelectionDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(SelectionComponent))
    HoverIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(IsHoveredComponent), CGF.No(HoverGroupTrackerComponent))
    HoverAccess = CGF.AccessReaction(CGF.Ro(IsHoveredComponent))
    SelectionAccess = CGF.AccessReaction(CGF.Ro(SelectionComponent))
    CameraCollideAccess = CGF.AccessReaction(CGF.Ro(CameraCollideComponent))
    Reactions = CGF.Reactions(HoveredActivated, HoveredDeactivated, SelectionDeactivated, HoverIterate, HoverAccess, SelectionAccess, CameraCollideAccess)
    _MAX_PICK_RAY_LEN = 1500.0

    def __init__(self):
        super(HoverSystem, self).__init__()
        self.__lastCursorPos = None
        self.__lastCursorActive = False
        return

    def update(self):
        q = CGF.CommandQueue(self.gom)
        hoverAccess = self.reaction(self.HoverAccess)
        hoverStateChanged = False
        for go, _ in self.reaction(self.SelectionDeactivated):
            self.onIsSelectableRemoved(go, hoverAccess, q)
            hoverStateChanged = True

        for vseComponent, _ in self.reaction(self.HoveredDeactivated):
            self.onIsHoveredRemoved(vseComponent)
            hoverStateChanged = True

        for vseComponent, _ in self.reaction(self.HoveredActivated):
            self.onIsHoveredAdded(vseComponent)
            hoverStateChanged = True

        self.tick(q, hoverAccess, hoverStateChanged)

    def onIsHoveredAdded(self, vseComponent):
        vseComponent.context.onGameObjectHoverIn()

    def onIsHoveredRemoved(self, vseComponent):
        vseComponent.context.onGameObjectHoverOut()

    def onIsSelectableRemoved(self, gameObject, hoverAccess, queue):
        if hoverAccess.find(gameObject):
            queue.removeComponent(gameObject, IsHoveredComponent)

    def tick(self, queue, hoverAccess, hoverStateChanged):
        cursor = GUI.mcursor()
        cursorPos = cursor.position
        cursorActive = cursor.inWindow and cursor.inFocus and self._hangarSpace.isSelectionEnabled and self._hangarSpace.isCursorOver3DScene
        if not hoverStateChanged and cursorActive == self.__lastCursorActive and cursorPos == self.__lastCursorPos:
            return
        else:
            self.__lastCursorActive = cursorActive
            self.__lastCursorPos = cursorPos
            hoveredGameObject = self.__getGameObjectUnderCursor() if cursorActive else None
            if hoveredGameObject and hoverAccess.find(hoveredGameObject):
                return
            for gameObject, _ in self.reaction(self.HoverIterate):
                queue.removeComponent(gameObject, IsHoveredComponent)

            selectionAccess = self.reaction(self.SelectionAccess)
            if hoveredGameObject and selectionAccess.find(hoveredGameObject):
                queue.createComponent(hoveredGameObject, IsHoveredComponent)
            return

    def __getGameObjectUnderCursor(self):
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        skipFlags = CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE | CollisionFlags.TRIANGLE_NOCOLLIDE
        res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * self._MAX_PICK_RAY_LEN, skipFlags, -1, -1, ColliderTypes.HANGAR_FLAG)
        if res is not None and res[5] and res[5].valid:
            gameObject = res[5]
            cameraCollideAccess = self.reaction(self.CameraCollideAccess)
            cameraCollideComponent = cameraCollideAccess.find(gameObject)
            if cameraCollideComponent and cameraCollideComponent.isColliding:
                return
            return gameObject
        else:
            return
