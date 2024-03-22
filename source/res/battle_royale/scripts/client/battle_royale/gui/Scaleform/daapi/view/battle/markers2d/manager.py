# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/markers2d/manager.py
import plugins
import BattleReplay
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

class BattleRoyaleMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BattleRoyaleMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = plugins.BattleRoyaleVehicleMarkerPlugin
        setup['vehiclesTargets'] = plugins.BRVehicleMarkerTargetPlugin
        if BattleReplay.g_replayCtrl.isPlaying:
            setup['vehiclesTargets'] = plugins.BRVehicleMarkerTargetPluginReplayPlaying
        if BattleReplay.g_replayCtrl.isRecording:
            setup['vehiclesTargets'] = plugins.BRVehicleMarkerTargetPluginReplayRecording
        return setup
