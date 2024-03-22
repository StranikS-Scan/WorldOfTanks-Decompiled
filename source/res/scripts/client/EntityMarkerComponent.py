# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityMarkerComponent.py
import typing
from chat_commands_consts import MarkerType, INVALID_TARGET_ID
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController

class EntityMarkerComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EntityMarkerComponent, self).__init__()
        self._isReconnect = not self._isAvatarReady
        self.markerID = None
        return

    def set_visible(self, oldValue):
        ctrl = self.sessionProvider.shared.areaMarker
        if not ctrl:
            return
        if self.visible:
            ctrl.showMarkersById(self.markerID)
        else:
            ctrl.hideMarkersById(self.markerID)

    def onDestroy(self):
        super(EntityMarkerComponent, self).onDestroy()
        self.__clearBattleCommunication()
        self.__removeMarker()
        self.markerID = None
        return

    def _onAvatarReady(self):
        super(EntityMarkerComponent, self)._onAvatarReady()
        self.__createMarker(isReconnect=self._isReconnect)

    def __createMarker(self, isReconnect=False):
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl:
            marker = ctrl.createMarker(matrix=self.entity.matrix, markerType=self.style, targetID=self.bcTargetID, entity=self.entity, visible=self.visible)
            self.markerID = ctrl.addMarker(marker, isReconnect=isReconnect)

    def __clearBattleCommunication(self):
        ctrl = self.sessionProvider.shared.areaMarker
        if not ctrl:
            return
        else:
            advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            marker = ctrl.getMarkerById(self.markerID)
            if advChatCmp and marker and self.bcTargetID != INVALID_TARGET_ID:
                for component in marker.components.itervalues():
                    if component.bcMarkerType == MarkerType.INVALID_MARKER_TYPE:
                        continue
                    advChatCmp.removeActualTargetIfDestroyed(self.bcTargetID, component.bcMarkerType)

            return

    def __removeMarker(self):
        ctrl = self.sessionProvider.shared.areaMarker
        if not ctrl:
            return
        ctrl.removeMarker(self.markerID)
