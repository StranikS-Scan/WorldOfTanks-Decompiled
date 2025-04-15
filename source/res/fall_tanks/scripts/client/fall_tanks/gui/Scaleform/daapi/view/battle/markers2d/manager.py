# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/markers2d/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins, MarkersManager
from fall_tanks.gui.Scaleform.daapi.view.battle.markers2d.vehicle_plugins import FallTanksSettingsPlugin, FallTanksVehicleMarkerPlugin

class FallTanksMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'fall_tanks|fallTanksBattleVehicleMarkersApp.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = {'settings': FallTanksSettingsPlugin,
         'eventBus': plugins.EventBusPlugin,
         'controlMode': plugins.ControlModePlugin,
         'vehiclesTargets': plugins.VehicleMarkerTargetPlugin,
         'vehicles': FallTanksVehicleMarkerPlugin}
        return setup
