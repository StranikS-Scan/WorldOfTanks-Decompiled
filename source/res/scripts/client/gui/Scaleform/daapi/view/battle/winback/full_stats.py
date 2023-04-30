# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/winback/full_stats.py
from gui.Scaleform.daapi.view.battle.classic.full_stats import FullStatsComponent

class WinbackFullStatsComponent(FullStatsComponent):

    @staticmethod
    def _buildTabs(builder):
        builder.addStatisticsTab()
        builder.addBoostersTab()
        return builder.getTabs()
