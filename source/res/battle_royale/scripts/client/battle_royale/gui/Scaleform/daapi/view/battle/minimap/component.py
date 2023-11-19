# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/minimap/component.py
import logging
import plugins
from gui.Scaleform.daapi.view.battle.epic.minimap import EpicMinimapComponent
_logger = logging.getLogger(__name__)

class BattleRoyaleMinimapComponent(EpicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BattleRoyaleMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['personal'] = plugins.BattleRoyalePersonalEntriesPlugin
        setup['deathZones'] = plugins.DeathZonesPlugin
        setup[plugins.RADAR_PLUGIN] = plugins.BattleRoyaleRadarPlugin
        setup['airdrop'] = plugins.AirDropPlugin
        setup[plugins.VEHICLES_PLUGIN] = plugins.BattleRoyaleVehiclePlugin
        setup['pinging'] = plugins.BattleRoyalMinimapPingPlugin
        setup['area'] = plugins.BattleRoyalStaticMarkerPlugin
        return setup
