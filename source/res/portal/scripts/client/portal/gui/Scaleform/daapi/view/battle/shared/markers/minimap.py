# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/shared/markers/minimap.py
import logging
import Math
import typing
from constants import MinimapLayerType
from portal.gui.Scaleform.daapi.view.battle.shared.markers.mixins import PortalAreaMarkerListener
from gui.Scaleform.daapi.view.battle.shared.minimap import common, settings
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from portal_constants import PORTAL_BATTLE_CTRL_ID, PORTAL_GUI_MARKERS_MINIMAP
from chat_commands_consts import getUniqueTeamOrControlPointID
from portal.gui.battle_control.controllers.portal_gui_controllers import getPortalBattleMarkersController
from gui.Scaleform.daapi.view.battle.epic.minimap import EpicMinimapPingPlugin
_logger = logging.getLogger(__name__)
_layerTypesMapping = {MinimapLayerType.BASE: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_EFFECT,
 MinimapLayerType.ALERT: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_ALERT}
if typing.TYPE_CHECKING:
    from portal.gui.battle_control.controllers.markers.portal_markers_ctrl import PortalMarkersController

class PortalMinimapAreaMarkersPlugin(common.EntriesPlugin, PortalAreaMarkerListener):

    def start(self):
        super(PortalMinimapAreaMarkersPlugin, self).start()
        portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            for areaMarker, markerPos in portalAreaMarkersController.getZoneMarkers().itervalues():
                self.__addAreaMarker(areaMarker, markerPos, areaMarker.markerMinimapEntryID)

        self.startListen()

    def stop(self):
        self.stopListen()
        super(PortalMinimapAreaMarkersPlugin, self).stop()

    def _onMarkerToZoneAdded(self, areaMarker, markerPos):
        self.__addAreaMarker(areaMarker, markerPos, areaMarker.markerMinimapEntryID)

    def _onMarkerFromZoneRemoved(self, areaMarker):
        self.__removeAreaMarker(areaMarker)

    def _onAreaMarkerProgressChanged(self, areaMarker, progress=None, restTime=None, maxHP=None, currentHP=None):
        self.__updateAreaMarkerProgress(areaMarker, progress, restTime)

    def __addAreaMarker(self, areaMarker, markerPos, markerEntryID):
        if not markerEntryID:
            _logger.info('Minimap marker is empty for areaMarker %d', areaMarker.id)
            return
        matrix = Math.Matrix()
        matrix.setTranslate(markerPos)
        self._addEntryEx(uniqueID=areaMarker.id, symbol=markerEntryID, container=settings.CONTAINER_NAME.EQUIPMENTS, matrix=matrix, active=True)

    def __removeAreaMarker(self, areaMarker):
        self._delEntryEx(uniqueID=areaMarker.id)

    def __updateAreaMarkerProgress(self, areaMarker, progress=None, restTime=None):
        if areaMarker and areaMarker.id in self._entries:
            entryID = self._entries[areaMarker.id].getID()
            if progress is not None:
                self._invoke(entryID, 'setProgress', progress)
        return


class PortalControlPointsPlugin(common.EntriesPlugin):

    def __init__(self, parentObj):
        super(PortalControlPointsPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        super(PortalControlPointsPlugin, self).start()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate += self.__onBasePointsUpdate
        self.restart()
        return

    def stop(self):
        super(PortalControlPointsPlugin, self).stop()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate -= self.__onBasePointsUpdate
        return

    def restart(self):
        self._addTeamBasePosition()

    def _addTeamBasePosition(self):
        positions = self._arenaVisitor.type.getTeamBasePositionsIterator()
        for team, position, number in positions:
            number = 1 if number == 0 else number
            uid = getUniqueTeamOrControlPointID(team, number)
            self._addBaseEntry(position, uid)

    def __onBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        uid = getUniqueTeamOrControlPointID(team, baseID)
        model = self.__markers.get(uid)
        if model is None:
            _logger.error('No marker with id: %d', uid)
            return
        else:
            self._invoke(model.getID(), 'setProgress', points)
            return

    def _addBaseEntry(self, position, uid):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        model = self._addEntryEx(uniqueID=uid, symbol=PORTAL_GUI_MARKERS_MINIMAP.BASE_MARKER, container=settings.CONTAINER_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if model is not None:
            self.__markers[uid] = model
        return


class PortalMinimapPingPlugin(EpicMinimapPingPlugin):

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        commands.sendAttentionToPosition3D(position, locationCommand)
