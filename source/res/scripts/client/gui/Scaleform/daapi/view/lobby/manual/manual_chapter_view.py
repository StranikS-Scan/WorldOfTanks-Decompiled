# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/manual_chapter_view.py
import logging
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.ManualChapterViewMeta import ManualChapterViewMeta
from gui.Scaleform.daapi.view.lobby.manual.manual_view_base import ManualViewBase
_logger = logging.getLogger(__name__)

class ManualChapterView(ManualViewBase, ManualChapterViewMeta):
    __background_alpha__ = 1

    def __init__(self, ctx=None):
        super(ManualChapterView, self).__init__(ctx)
        self.__chapterIndex = self._ctx['chapterIndex']
        self._pageIndex = self._ctx.get('pageIndex', None)
        return

    def closeView(self):
        self._close()
        g_eventBus.handleEvent(events.ManualEvent(events.ManualEvent.CHAPTER_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)

    def bootcampButtonClicked(self):
        _logger.debug('ManualChapterView. Requested bootcamp start.')
        self.manualController.runBootcamp()

    def _populate(self):
        super(ManualChapterView, self)._populate()
        self.setData(self.__chapterIndex, self._pageIndex)
        g_eventBus.handleEvent(events.ManualEvent(events.ManualEvent.CHAPTER_OPENED), scope=EVENT_BUS_SCOPE.LOBBY)

    def setData(self, chapterIndex, pageIndex):
        data = self.manualController.getChapterUIData(chapterIndex)
        self.as_setInitDataS(data)
        self.as_showPageS(pageIndex or 0)
