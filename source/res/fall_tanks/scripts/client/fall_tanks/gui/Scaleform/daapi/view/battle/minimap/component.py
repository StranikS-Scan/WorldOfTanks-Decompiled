# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/minimap/component.py
from constants import IS_DEVELOPMENT
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicTeleportPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent
from fall_tanks.gui.Scaleform.daapi.view.battle.minimap.plugins import FallTanksGlobalSettingsPlugin, FallTanksPersonalEntriesPlugin, FallTanksArenaVehiclesPlugin

class FallTanksMinimapComponent(MinimapComponent):

    def hasMinimapGrid(self):
        return True

    def _setupPlugins(self, arenaVisitor):
        setup = {'settings': FallTanksGlobalSettingsPlugin,
         'personal': FallTanksPersonalEntriesPlugin,
         'vehicles': FallTanksArenaVehiclesPlugin}
        if IS_DEVELOPMENT:
            setup['teleport'] = ClassicTeleportPlugin
        return setup
