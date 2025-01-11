# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hover_component.py
import BigWorld
import CGF
import GUI
import Event
from GenericComponents import VSEComponent
from cgf_script.managers_registrator import tickGroup, onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent
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

    def __init__(self):
        super(SelectionComponent, self).__init__()
        self.onClickAction = Event.Event()


@registerComponent
class IsHoveredComponent(object):
    domain = CGF.DomainOption.DomainClient


class HoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

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
        gameObjectID = None
        if GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isSelectionEnabled and self._hangarSpace.isCursorOver3DScene:
            gameObjectID = self.__getGameObjectUnderCursor()
        hoveredGameObject = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent))
        for gameObject, _ in hoveredGameObject:
            if gameObject.id != gameObjectID:
                gameObject.removeComponentByType(IsHoveredComponent)
            return

        if gameObjectID == 0:
            return
        else:
            hoverableGameObjects = CGF.Query(self.spaceID, (CGF.GameObject, SelectionComponent))
            for gameObject, _ in hoverableGameObjects:
                if gameObject.id == gameObjectID:
                    gameObject.createComponent(IsHoveredComponent)

            return

    def __getGameObjectUnderCursor(self):
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        skipFlags = CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE | CollisionFlags.TRIANGLE_NOCOLLIDE
        res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1500, skipFlags, -1, -1, ColliderTypes.HANGAR_FLAG)
        return res[5] if res is not None else None
