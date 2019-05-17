# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/session_stats_builders.py
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_tooltips import SessionStatsTankInfo, SessionStatsEfficiencyParam
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.SESSION_STATS_TANK_INFO, TOOLTIPS_CONSTANTS.SESSION_STATS_TANK_INFO_UI, SessionStatsTankInfo(contexts.SessionStatsContext())), DataBuilder(TOOLTIPS_CONSTANTS.SESSION_STATS_EFFICIENCY_PARAM, TOOLTIPS_CONSTANTS.SESSION_STATS_EFFICIENCY_PARAM_UI, SessionStatsEfficiencyParam(contexts.SessionStatsContext())))
