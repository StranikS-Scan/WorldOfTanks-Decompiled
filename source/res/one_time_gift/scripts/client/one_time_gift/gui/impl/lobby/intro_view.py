# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/intro_view.py
import logging
from gui.sounds.filters import switchVideoOverlaySoundFilter
from helpers import dependency
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView
from shared_utils import safeCall
from one_time_gift.gui.impl.gen.view_models.views.lobby.intro_view_model import IntroViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
from one_time_gift.gui.impl.lobby.meta_view.sub_view_base import SubViewBase
from one_time_gift.gui.shared.hide_tooltips import hideTooltips
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
_logger = logging.getLogger(__name__)

class IntroView(SubViewBase):
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)

    @property
    def viewId(self):
        return MainViews.INTRO

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def initialize(self, onConfirmCallback=None, onCloseCallback=None, onErrorCallback=None, showIntroVideo=False):
        _logger.debug('IntroView::initialize')
        super(IntroView, self).initialize(onConfirmCallback, onCloseCallback, onErrorCallback)
        self.__showIntroVideo = showIntroVideo
        self.__updateViewModel()
        if showIntroVideo:
            self.__onShowVideo()

    def _getEvents(self):
        return super(IntroView, self)._getEvents() + ((self.viewModel.onShowVideo, self.__onShowVideo),
         (self.viewModel.onContinue, self.__onContinue),
         (self.viewModel.onClose, self._onClose),
         (self.__oneTimeGiftController.onSettingsChanged, self.__onSettingsChanged),
         (self.__oneTimeGiftController.onEntryPointUpdated, self.__onSettingsChanged))

    def __onContinue(self):
        _logger.debug('IntroView::__onContinue')
        safeCall(self._onConfirmCallback)

    def __onSettingsChanged(self, *_, **__):
        _logger.debug('IntroView::__onSettingsChanged')
        error = self.__oneTimeGiftController.getAvailabilityError()
        if error is not None:
            safeCall(self._onErrorCallback, error=error)
            return
        else:
            self.__updateViewModel()
            return

    def __onShowVideo(self):
        _logger.debug('IntroView::__onShowVideo')
        if not hasattr(GUI_SETTINGS, 'oneTimeGift'):
            _logger.warning('GUI_SETTINGS does not contain oneTimeGift section')
            return
        hideTooltips()
        switchVideoOverlaySoundFilter(True)
        introVideoUrl = GUI_SETTINGS.oneTimeGift.get('introVideo')
        url = GUI_SETTINGS.checkAndReplaceWebBridgeMacros(introVideoUrl) if introVideoUrl else introVideoUrl
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY, parent=self.getParentWindow(), callbackOnClose=self.__onVideoClosed)

    def __updateViewModel(self):
        endTime = self.__oneTimeGiftController.getEndTime()
        self.viewModel.setEndTime(endTime)
        if not self.__showIntroVideo:
            self.viewModel.setShowAnimation(False)

    def __onVideoClosed(self):
        if self.__showIntroVideo:
            self.viewModel.setShowAnimation(True)
        switchVideoOverlaySoundFilter(False)
