# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbySelectableView.py
from gui.Scaleform.daapi import LobbySubView
import SoundGroups
import BigWorld
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.Waiting import Waiting

class LobbySelectableView(LobbySubView):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbySelectableView, self).__init__(ctx)
        self.__selected3DEntity = None
        self.__selected3DEntityUnderMouseDown = None
        return

    def _populate(self):
        super(LobbySelectableView, self)._populate()
        self.hangarSpace.onMouseEnter += self._on3DObjectMouseEnter
        self.hangarSpace.onMouseExit += self._on3DObjectMouseExit
        self.hangarSpace.onMouseDown += self._on3DObjectMouseDown
        self.hangarSpace.onMouseUp += self._on3DObjectMouseUp
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)

    def _dispose(self):
        super(LobbySelectableView, self)._dispose()
        self.hangarSpace.onMouseEnter -= self._on3DObjectMouseEnter
        self.hangarSpace.onMouseExit -= self._on3DObjectMouseExit
        self.hangarSpace.onMouseDown -= self._on3DObjectMouseDown
        self.hangarSpace.onMouseUp -= self._on3DObjectMouseUp
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)
        self.__selected3DEntityUnderMouseDown = None
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

    def _on3DObjectMouseEnter(self, entity):
        if Waiting.isVisible():
            return
        else:
            self.__selected3DEntity = entity
            if not self.hangarSpace.isCursorOver3DScene:
                return
            if entity is None:
                return
            self._highlight3DEntityAndShowTT(entity)
            if entity.mouseOverSoundName:
                SoundGroups.g_instance.playSound3D(entity.model.root, entity.mouseOverSoundName)
            return

    def _on3DObjectMouseExit(self, entity):
        self.__selected3DEntity = None
        if self.hangarSpace.isCursorOver3DScene:
            self._fade3DEntityAndHideTT(entity)
        return

    def _on3DObjectMouseDown(self):
        if self.hangarSpace.isCursorOver3DScene:
            self.__selected3DEntityUnderMouseDown = self.__selected3DEntity
            if self.__selected3DEntity and hasattr(self.__selected3DEntity, 'onMouseDown'):
                self.__selected3DEntity.onMouseDown()

    def _on3DObjectMouseUp(self):
        if self.hangarSpace.isCursorOver3DScene:
            if self.__selected3DEntityUnderMouseDown:
                if self.__selected3DEntityUnderMouseDown == self.__selected3DEntity:
                    if hasattr(self.__selected3DEntityUnderMouseDown, 'onMouseClick'):
                        self.__selected3DEntityUnderMouseDown.onMouseClick()
                if hasattr(self.__selected3DEntityUnderMouseDown, 'onMouseUp'):
                    self.__selected3DEntityUnderMouseDown.onMouseUp()
        self._on3DObjectMouseEnter(self.__selected3DEntity)
        self.__selected3DEntityUnderMouseDown = None
        return
