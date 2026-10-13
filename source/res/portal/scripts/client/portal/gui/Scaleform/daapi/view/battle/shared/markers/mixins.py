# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/shared/markers/mixins.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from portal_constants import PORTAL_BATTLE_CTRL_ID
import typing
if typing.TYPE_CHECKING:
    from portal.gui.battle_control.controllers.markers.portal_markers_ctrl import PortalMarkersController

class PortalAreaMarkerListener(object):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def startListen(self):
        portalGuiBattleControllers = self.__guiSessionProvider.dynamic._repository._ctrls
        portalAreaMarkersController = portalGuiBattleControllers.get(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            portalAreaMarkersController.onMarkerToZoneAdded += self._onMarkerToZoneAdded
            portalAreaMarkersController.onMarkerFromZoneRemoved += self._onMarkerFromZoneRemoved
            portalAreaMarkersController.onMarkerProgressUpdated += self._onAreaMarkerProgressChanged

    def stopListen(self):
        portalGuiBattleControllers = self.__guiSessionProvider.dynamic._repository._ctrls
        portalAreaMarkersController = portalGuiBattleControllers.get(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            portalAreaMarkersController.onMarkerToZoneAdded -= self._onMarkerToZoneAdded
            portalAreaMarkersController.onMarkerFromZoneRemoved -= self._onMarkerFromZoneRemoved
            portalAreaMarkersController.onMarkerProgressUpdated -= self._onAreaMarkerProgressChanged

    def _onMarkerToZoneAdded(self, areaMarker, matrix):
        pass

    def _onMarkerFromZoneRemoved(self, areaMarker):
        pass

    def _onAreaMarkerProgressChanged(self, areaMarker, progress=None, restTime=None, maxHP=None, currentHP=None):
        pass
