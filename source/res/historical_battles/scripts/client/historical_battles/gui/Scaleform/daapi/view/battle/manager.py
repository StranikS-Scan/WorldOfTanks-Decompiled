# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/manager.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from historical_battles.gui.Scaleform.daapi.view.battle.markers2d import HBVehicleMarkerSettingsPlugin, HBVehicleMarkerPlugin, HBObjectivesMarkerPlugin, HBTeamsOrControlsPointsPlugin, HBAreaMarkerPlugin, HBEquipmentsMarkerPlugin

class HistoricalMarkersManager(EventMarkersManager):
    MARKERS_MANAGER_SWF = 'historical_battles|historical_battles_battle_vehicle_markers.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(HistoricalMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['area_markers'] = HBAreaMarkerPlugin
        setup['equipments'] = HBEquipmentsMarkerPlugin
        setup['vehicles'] = HBVehicleMarkerPlugin
        setup['settings'] = HBVehicleMarkerSettingsPlugin
        setup['objectives'] = HBObjectivesMarkerPlugin
        if 'teamAndControlPoints' in setup:
            setup['teamAndControlPoints'] = HBTeamsOrControlsPointsPlugin
        return setup

    def setMarkerRenderInfo(self, markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale):
        self.setMarkerCustomDistanceStr(markerID, self.__getInbattleMarkersCustomDistanceStr())
        super(HistoricalMarkersManager, self).setMarkerRenderInfo(markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale)

    def __getInbattleMarkersCustomDistanceStr(self):
        return backport.text(R.strings.hb_battle.inbattle_markers.distance_str())
