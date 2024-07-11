# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/ArenaInfoRacesComponent.py
import logging
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class ArenaInfoRacesComponent(DynamicScriptComponent):

    def __init__(self):
        super(ArenaInfoRacesComponent, self).__init__()
        self.onRaceEndTimeUpdated = Event.Event()
        self.onRankListUpdated = Event.Event()

    def onEnterWorld(self, prereqs):
        super(ArenaInfoRacesComponent, self).onEnterWorld(prereqs)
        _logger.debug('ArenaInfoRacesComponent endTime=%s', self.raceEndTime)

    def set_raceEndTime(self, _=None):
        _logger.debug('ArenaInfoRacesComponent endTime=%s', self.raceEndTime)
        self.onRaceEndTimeUpdated(self.raceEndTime)

    def set_rankList(self, _=None):
        rankList = self.rankList
        vehicleId = rankList[-1]['vehicleID']
        position = rankList[-1]['position']
        self.onRankListUpdated(vehicleId, position)

    def getPositionById(self, vehicleID):
        for item in self.rankList:
            if item['vehicleID'] == vehicleID:
                return item['position']
