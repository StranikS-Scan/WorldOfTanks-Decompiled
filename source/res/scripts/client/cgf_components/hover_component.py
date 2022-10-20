# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hover_component.py
import BigWorld
import CGF
import GUI
from GenericComponents import VSEComponent
from cgf_script.managers_registrator import tickGroup, onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import CGFComponent
from constants import IS_CLIENT
from vehicle_systems.tankStructure import ColliderTypes
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
if IS_CLIENT:
    from AvatarInputHandler import cameras

class IsHovered(CGFComponent):
    pass


class HoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HoverManager, self).__init__()
        self.__enabled = True

    def enable(self):
        self.__enabled = True

    def disable(self):
        self.__enabled = False

    @onAddedQuery(VSEComponent, IsHovered)
    def onIsHoveredAdded(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverIn()

    @onRemovedQuery(VSEComponent, IsHovered)
    def onIsHoveredRemoved(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverOut()

    @tickGroup(groupName='Simulation')
    def tick(self):
        gameObjectID = None
        if self.__enabled and GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isSelectionEnabled:
            gameObjectID = self.__getGameObjectUnderCursor()
        gameObjects = CGF.Query(self.spaceID, CGF.GameObject)
        for gameObject in gameObjects:
            if gameObject.id == gameObjectID:
                self._updateHoverComponent(gameObject, True)
            if gameObject.findComponentByType(IsHovered):
                self._updateHoverComponent(gameObject, False)

        return

    def _updateHoverComponent(self, go, isHovered):
        if isHovered:
            if go.findComponentByType(IsHovered) is None:
                go.createComponent(IsHovered)
        else:
            go.removeComponentByType(IsHovered)
        return

    def __getGameObjectUnderCursor(self):
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1000, 0, 0, -1, ColliderTypes.HANGAR_FLAG)
        return res[2] if res is not None else None
