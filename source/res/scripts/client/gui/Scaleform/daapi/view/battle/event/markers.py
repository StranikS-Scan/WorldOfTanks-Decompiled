# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers, settings

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
    MARKER_OWNERS = {settings.MARKER_SYMBOL_NAME.EVENT_VOLOT_MARKER: 'ally',
     settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER: 'enemy'}

    def __init__(self, markerID, active=True, owner=None):
        super(EventBaseMarker, self).__init__(markerID, active, owner)
        self._position = None
        self._symbol = None
        self._isInProgress = False
        self._progress = (0, 0)
        return

    def setSymbol(self, symbol):
        self._symbol = symbol

    def getSymbol(self):
        return self._symbol

    def setPosition(self, position):
        self._position = position

    def getPosition(self):
        return self._position

    def getDistance(self, playerPosition):
        return None if self._position is None else (self._position - playerPosition).length

    def setIsInProgress(self, isInProgress):
        self._isInProgress = isInProgress

    def getIsInProgress(self):
        return self._isInProgress

    def setProgress(self, progress):
        self._progress = progress

    def getProgress(self):
        return self._progress


class EventBaseMinimapMarker(EventBaseMarker):
    MARKER_SYMBOLS = {'SoulCollector': 'EventVolotEntryUI',
     'EnemyCamp': 'EventEnemyCampEntryUI'}


class EventBasePlayerPanelMarker(EventBaseMarker):
    MARKER_SYMBOLS = {'SoulCollector': 'eventCollector',
     'EnemyCamp': 'eventCamp'}
