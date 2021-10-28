# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers, settings
from chat_commands_consts import MarkerType, INVALID_COMMAND_ID

class EventVehicleMarker(markers.VehicleMarker):
    OVERRIDE_CHAT_COMMAND_NAME = {'attackBase': 'eventCamp',
     'attackingBase': 'eventCamp',
     'defendBase': 'eventCollector',
     'defendingBase': 'eventCollector'}

    def getOverride(self, command):
        return self.OVERRIDE_CHAT_COMMAND_NAME.get(command, command)


class EventBaseMarker(markers.BaseMarker):
    VOLOT_SYMBOL = 'EventVolot'
    CAMP_SHAPE = 'EventEnemyCamp'
    CAMP_COLOR = 'white'
    MARKER_SYMBOLS = {'SoulCollector': settings.MARKER_SYMBOL_NAME.EVENT_VOLOT_MARKER,
     'EnemyCamp': settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER}
    UNSUPPORTED_INVOKE_FN = ('triggerClickAnimation',)

    def __init__(self, markerID, active, symbol, position):
        super(EventBaseMarker, self).__init__(markerID, active)
        self._position = position
        self._symbol = symbol
        self._relevantGoal = None
        self._progress = (0, 0)
        return

    def getSymbol(self):
        return self._symbol

    def getPosition(self):
        return self._position

    def getDistance(self, playerPosition):
        return None if self._position is None else (self._position - playerPosition).length

    def setRelevantGoal(self, relevantGoal):
        self._relevantGoal = relevantGoal

    def getRelevantGoal(self):
        return self._relevantGoal

    def setProgress(self, progress):
        self._progress = progress

    def getProgress(self):
        return self._progress

    def isVolot(self):
        return self._symbol.startswith(self.VOLOT_SYMBOL)


class EventBaseMinimapMarker(EventBaseMarker):
    MARKER_SYMBOLS = {'SoulCollector': 'EventVolotEntryUI',
     'EnemyCamp': 'EventEnemyCampEntryUI'}
    UNSUPPORTED_INVOKE_FN = ('triggerClickAnimation', 'setReplyCount', 'setActiveState', 'setMarkerReplied')

    def getDistance(self, _):
        return None


class EventPlayerPanelMarker(markers.Marker):
    MARKER_SYMBOLS = {'SoulCollector': 'eventCollector',
     'EnemyCamp': 'eventCamp'}
    ALLOWED_MARKER_TYPES = {MarkerType.LOCATION_MARKER_TYPE: ('goingTo',),
     MarkerType.BASE_MARKER_TYPE: ('eventCollector', 'eventCamp'),
     MarkerType.VEHICLE_MARKER_TYPE: ('attack',)}

    def __init__(self, markerID, markerType, active=True, markerSymbolName=None):
        super(EventPlayerPanelMarker, self).__init__(markerID, active)
        self._owners = set()
        self._activeCommandID = INVALID_COMMAND_ID
        self._boundCheckEnabled = True
        self._markerType = markerType
        self._markerSymbolName = self.MARKER_SYMBOLS[markerSymbolName] if markerSymbolName in self.MARKER_SYMBOLS else markerSymbolName

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
