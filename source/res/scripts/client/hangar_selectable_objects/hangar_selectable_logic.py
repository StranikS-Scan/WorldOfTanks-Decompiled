# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_selectable_objects/hangar_selectable_logic.py
import BigWorld
import SoundGroups
from gui.Scaleform.Waiting import Waiting
from hangar_selectable_objects import ISelectableObject
from .base_selectable_logic import BaseSelectableLogic

class HangarSelectableLogic(BaseSelectableLogic):
    __slots__ = ('__selected3DEntity', '__selected3DEntityUnderMouseDown')

    def __init__(self):
        super(HangarSelectableLogic, self).__init__()
        self.__selected3DEntity = None
        self.__selected3DEntityUnderMouseDown = None
        return

    def fini(self):
        self.__selected3DEntityUnderMouseDown = None
        if self.__selected3DEntity is not None:
            self.__fade3DEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        super(HangarSelectableLogic, self).fini()
        return

    def _onNotifyCursorOver3dScene(self, isCursorOver3dScene):
        if self.__selected3DEntity:
            if isCursorOver3dScene:
                self.__highlight3DEntity(self.__selected3DEntity)
            else:
                self.__fade3DEntity(self.__selected3DEntity)
        else:
            targetEntity = BigWorld.target()
            if targetEntity is not None:
                if isCursorOver3dScene and self._filterEntity(targetEntity):
                    self.__onMouseEnter(targetEntity)
        return

    def _filterEntity(self, entity):
        if entity is None:
            return False
        elif not isinstance(entity, ISelectableObject):
            return False
        elif not self._hangarSpace.isCursorOver3DScene:
            return False
        else:
            return False if not entity.enabled else True

    def _onMouseEnter(self, entity):
        if self.__onMouseEnter(entity) and entity.mouseOverSoundName:
            if entity.isOver3DSound:
                SoundGroups.g_instance.playSoundPos(entity.mouseOverSoundName, entity.model.root.position)
            else:
                SoundGroups.g_instance.playSound2D(entity.mouseOverSoundName)

    def _onMouseExit(self, entity):
        self.__selected3DEntity = None
        if not isinstance(entity, ISelectableObject):
            return
        else:
            if self._hangarSpace.isCursorOver3DScene:
                self.__fade3DEntity(entity)
            return

    def _onMouseDown(self):
        if self._hangarSpace.isCursorOver3DScene:
            self.__selected3DEntityUnderMouseDown = self.__selected3DEntity
            if self.__selected3DEntity:
                self.__selected3DEntity.onMouseDown()

    def _onMouseUp(self):
        if self._hangarSpace.isCursorOver3DScene:
            if self.__selected3DEntityUnderMouseDown:
                self.__selected3DEntityUnderMouseDown.onMouseUp()
                if self.__selected3DEntityUnderMouseDown == self.__selected3DEntity:
                    self.__selected3DEntityUnderMouseDown.onMouseClick()
        self.__onMouseEnter(self.__selected3DEntity)
        self.__selected3DEntityUnderMouseDown = None
        return

    def __onMouseEnter(self, entity):
        if Waiting.isVisible():
            return False
        if not self._filterEntity(entity):
            return False
        self.__selected3DEntity = entity
        self.__highlight3DEntity(entity)
        return True

    def __highlight3DEntity(self, entity):
        entity.setHighlight(True)
        self._callbackMethodCall('onHighlight3DEntity', entity)

    def __fade3DEntity(self, entity):
        entity.setHighlight(False)
        self._callbackMethodCall('onFade3DEntity', entity)
