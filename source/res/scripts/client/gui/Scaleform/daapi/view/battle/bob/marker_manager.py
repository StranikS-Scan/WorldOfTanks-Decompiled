# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/marker_manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.points_of_interest import markers2d as poi_plugins

class BobMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BobMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['pointsOfInterest'] = poi_plugins.PointsOfInterestPlugin
        return setup
