# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/tooltips/advent_calendar_simple_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.advent_calendar_simple_tooltip_model import AdventCalendarSimpleTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class AdventCalendarSimpleTooltip(ViewImpl[AdventCalendarSimpleTooltipModel]):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.advent_calendar.tooltips.AdventCalendarSimpleTooltip())
        settings.model = AdventCalendarSimpleTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdventCalendarSimpleTooltip, self).__init__(settings)

    def _onLoading(self, payload):
        with self.getViewModel().transaction() as vm:
            vm.setPayload(payload)
