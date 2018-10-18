# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import logging
import math
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin, IArenaVehiclesController
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings, markers
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
_logger = logging.getLogger(__name__)

class PveEventVehicleMarkerPlugin(MarkerPlugin, IArenaVehiclesController):
    __slots__ = ('_markers', '_clazz', '_playerVehicleID', '_vehicleMarkerName', '_avgPlayerDamage', '_playerTeam')
    __DENIED_VEHICLE_MARKERS = ('attackSender',)

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(PveEventVehicleMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self._clazz = clazz
        self._playerVehicleID = 0
        self._playerTeam = None
        self._avgPlayerDamage = None
        self._vehicleMarkerName = settings.MARKER_SYMBOL_NAME.VEHICLE_PVE_MARKER
        return

    def init(self):
        super(PveEventVehicleMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
        eventPointsComp = self._getEventPointsComponent()
        if eventPointsComp is not None:
            eventPointsComp.onCurrentEventPointsUpdated += self.__onCurrentEventPointsUpdated
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
        eventPointsComp = self._getEventPointsComponent()
        if eventPointsComp is not None:
            eventPointsComp.onCurrentEventPointsUpdated -= self.__onCurrentEventPointsUpdated
        super(PveEventVehicleMarkerPlugin, self).fini()
        return

    def start(self):
        super(PveEventVehicleMarkerPlugin, self).start()
        arenaDP = self.sessionProvider.getArenaDP()
        self._playerVehicleID = arenaDP.getPlayerVehicleID()
        self._playerTeam = arenaDP.getNumberOfTeam()
        self.sessionProvider.addArenaCtrl(self)

    def stop(self):
        while self._markers:
            _, marker = self._markers.popitem()
            marker.destroy()

        super(PveEventVehicleMarkerPlugin, self).stop()

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        feedback = self.sessionProvider.shared.feedback
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if not vInfo.isAlive():
                continue
            vehicleID = vInfo.vehicleID
            if vehicleID == self._playerVehicleID:
                continue
            vProxy = feedback.getVehicleProxy(vehicleID)
            if vehicleID not in self._markers:
                self.__addMarkerToPool(vehicleID, vProxy=vProxy)
            self._initVehicleMarker(vInfo)

    def _getEventPointsComponent(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        return getattr(componentSystem, 'eventPointsComponent', None)

    def _calcHeathValue(self, health, vehicleID):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        if vInfo.team == self._playerTeam:
            return health
        else:
            playerDamage = self._avgPlayerDamage
            result = 1
            if playerDamage is None:
                vProxy = self.sessionProvider.shared.feedback.getVehicleProxy(self._playerVehicleID)
                if vProxy is None:
                    return result
                playerDamage = self._avgPlayerDamage = vProxy.typeDescriptor.shot.shell.damage[0]
            try:
                result = math.ceil(health / playerDamage)
            except ZeroDivisionError:
                _logger.warning('ZeroDivisionError: _avgPlayerDamage cannot be 0')

            return result

    def _initVehicleMarker(self, vInfo):
        marker = self._markers.get(vInfo.vehicleID)
        if marker and marker.isActive():
            markerID = marker.getMarkerID()
            if vInfo.team == self._playerTeam:
                teamMarker = 'ally'
                battleCtx = self.sessionProvider.getCtx()
                playerColor = '#F2EC4E' if battleCtx.isSquadMan(vInfo.vehicleID) else '#60B169'
                playerName = battleCtx.getPlayerFullNameParts(vInfo.vehicleID).playerName
                playerName = '<font color="{}">{}</font>'.format(playerColor, playerName)
                self._invokeMarker(markerID, 'setPlayerName', playerName)
                self._invokeMarker(markerID, 'setCounter', 0)
                eventPointsComp = self._getEventPointsComponent()
                if eventPointsComp is not None:
                    self.__onCurrentEventPointsUpdated(eventPointsComp.currentEventPoints, vInfo.vehicleID)
            else:
                teamMarker = 'enemy'
            self._invokeMarker(markerID, 'setType', teamMarker)
            self._invokeMarker(markerID, 'setInitHealth', self._calcHeathValue(vInfo.vehicleType.maxHealth, vInfo.vehicleID), self._calcHeathValue(marker.getHealth(), vInfo.vehicleID))
        return

    def _setVehicleDead(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def _showActionMarker(self, vehicleID, markerName):
        if markerName in self.__DENIED_VEHICLE_MARKERS:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        if markerName == 'attack':
            self._invokeMarker(markerID, 'setAttack', True)
        else:
            self._invokeMarker(markerID, 'showActionMarker', markerName)

    def _updateVehicleHealth(self, markerID, vehicleID, newHealth, *args):
        self._invokeMarker(markerID, 'setHealth', self._calcHeathValue(newHealth, vehicleID))

    def _hideVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setActive(False):
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, False)
                self._setMarkerMatrix(markerID, None)
            marker.detach()
        return

    def __onCurrentEventPointsUpdated(self, eventPoints, vehicleID=None):
        teamPoints = eventPoints[self._playerTeam]
        if vehicleID is not None and vehicleID in self._markers and vehicleID in teamPoints:
            self._invokeMarker(self._markers[vehicleID].getMarkerID(), 'setCounter', teamPoints[vehicleID])
        else:
            for vID, pointValue in teamPoints.iteritems():
                if vID in self._markers:
                    self._invokeMarker(self._markers[vID].getMarkerID(), 'setCounter', pointValue)

        return

    def __onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def __onVehicleMarkerAdded(self, vProxy, vInfo, *args):
        if not vInfo.isAlive():
            return
        vehicleID = vInfo.vehicleID
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setActive(True):
                marker.attach(vProxy)
                self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())
                self._setMarkerActive(marker.getMarkerID(), True)
                self._initVehicleMarker(vInfo)
        else:
            self.__addMarkerToPool(vehicleID, vProxy)
            self._initVehicleMarker(vInfo)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self._markers:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        if eventID == _EVENT_ID.VEHICLE_DEAD:
            self._setVehicleDead(vehicleID)
        elif eventID == _EVENT_ID.VEHICLE_HEALTH:
            self._updateVehicleHealth(markerID, vehicleID, *value)
        elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
            self._showActionMarker(vehicleID, value)

    def __addMarkerToPool(self, vehicleID, vProxy=None):
        if vProxy is not None:
            matrixProvider = self._clazz.fetchMatrixProvider(vProxy)
            active = True
        else:
            matrixProvider = None
            active = False
        markerID = self._createMarkerWithMatrix(self._vehicleMarkerName, matrixProvider=matrixProvider, active=active)
        marker = self._clazz(markerID, vehicleID, vProxy=vProxy, active=active)
        marker.onVehicleModelChanged += self.__onVehicleModelChanged
        self._markers[vehicleID] = marker
        return marker

    def __onVehicleModelChanged(self, markerID, matrixProvider):
        self._setMarkerMatrix(markerID, matrixProvider)
