# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/markers.py
import Math
from gui.battle_control import matrix_factory
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import MinimapEntry
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES as _CMD_NAMES
from chat_commands_consts import MarkerType, INVALID_COMMAND_ID

class _ObjectivesMarkerMixin(object):
    isAlly = property(lambda self: self._isAlly if hasattr(self, '_isAlly') else False)
    isGoalForPlayer = property(lambda self: self._isGoal if hasattr(self, '_isGoal') else False)
    isInAOI = property(lambda self: self._isInAOI if hasattr(self, '_isInAOI') else False)
    ownVehicleID = property(lambda self: self._ownVehicleID if hasattr(self, '_ownVehicleID') else 0)
    animationID = property(lambda self: self._animationID if hasattr(self, '_animationID') else 0)

    @isAlly.setter
    def isAlly(self, value):
        self._isAlly = value

    @isGoalForPlayer.setter
    def isGoalForPlayer(self, value):
        self._isGoal = value

    @isInAOI.setter
    def isInAOI(self, value):
        self._isInAOI = value

    @ownVehicleID.setter
    def ownVehicleID(self, value):
        self._ownVehicleID = value

    @animationID.setter
    def animationID(self, value):
        self._animationID = value


class HBObjectivesMarker(markers.LocationMarker, _ObjectivesMarkerMixin):
    FLASH_SYMBOL_NAME = 'HistoricalControlPointMarkerUI'
    DISTANCE_FOR_MARKER_HIDE = 50
    STATIC_MARKER_CULL_DISTANCE = 1800
    STATIC_MARKER_MIN_SCALE = 60.0
    STATIC_MARKER_BOUNDS = Math.Vector4(30, 30, 90, -15)
    INNER_STATIC_MARKER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    STATIC_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
    MIN_Y_OFFSET = 1.2
    MAX_Y_OFFSET = 3.0
    DISTANCE_FOR_MIN_Y_OFFSET = 400
    MAX_Y_BOOST = 1.4
    BOOST_START = 120

    def __init__(self, markerID, position, active=True, markerSymbolName=None):
        super(HBObjectivesMarker, self).__init__(markerID, position, active, markerSymbolName)
        self._activeCommandID = INVALID_COMMAND_ID
        self._boundCheckEnabled = True
        self._matrix = matrix_factory.makePositionMP(position)

    def getActiveCommandID(self):
        return self._activeCommandID

    def setActiveCommandID(self, commandID):
        self._activeCommandID = commandID

    def setMatrix(self, matrix):
        self._matrix = matrix

    def getMatrix(self):
        return self._matrix

    def getPosition(self):
        return Math.Matrix(self._matrix).translation if self._matrix is not None else self._position

    def setBoundCheckEnabled(self, enabled):
        self._boundCheckEnabled = enabled

    def getBoundCheckEnabled(self):
        return self._boundCheckEnabled


class HBObjectivesMinimapEntry(MinimapEntry, _ObjectivesMarkerMixin):
    FLASH_SYMBOL_NAME = 'HBCustomMinimapEntryUI'
    GOAL_ICON = 'controlPointBoss'
    GOAL_REPLIED_ICON = 'controlPointBossAttack'
    SPOTTED_ANIMATION = 'HistoricalPositionFlashEntryUI'
    ONCALL_ANIMATION = 'HBDamageAlertSPG'
    ANIMATION_SPEED = 1000.0
    ANIMATION_LIFETIME = 5.0

    def getMarkerID(self):
        return self.getID()


class HBPlayerPanelMarker(markers.Marker):
    ALLOWED_MARKER_TYPES = {MarkerType.LOCATION_MARKER_TYPE: (_CMD_NAMES.GOING_THERE, _CMD_NAMES.OBJECTIVES_POINT),
     MarkerType.VEHICLE_MARKER_TYPE: (_CMD_NAMES.ATTACK_ENEMY,
                                      _CMD_NAMES.ATTACKING_ENEMY,
                                      _CMD_NAMES.ATTACKING_ENEMY_WITH_SPG,
                                      _CMD_NAMES.SOS,
                                      _CMD_NAMES.HELPME,
                                      _CMD_NAMES.SUPPORTING_ALLY)}

    def __init__(self, markerID, markerType, active=True, markerSymbolName=None):
        super(HBPlayerPanelMarker, self).__init__(markerID, active)
        self._owners = set()
        self._activeCommandID = INVALID_COMMAND_ID
        self._boundCheckEnabled = True
        self._markerType = markerType
        self._markerSymbolName = markerSymbolName

    def getActiveCommandID(self):
        return self._activeCommandID

    def setActiveCommandID(self, commandID):
        self._activeCommandID = commandID

    def getMarkerOwners(self):
        return self._owners

    def setMarkerOwners(self, owners):
        self._owners = owners

    def getMarkerType(self):
        return self._markerType

    def getMarkerSubtype(self):
        return self._markerSymbolName

    def setBoundCheckEnabled(self, enabled):
        self._boundCheckEnabled = enabled

    def getBoundCheckEnabled(self):
        return self._boundCheckEnabled


class HBVehiclePanelMarker(HBPlayerPanelMarker):
    ALLOWED_MARKER_TYPES = {MarkerType.VEHICLE_MARKER_TYPE: (_CMD_NAMES.ATTACK_ENEMY, _CMD_NAMES.ATTACKING_ENEMY, _CMD_NAMES.ATTACKING_ENEMY_WITH_SPG)}
