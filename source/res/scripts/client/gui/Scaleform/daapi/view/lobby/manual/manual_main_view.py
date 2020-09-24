# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/manual_main_view.py
import logging
from gui.Scaleform.daapi.view.meta.ManualMainViewMeta import ManualMainViewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.manual.manual_view_base import ManualViewBase
_logger = logging.getLogger(__name__)

class ManualMainView(ManualViewBase, ManualMainViewMeta):
    __background_alpha__ = 1

    def closeView(self):
        self._close()
        self.manualController.clear()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onChapterOpenedS(self, chapterIndex):
        _logger.debug('ManualMainView. Chapter selected: %s', chapterIndex)
        shared_events.openManualPage(chapterIndex)

    def _populate(self):
        super(ManualMainView, self)._populate()
        chapters = self.manualController.getChaptersUIData()
        self.as_setChaptersS(chapters)
        self.as_setPageBackgroundS(RES_ICONS.MAPS_ICONS_MANUAL_MAINPAGE_BACKGROUND)
        self.addListener(events.ManualEvent.CHAPTER_OPENED, self.__onChapterOpened, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)
        ctx = self._ctx
        if ctx:
            self.manualController.showChapterView(ctx['chapterIndex'], ctx['pageIndex'])

    def _dispose(self):
        super(ManualMainView, self)._dispose()
        self.removeListener(events.ManualEvent.CHAPTER_OPENED, self.__onChapterOpened, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)

    def __onChapterClosed(self, _):
        self.as_showCloseBtnS(True)

    def __onChapterOpened(self, _):
        self.as_showCloseBtnS(False)
