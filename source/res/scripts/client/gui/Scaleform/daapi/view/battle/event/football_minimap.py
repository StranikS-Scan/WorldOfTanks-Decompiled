# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_minimap.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins

class FootballSettingsPlugin(GlobalSettingsPlugin):

    def start(self):
        pass

    def stop(self):
        pass

    def _toogleVisible(self):
        pass


class FootballMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(FootballMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['PhysicalObject'] = plugins.PhysicalObjectPlugin
        setup['settings'] = FootballSettingsPlugin
        return setup
