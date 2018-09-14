# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbySelectableView.py
from gui.Scaleform.daapi import LobbySubView
from gui.shared.utils.HangarSpace import g_hangarSpace
import SoundGroups
import BigWorld
from gui.shared.events import LobbySimpleEvent

class LobbySelectableView(LobbySubView):

    def __init__(self, ctx=None):
        super(LobbySelectableView, self).__init__(ctx)
        self._isCursorOver3dScene = False
        self._selected3DEntity = None
        self.__objectSelectionEnabled = True
        return

    def _populate(self, objectSelectionEnabled=True):
        super(LobbySelectableView, self)._populate()
        self.__objectSelectionEnabled = objectSelectionEnabled
        if self.__objectSelectionEnabled:
            g_hangarSpace.onObjectSelected += self._on3DObjectSelected
            g_hangarSpace.onObjectUnselected += self._on3DObjectUnSelected
            g_hangarSpace.onObjectClicked += self._on3DObjectClicked
            g_hangarSpace.onObjectReleased += self._on3DObjectReleased
            self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)

    def _highlight3DEntityAndShowTT(self, entity):
        entity.highlight(True)

    def _fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)

    def _onNotifyCursorOver3dScene(self, event):
        self._isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self._selected3DEntity is not None:
            if self._isCursorOver3dScene:
                self._highlight3DEntityAndShowTT(self._selected3DEntity)
            else:
                self._fade3DEntityAndHideTT(self._selected3DEntity)
        return

    def _on3DObjectSelected(self, entity):
        self._selected3DEntity = entity
        if self._isCursorOver3dScene:
            self._highlight3DEntityAndShowTT(entity)
            if entity.mouseOverSoundName:
                SoundGroups.g_instance.playSound3D(entity.model.root, entity.mouseOverSoundName)

    def _on3DObjectUnSelected(self, entity):
        self._selected3DEntity = None
        if self._isCursorOver3dScene:
            self._fade3DEntityAndHideTT(entity)
        return

    def _on3DObjectClicked(self):
        if self._isCursorOver3dScene:
            if self._selected3DEntity is not None:
                self._selected3DEntity.onClicked()
        return

    def _on3DObjectReleased(self):
        if self._isCursorOver3dScene:
            if self._selected3DEntity is not None:
                self._selected3DEntity.onReleased()
        return

    def _dispose(self):
        super(LobbySelectableView, self)._dispose()
        if self.__objectSelectionEnabled:
            g_hangarSpace.onObjectSelected -= self._on3DObjectSelected
            g_hangarSpace.onObjectUnselected -= self._on3DObjectUnSelected
            g_hangarSpace.onObjectClicked -= self._on3DObjectClicked
            g_hangarSpace.onObjectReleased -= self._on3DObjectReleased
            self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self._onNotifyCursorOver3dScene)
        if self._selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self._selected3DEntity)
            self._selected3DEntity = None
        return
