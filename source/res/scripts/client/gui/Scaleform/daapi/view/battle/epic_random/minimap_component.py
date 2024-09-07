# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/minimap_component.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.classic.minimap import TeamsOrControlsPointsPlugin
_SCALE_FAC = 2.0 / 3.0

class EpicRandomMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(EpicRandomMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['points'] = EpicRandomTeamsOrControlsPointsPlugin
        return setup


class EpicRandomTeamsOrControlsPointsPlugin(TeamsOrControlsPointsPlugin):

    def _addPointEntry(self, symbol, position, number):
        entryID = super(EpicRandomTeamsOrControlsPointsPlugin, self)._addPointEntry(symbol, position, number)
        if entryID is not None:
            self._invoke(entryID, 'setScale', _SCALE_FAC)
        return entryID
