# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/full_stats.py
from gui.Scaleform.daapi.view.battle.shared.tabbed_full_stats import TabbedFullStatsComponent

class FullStatsComponent(TabbedFullStatsComponent):

    @staticmethod
    def _buildTabs(builder):
        builder.addStatisticsTab()
        builder.addBoostersTab()
        return builder.getTabs()
