# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/minimap/component.py
import logging
from gui.Scaleform.daapi.view.battle.battle_royale.minimap import plugins
from gui.Scaleform.daapi.view.battle.epic.minimap import EpicMinimapComponent
_logger = logging.getLogger(__name__)
_RADAR_PLUGIN = 'radar'
_VEHICLES_PLUGIN = 'vehicles'

class BattleRoyaleMinimapComponent(EpicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BattleRoyaleMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['personal'] = plugins.BattleRoyalePersonalEntriesPlugin
        setup['deathZones'] = plugins.DeathZonesPlugin
        setup[_RADAR_PLUGIN] = plugins.BattleRoyaleRadarPlugin
        setup['airdrop'] = plugins.AirDropPlugin
        setup[_VEHICLES_PLUGIN] = plugins.BattleRoyaleVehiclePlugin
        setup['pinging'] = plugins.BattleRoyalMinimapPingPlugin
        setup['area'] = plugins.BattleRoyalStaticMarkerPlugin
        return setup

    def _populate(self):
        super(BattleRoyaleMinimapComponent, self)._populate()
        radarPlugin = self.getPlugin(_RADAR_PLUGIN)
        if radarPlugin:
            vehiclesPlugin = self.getPlugin(_VEHICLES_PLUGIN)
            if vehiclesPlugin:
                vehiclesPlugin.setRadarPlugin(radarPlugin)
                return
            _logger.error('Vehicles plugin has not been found!')
        else:
            _logger.error('Radar plugin has not been found!')
        _logger.error('Vehicles markers can not be initialized properly!')
