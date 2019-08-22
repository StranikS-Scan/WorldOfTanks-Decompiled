# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/minimap/component.py
from gui.Scaleform.daapi.view.battle.battle_royale.minimap import plugins
from gui.Scaleform.daapi.view.battle.epic.minimap import EpicMinimapComponent
from gui.Scaleform.daapi.view.battle.epic.minimap import SimpleMarkPositionPlugin

class BattleRoyaleMinimapComponent(EpicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BattleRoyaleMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['personal'] = plugins.BattleRoyalePersonalEntriesPlugin
        setup['deathZones'] = plugins.DeathZonesPlugin
        setup['radar'] = plugins.BattleRoyaleRadarPlugin
        setup['airdrop'] = plugins.AirDropPlugin
        setup['vehicles'] = plugins.BattleRoyaleVehiclePlugin
        setup['cells'] = SimpleMarkPositionPlugin
        return setup
