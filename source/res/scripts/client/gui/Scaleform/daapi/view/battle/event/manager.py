# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.event.plugins import EventVehicleMarkerPlugin, EventCampsOrControlsPointsPlugin
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys

class EventMarkersManager(MarkersManager):

    def _populate(self):
        self.settingsCore.applySetting(BattleCommStorageKeys.SHOW_STICKY_MARKERS, True)
        self.settingsCore.applySetting(BattleCommStorageKeys.SHOW_BASE_MARKERS, True)
        self.settingsCore.confirmChanges(self.settingsCore.applyStorages(restartApproved=False))
        self.settingsCore.clearStorages()
        super(EventMarkersManager, self)._populate()

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = EventVehicleMarkerPlugin
        setup['teamAndControlPoints'] = EventCampsOrControlsPointsPlugin
        return setup
