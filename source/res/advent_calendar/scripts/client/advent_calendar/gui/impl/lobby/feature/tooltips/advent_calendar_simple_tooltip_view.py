# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/tooltips/advent_calendar_simple_tooltip_view.py
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.simple_tooltip_model import SimpleTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class AdventCalendarSimpleTooltip(ViewImpl[SimpleTooltipModel]):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarSimpleTooltip(), model=SimpleTooltipModel(), args=args, kwargs=kwargs)
        super(AdventCalendarSimpleTooltip, self).__init__(settings)

    def _onLoading(self, payload):
        with self.getViewModel().transaction() as vm:
            vm.setPayload(payload)
