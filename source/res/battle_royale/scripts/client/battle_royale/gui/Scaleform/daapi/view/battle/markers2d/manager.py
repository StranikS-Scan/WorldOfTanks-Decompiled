# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/markers2d/manager.py
import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

class BattleRoyaleMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BattleRoyaleMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = plugins.BattleRoyaleVehicleMarkerPlugin
        setup['settings'] = plugins.BattleRoyaleSettingsPlugin
        return setup
