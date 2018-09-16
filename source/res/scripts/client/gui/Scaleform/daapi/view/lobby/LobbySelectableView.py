# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbySelectableView.py
from gui.Scaleform.daapi import LobbySubView
import SoundGroups
import BigWorld
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class LobbySelectableView(LobbySubView):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbySelectableView, self).__init__(ctx)
        self.__selected3DEntity = None
        self.__selected3DEntityOnClick = None
        self.__isMouseDown = False
        self._objectSelectionEnabled = True
        return

    def _populate(self):
        super(LobbySelectableView, self)._populate()
        if self._objectSelectionEnabled:
            self.hangarSpace.onObjectSelected += self._on3DObjectSelected
            self.hangarSpace.onObjectUnselected += self._on3DObjectUnSelected
            self.hangarSpace.onObjectClicked += self._on3DObjectClicked
            self.hangarSpace.onObjectReleased += self._on3DObjectReleased
            self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)

    def _dispose(self):
        super(LobbySelectableView, self)._dispose()
        if self._objectSelectionEnabled:
            self.hangarSpace.onObjectSelected -= self._on3DObjectSelected
            self.hangarSpace.onObjectUnselected -= self._on3DObjectUnSelected
            self.hangarSpace.onObjectClicked -= self._on3DObjectClicked
            self.hangarSpace.onObjectReleased -= self._on3DObjectReleased
            self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)
        self.__selected3DEntityOnClick = None
        if self.__selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        return

    def _highlight3DEntityAndShowTT(self, entity):
        entity.highlight(True)

    def _fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)

    def _onNotifyCursorOver3dScene(self, event):
        isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self.__selected3DEntity:
            if isCursorOver3dScene:
                self._highlight3DEntityAndShowTT(self.__selected3DEntity)
            else:
                self._fade3DEntityAndHideTT(self.__selected3DEntity)

    def _on3DObjectSelected(self, entity):
        self.__selected3DEntity = entity
        if self.hangarSpace.isCursorOver3DScene and not self.__isMouseDown and entity:
            self._highlight3DEntityAndShowTT(entity)
            if entity.mouseOverSoundName:
                SoundGroups.g_instance.playSound3D(entity.model.root, entity.mouseOverSoundName)

    def _on3DObjectUnSelected(self, entity):
        self.__selected3DEntity = None
        self.__selected3DEntityOnClick = None
        if self.hangarSpace.isCursorOver3DScene:
            self._fade3DEntityAndHideTT(entity)
        return

    def _on3DObjectClicked(self):
        self.__isMouseDown = True
        self.__selected3DEntityOnClick = self.__selected3DEntity
        if self.hangarSpace.isCursorOver3DScene:
            if self.__selected3DEntity and hasattr(self.__selected3DEntity, 'onClicked'):
                self.__selected3DEntity.onClicked()

    def _on3DObjectReleased(self):
        self.__isMouseDown = False
        if self.hangarSpace.isCursorOver3DScene:
            if self.__selected3DEntity and self.__selected3DEntity == self.__selected3DEntityOnClick:
                if hasattr(self.__selected3DEntity, 'onReleased'):
                    self.__selected3DEntity.onReleased()
        self._on3DObjectSelected(self.__selected3DEntity)
        self.__selected3DEntityOnClick = None
        return
