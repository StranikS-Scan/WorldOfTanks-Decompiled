# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/container_view.py
import logging
from advent_calendar.gui.impl.lobby.feature.base_view import BaseView
from advent_calendar.gui.impl.lobby.feature.tooltips.advent_calendar_simple_tooltip_view import AdventCalendarSimpleTooltip
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class AdventCalendarContainerView(BaseView):

    def __init__(self, settings):
        self.__componentPresenters = []
        super(AdventCalendarContainerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarContainerView, self)._onLoading(args, kwargs)
        self.__componentPresenters.extend(self._registerSubModels())
        for presenter in self.__componentPresenters:
            presenter.initialize()

    def _finalize(self):
        for presenter in self.__componentPresenters:
            presenter.finalize()
            presenter.clear()

        self.__componentPresenters = None
        super(AdventCalendarContainerView, self)._finalize()
        return

    def createToolTipContent(self, event, contentID):
        for presenter in self.__componentPresenters:
            content = presenter.createToolTipContent(event, contentID)
            if content is not None:
                return content

        if contentID == R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarSimpleTooltip():
            payload = event.getArgument('payload', '')
            if not payload:
                _logger.error("Parameter 'payload' is omitted")
                return
            return AdventCalendarSimpleTooltip(payload)
        else:
            return super(AdventCalendarContainerView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        for presenter in self.__componentPresenters:
            content = presenter.createPopOverContent(event)
            if content is not None:
                return content

        return

    def _registerSubModels(self):
        raise NotImplementedError
