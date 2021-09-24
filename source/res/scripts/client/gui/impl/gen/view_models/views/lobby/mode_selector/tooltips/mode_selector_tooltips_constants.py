# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/tooltips/mode_selector_tooltips_constants.py
from frameworks.wulf import ViewModel

class ModeSelectorTooltipsConstants(ViewModel):
    __slots__ = ()
    DISABLED_TOOLTIP = 'disabledTooltip'
    RANDOM_BP_PAUSED_TOOLTIP = 'randomBPPausedTooltip'
    RANKED_CALENDAR_DAY_INFO_TOOLTIP = 'rankedCalendarDayInfoExtended'
    RANKED_STEP_TOOLTIP = 'rankedStep'
    RANKED_BATTLES_RANK_TOOLTIP = 'rankedBattlesRank'
    RANKED_BATTLES_LEAGUE_TOOLTIP = 'rankedBattlesLeague'
    RANKED_BATTLES_EFFICIENCY_TOOLTIP = 'rankedBattlesEfficiency'
    RANKED_BATTLES_POSITION_TOOLTIP = 'rankedBattlesPosition'
    CALENDAR_TOOLTIP = 'calendarTooltip'
    MAPBOX_CALENDAR_TOOLTIP = 'mapboxCalendar'
    EPIC_BATTLE_CALENDAR_TOOLTIP = 'epicBattleCalendarTooltip'
    EVENT_BATTLES_CALENDAR_TOOLTIP = 'eventBattlesCalendar'

    def __init__(self, properties=0, commands=0):
        super(ModeSelectorTooltipsConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ModeSelectorTooltipsConstants, self)._initialize()
