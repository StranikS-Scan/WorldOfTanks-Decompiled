# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_parent_view.py
import logging
from gui.impl.gen import R
from gui.impl.lobby.advent_calendar_v2.advent_calendar_view import AdventCalendarView
from gui.impl.lobby.advent_calendar_v2.tooltips.advent_calendar_simple_tooltip_view import AdventCalendarSimpleTooltip
_logger = logging.getLogger(__name__)

class AdventCalendarParentView(AdventCalendarView):

    def __init__(self, settings):
        self.__componentPresenters = []
        super(AdventCalendarParentView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarParentView, self)._onLoading(args, kwargs)
        self.__componentPresenters.extend(self._registerSubModels())
        for presenter in self.__componentPresenters:
            presenter.initialize()

    def _finalize(self):
        for presenter in self.__componentPresenters:
            presenter.finalize()
            presenter.clear()

        self.__componentPresenters = None
        super(AdventCalendarParentView, self)._finalize()
        return

    def createToolTipContent(self, event, contentID):
        for presenter in self.__componentPresenters:
            content = presenter.createToolTipContent(event, contentID)
            if content is not None:
                return content

        if contentID == R.views.lobby.advent_calendar.tooltips.AdventCalendarSimpleTooltip():
            payload = event.getArgument('payload', '')
            if not payload:
                _logger.error("Parameter 'payload' is omitted")
                return
            return AdventCalendarSimpleTooltip(payload)
        else:
            return super(AdventCalendarParentView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        for presenter in self.__componentPresenters:
            content = presenter.createPopOverContent(event)
            if content is not None:
                return content

        return

    def _registerSubModels(self):
        raise NotImplementedError
