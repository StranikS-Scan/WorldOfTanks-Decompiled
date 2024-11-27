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
from shared_utils import first
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


@registerComponent
class IsExternalHoveredComponent(object):
    domain = CGF.DomainOption.DomainClient


class HoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args):
        super(HoverManager, self).__init__(*args)
        self.__externalHovered = set()
        self.__currentExternalHoverId = None
        return

    def deactivate(self):
        self.__externalHovered.clear()
        self.__currentExternalHoverId = None
        return

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

    @onAddedQuery(CGF.GameObject, IsExternalHoveredComponent)
    def onIsExternalHoveredAdded(self, go, *args):
        self.__externalHovered.add(go.id)
        if self.__currentExternalHoverId is None:
            self.__currentExternalHoverId = go.id
        return

    @onRemovedQuery(CGF.GameObject, IsExternalHoveredComponent)
    def onIsExternalHoveredRemoved(self, go, *args):
        self.__externalHovered.discard(go.id)
        if self.__currentExternalHoverId == go.id:
            self.__currentExternalHoverId = None
        if self.__externalHovered and self.__currentExternalHoverId is None:
            self.__currentExternalHoverId = first(self.__externalHovered)
        return

    @tickGroup(groupName='Simulation')
    def tick(self):
        gameObjectID = None
        if GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isSelectionEnabled:
            if self.__currentExternalHoverId is not None:
                gameObjectID = self.__currentExternalHoverId
            elif self._hangarSpace.isCursorOver3DScene:
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
