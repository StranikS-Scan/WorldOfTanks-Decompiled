# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/slide.py
import time
import typing
import game_loading_bindings
from frameworks.state_machine import StateFlags
from gui.game_loading import loggers
from gui.game_loading.common import normalizeGfImagePath
from gui.game_loading.resources.consts import InfoStyles
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.states.base import BaseState, BaseViewResourcesTickingState
if typing.TYPE_CHECKING:
    from frameworks.state_machine import StateEvent
    from gui.game_loading.resources.models import LocalImageModel
    from gui.game_loading.resources.base import BaseResources
_logger = loggers.getStatesLogger()

def _showImage(image, settings):
    imagePath = normalizeGfImagePath(image.imageRelativePath)
    if not imagePath:
        _logger.warning('Broken image path: %s.', imagePath)
        return
    if not game_loading_bindings.isViewOpened():
        _logger.debug('Opening GF view.')
        game_loading_bindings.createLoadingView()
    data = {'backgroundPath': imagePath,
     'text': image.localizationText or '',
     'description': image.descriptionText or '',
     'contentState': settings.contentState,
     'transitionTime': image.transition,
     'ageRatingPath': settings.ageRatingPath,
     'info': settings.info,
     'infoStyle': InfoStyles.DEFAULT.value}
    game_loading_bindings.setViewData(data)
    _logger.debug('Image [%s] shown.', image)


class StaticSlideState(BaseState):
    __slots__ = ('_images', '_image', '_imageViewSettings')

    def __init__(self, stateID, images, imageViewSettings, flags=StateFlags.UNDEFINED):
        super(StaticSlideState, self).__init__(stateID=stateID, flags=flags)
        self._images = images
        self._image = None
        self._imageViewSettings = imageViewSettings
        return

    @property
    def lastShownImage(self):
        return self._image

    def setImage(self, image):
        self._image = image
        _logger.debug('[%s] image [%s] set.', self, image)

    def _onEntered(self):
        super(StaticSlideState, self)._onEntered()
        self._image = self._image or self._images.get()
        _showImage(self._image, self._imageViewSettings)

    def _onExited(self):
        self._images.reset()
        super(StaticSlideState, self)._onExited()


class SlideState(BaseViewResourcesTickingState):
    __slots__ = ('_image', '_imageViewSettings', '_isImageOverridden')

    def __init__(self, stateID, images, imageViewSettings, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(SlideState, self).__init__(stateID=stateID, resources=images, flags=flags, isSelfTicking=isSelfTicking, onCompleteEvent=onCompleteEvent)
        self._image = None
        self._imageViewSettings = imageViewSettings
        self._isImageOverridden = False
        return

    @property
    def lastShownImage(self):
        return self._image

    @property
    def timeLeft(self):
        return max(self._nextTickTime - time.time(), 0)

    def setImage(self, image):
        self._image = image
        self._nextTickTime = time.time() + image.minShowTimeSec
        self._isImageOverridden = True
        _logger.debug('[%s] image [%s] set.', self, image)

    def _onEntered(self):
        super(SlideState, self)._onEntered()
        if self._isImageOverridden and self._image:
            self._isImageOverridden = False
            self._view(self._image)

    def _view(self, image):
        self._image = image
        _showImage(image, self._imageViewSettings)
