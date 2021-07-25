# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/manual_chapter_view.py
import logging
from helpers import dependency
from skeletons.gui.game_control import IMapsTrainingController
from gui.doc_loaders.manual_xml_data_reader import ManualPageTypes
from account_helpers import AccountSettings
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.ManualChapterViewMeta import ManualChapterViewMeta
from gui.Scaleform.daapi.view.lobby.manual.manual_view_base import ManualViewBase
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
_logger = logging.getLogger(__name__)

class ManualChapterView(ManualViewBase, ManualChapterViewMeta):
    BC_HANGAR_GUIDE_CARD_SWIPE_SOUND_ID = 'bc_hangar_guide_card_swipe'
    BC_GUIDE_ELEMENT_BUTTON_SOUND_ID = 'bc_guide_element_button'
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def __init__(self, ctx=None):
        super(ManualChapterView, self).__init__(ctx)
        self.__chapterIndex = self._ctx['chapterIndex']
        self._pageIndex = self._ctx.get('pageIndex', None)
        self.chapterData = self.manualController.getChapterUIData(self.__chapterIndex)
        return

    def closeView(self):
        self._close()
        g_eventBus.handleEvent(events.ManualEvent(events.ManualEvent.CHAPTER_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)

    def pageButtonClicked(self, pageType):
        if pageType == ManualPageTypes.BOOTCAMP_PAGE:
            _logger.debug('ManualChapterView. Requested bootcamp start.')
            self.manualController.runBootcamp()
        elif pageType == ManualPageTypes.MAPS_TRAINING_PAGE:
            self.mapsTrainingController.selectMapsTrainingMode()

    def bootcampHighlighted(self):
        self.soundManager.playSound(self.BC_GUIDE_ELEMENT_BUTTON_SOUND_ID)

    def _populate(self):
        super(ManualChapterView, self)._populate()
        self.setData(self.__chapterIndex, self._pageIndex)
        g_eventBus.handleEvent(events.ManualEvent(events.ManualEvent.CHAPTER_OPENED), scope=EVENT_BUS_SCOPE.LOBBY)

    def setData(self, chapterIndex, pageIndex):
        data = self.markChapterPagesAsRead(self.chapterData)
        self.as_setInitDataS(data)
        pageIndex = pageIndex or 0
        self.as_showPageS(pageIndex)
        self.markPageAsRead(int(data['details'][pageIndex]['id']))

    def openVideo(self, url):
        webHandlers = webApiCollection(ui_web_api.CloseViewWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
        ctx = {'url': url,
         'webHandlers': webHandlers,
         'returnAlias': VIEW_ALIAS.MANUAL_CHAPTER_VIEW}
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MANUAL_BROWSER_VIEW), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def onPreviewClicked(self, url):
        self.openVideo(url)

    def onPageChanged(self, pageId):
        self.markPageAsRead(int(pageId))
        self.soundManager.playSound(self.BC_HANGAR_GUIDE_CARD_SWIPE_SOUND_ID)

    def markPageAsRead(self, pageId):
        chapters = AccountSettings.getManualUnreadPages()
        for chapter in chapters:
            if pageId in chapter:
                chapter.remove(pageId)
                AccountSettings.setManualUnreadPages(chapters)
                self.updatePaginator()
                break

    def getUnreadPages(self):
        return sum(AccountSettings.getManualUnreadPages(), [])

    def markChapterPagesAsRead(self, chapterUIData):
        allUnReadPages = self.getUnreadPages()
        for index, page in enumerate(chapterUIData['details']):
            if chapterUIData['pages'][index]['hasNewContent'] and int(page['id']) not in allUnReadPages:
                chapterUIData['pages'][index]['hasNewContent'] = False

        return chapterUIData

    def updatePaginator(self):
        data = self.markChapterPagesAsRead(self.chapterData)
        self.as_setPagesS(data['pages'])
