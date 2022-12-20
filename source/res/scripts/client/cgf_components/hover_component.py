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
        if not self.__enabled or not GUI.mcursor().inWindow or not GUI.mcursor().inFocus or not self._hangarSpace.isCursorOver3DScene:
            return
        else:
            cursorPosition = GUI.mcursor().position
            ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
            collidedId = None
            res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1000, 0, 0, -1, ColliderTypes.HANGAR_FLAG)
            if res is not None:
                collidedId = res[2]
            gameObjects = CGF.Query(self.spaceID, CGF.GameObject)
            for gameObject in gameObjects:
                if gameObject.id == collidedId:
                    self._updateHoverComponent(gameObject, True)
                self._updateHoverComponent(gameObject, False)

            return

    def _updateHoverComponent(self, go, isHovered):
        if isHovered:
            if go.findComponentByType(IsHovered) is None:
                go.createComponent(IsHovered)
        else:
            go.removeComponentByType(IsHovered)
        return
