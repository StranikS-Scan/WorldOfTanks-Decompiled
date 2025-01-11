# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/minimap.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.points_of_interest import minimap as poi_plugins

class BobMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BobMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['pointsOfInterest'] = poi_plugins.PointsOfInterestPlugin
        return setup
