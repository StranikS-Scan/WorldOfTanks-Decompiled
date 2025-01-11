# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/manager.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import CommonMarkerType
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from grinch.cgf.presents import getScoreComponent
from grinch.gui.shared.events import TurretDeployEvent, FlareAbilityEvent, RageAbilityEvent
VEHICLE_MARKER = 'GrinchVehicleMarkerUI'

class GrinchMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'grinch|grinchBattleVehicleMarkersApp.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(GrinchMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = GrinchVehicleMarkerPlugin
        return setup


class GrinchVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def start(self):
        super(GrinchVehicleMarkerPlugin, self).start()
        scoreCmp = getScoreComponent()
        if scoreCmp:
            scoreCmp.onVehiclePointsUpdated += self._onVehiclePointsUpdated
        g_eventBus.addListener(TurretDeployEvent.TURRET_DEPLOY_TIME_CHANGED, self._onTurretDeployUpdated, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(FlareAbilityEvent.FLARE_MARK, self._onFlareShow, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(RageAbilityEvent.VEHICLE_STATUS_CHANGED, self.__onRageVehicleStatusUpdate, EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        super(GrinchVehicleMarkerPlugin, self).stop()
        g_eventBus.removeListener(TurretDeployEvent.TURRET_DEPLOY_TIME_CHANGED, self._onTurretDeployUpdated, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(FlareAbilityEvent.FLARE_MARK, self._onFlareShow, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(RageAbilityEvent.VEHICLE_STATUS_CHANGED, self.__onRageVehicleStatusUpdate, EVENT_BUS_SCOPE.BATTLE)
        scoreCmp = getScoreComponent()
        if scoreCmp:
            scoreCmp.onVehiclePointsUpdated -= self._onVehiclePointsUpdated

    def __onRageVehicleStatusUpdate(self, event):
        if event.vehicleID in self._markers:
            markerID = self._markers[event.vehicleID].getMarkerID()
            if event.vehicleUndeadStatus:
                self._invokeMarker(markerID, 'updateRageUndeadHealth', 0)

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        team = vInfo.team
        hunting = False
        guiPropsName = 'team_' + str(team)
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        classTag = vInfo.getDisplayedClassTag()
        vehicleName = vInfo.getDisplayedName(nameParts.vehicleName)
        self._invokeMarker(markerID, 'setEntityType', guiProps.name())
        self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, vehicleName, self._getVehicleLevel(vInfo), nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')
        scoreCmp = getScoreComponent()
        if scoreCmp:
            points, _ = scoreCmp.getVehiclePoints(vInfo.vehicleID)
        else:
            points = 0
        self._invokeMarker(markerID, 'setGiftCount', points)

    def _onVehiclePointsUpdated(self, vehiclePoints):
        for vehicleID, (points, _) in vehiclePoints.iteritems():
            if vehicleID in self._markers:
                markerID = self._markers[vehicleID].getMarkerID()
                self._invokeMarker(markerID, 'setGiftCount', points)

    def _onTurretDeployUpdated(self, event):
        if event.vehicleID in self._markers:
            markerID = self._markers[event.vehicleID].getMarkerID()
            self._invokeMarker(markerID, 'showTurretDeploySeconds', event.deployTimeLeft)

    def _onFlareShow(self, event):
        if event.vehicleID in self._markers:
            markerID = self._markers[event.vehicleID].getMarkerID()
            self._invokeMarker(markerID, 'showFlareMark', event.isOn)

    def _getMarker2dType(self):
        return CommonMarkerType.VEHICLE

    def _getMarkerSymbol(self, _):
        return VEHICLE_MARKER
