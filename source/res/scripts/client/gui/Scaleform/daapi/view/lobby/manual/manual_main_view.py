# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/manual_main_view.py
import logging
from account_helpers import AccountSettings
from gui.Scaleform.daapi.view.meta.ManualMainViewMeta import ManualMainViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.Scaleform.daapi.view.lobby.manual.manual_view_base import ManualViewBase
_logger = logging.getLogger(__name__)

class ManualMainView(ManualViewBase, ManualMainViewMeta):

    @staticmethod
    def addCounter(param):
        chapters = AccountSettings.getManualUnreadPages()
        index = 0
        for chapter in chapters:
            length = len(chapter)
            param[index]['counter'] = str(length) if length > 0 else ''
            index += 1

        return param

    def closeView(self):
        self._close()

    def onChapterOpenedS(self, chapterIndex):
        _logger.debug('ManualMainView. Chapter selected: %s', chapterIndex)
        shared_events.openManualPage(chapterIndex)

    def _populate(self):
        super(ManualMainView, self)._populate()
        chapters = self.addCounter(self.chaptersUIData)
        self.as_setChaptersS(chapters)
        self.as_setPageBackgroundS(RES_ICONS.MAPS_ICONS_MANUAL_MAINPAGE_BACKGROUND)
        self.as_setDescrLabelBackBtnS(self.manualController.getDescrLabelBackBtn())
        self.as_showCloseBtnS(False)
        self.as_showBackBtnS(False)
        self.addListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)
        ctx = self._ctx
        if ctx and 'chapterIndex' in ctx:
            self.manualController.showChapterView(ctx['chapterIndex'], ctx['pageIndex'])

    def _dispose(self):
        super(ManualMainView, self)._dispose()
        self.removeListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.manualController.clear()

    def __onChapterClosed(self, _):
        chapters = self.addCounter(self.chaptersUIData)
        self.as_setChaptersS(chapters)
