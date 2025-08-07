# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/album_card_view.py
import logging
import weakref
import typing
from adisp import adisp_process
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.links import URLMacros
from gui.impl.gen.view_models.views.lobby.wot_anniversary.album_card_view_model import AlbumCardViewModel, ContentType
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import showImageView
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency, getClientLanguage
from shared_utils import nextTick
from skeletons.gui.game_control import IExternalLinksController
from skeletons.gui.wot_anniversary import IWotAnniversaryController
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.wot_anniversary.content_loader.models import DayContent
_logger = logging.getLogger(__name__)

class AlbumCardPresenter(SubModelPresenter):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)
    __externalLinks = dependency.descriptor(IExternalLinksController)

    def __init__(self, viewModel, parentView, closeCallback):
        self.__dayConfig = None
        self.__content = None
        self.__isFlow = False
        self.__closeCallback = closeCallback
        super(AlbumCardPresenter, self).__init__(viewModel, weakref.proxy(parentView))
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onPreview, self.__onPreview), (self.viewModel.onLearn, self.__onLearn))

    def initialize(self, dayID, isFlow, *args, **kwargs):
        super(AlbumCardPresenter, self).initialize(*args, **kwargs)
        self.__isFlow = isFlow
        daysConfig = self.__wotAnniversaryController.config.days
        if not 0 <= dayID < len(daysConfig):
            _logger.error('Invalid day ID - %s', dayID)
            nextTick(self.__close)()
            return
        else:
            self.__content = self.__wotAnniversaryController.cdnCacheMgr.getContentByDayID(dayID + 1)
            if self.__content is None or not self.__content.isContentLoaded():
                _logger.error('There are not image and localizations for the screen loading.')
                nextTick(self.__close)()
                return
            lang = getClientLanguage()
            titleLoc = ''
            descriptionLoc = ''
            if self.__content.localizations.has_key('title'):
                titleLoc = self.__content.localizations['title'].readString(lang)
            if self.__content.localizations.has_key('description'):
                descriptionLoc = self.__content.localizations['description'].readString(lang)
            self.__dayConfig = daysConfig[dayID]
            with self.viewModel.transaction() as tx:
                tx.setName(titleLoc)
                tx.setDescription(descriptionLoc)
                tx.setImageSrc(self.__content.image)
                tx.setLearning(bool(self.__dayConfig.additionalInfoUrl))
                if self.__dayConfig.videoUrl:
                    tx.setContentType(ContentType.VIDEO)
                else:
                    tx.setContentType(ContentType.IMAGE)
            return

    def clear(self):
        self.__dayConfig = None
        self.__content = None
        self.__closeCallback = None
        self.__isFlow = False
        super(AlbumCardPresenter, self).clear()
        return

    def __onPreview(self):
        if self.viewModel.getContentType() != ContentType.VIDEO:
            if self.__content is None or not self.__content.isContentLoaded():
                _logger.error('There are not image for the opening of ImageView.')
                return

            def closeCallback():
                if self.viewModel is not None:
                    self.viewModel.setIsBlurred(False)
                return

            self.viewModel.setIsBlurred(True)
            showImageView(imageSrc=self.__content.imageLarge, parent=self.getParentWindow(), closeCallback=closeCallback)
            return
        else:
            showBrowserOverlayView(self.__dayConfig.videoUrl, alias=VIEW_ALIAS.WOT_ANNIVERSARY_VIDEO_VIEW, parent=self.getParentWindow())
            return

    @adisp_process
    def __onLearn(self):
        processedUrl = yield URLMacros().parse(self.__dayConfig.additionalInfoUrl)
        self.__externalLinks.open(processedUrl)

    def __onClose(self):
        self.__close()

    def __close(self):
        self.__closeCallback(self.__isFlow)
