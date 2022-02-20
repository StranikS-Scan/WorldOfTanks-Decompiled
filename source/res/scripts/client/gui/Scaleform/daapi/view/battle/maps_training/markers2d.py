# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/markers2d.py
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins, vehicle_plugins, MarkersManager

class _MapsTrainingVehicleMarkerPlugin(vehicle_plugins.VehicleMarkerPlugin):
    __slots__ = ('__localGoals',)

    def __init__(self, parentObj):
        super(_MapsTrainingVehicleMarkerPlugin, self).__init__(parentObj)
        self.__localGoals = set()

    def start(self):
        super(_MapsTrainingVehicleMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onLocalKillGoalsUpdated += self.__onLocalKillGoalsUpdated
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onLocalKillGoalsUpdated -= self.__onLocalKillGoalsUpdated
        self.__localGoals = set()
        super(_MapsTrainingVehicleMarkerPlugin, self).stop()
        return

    def _setMarkerInitialState(self, marker, accountDBID=0):
        super(_MapsTrainingVehicleMarkerPlugin, self)._setMarkerInitialState(marker, accountDBID)
        self.__updateGoal(marker)

    def __onLocalKillGoalsUpdated(self, localGoals):
        self.__localGoals = set((vehID for vehID in localGoals))
        for marker in self._markers.itervalues():
            self.__updateGoal(marker)

    def __updateGoal(self, marker):
        if marker.getVehicleID() in self.__localGoals:
            self._invokeMarker(marker.getMarkerID(), 'showActionMarker', 'attack')
            marker.setActionState('attack')
            marker.setIsActionMarkerActive(True)
            marker.setIsSticky(True)
            self._setMarkerSticky(marker.getMarkerID(), True)


class MapsTrainingAreaStaticMarkerPlugin(plugins.AreaStaticMarkerPlugin):
    __slots__ = ()

    def start(self):
        super(MapsTrainingAreaStaticMarkerPlugin, self).start()
        self.settingsCore.onSettingsChanged += self.__onSettingsChange

    def stop(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        super(MapsTrainingAreaStaticMarkerPlugin, self).stop()

    def _onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if replierID == self.sessionProvider.arenaVisitor.getArenaUniqueID() or marker is None:
            return
        else:
            self._setMarkerRepliesAndCheckState(marker, newReplyCount, replierID == avatar_getter.getPlayerVehicleID())
            return

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_STICKY_MARKERS in diff.keys():
            for marker in self._markers.values():
                self.__updateMarkerIsSticky(marker)

    def __updateMarkerIsSticky(self, marker):
        markerID = marker.getMarkerID()
        if marker.getIsSticky():
            self._setMarkerSticky(markerID, True)


class MapsTrainingMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(MapsTrainingMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = _MapsTrainingVehicleMarkerPlugin
        setup['area'] = MapsTrainingAreaStaticMarkerPlugin
        return setup
