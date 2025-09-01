# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/slide.py
import typing
import game_loading_bindings
from frameworks.state_machine import StateFlags
from gui.game_loading import loggers
from gui.game_loading.resources.consts import InfoStyles
from gui.game_loading.state_machine.const import TickingMode
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.states.base import BaseViewResourcesTickingState, BaseState
from gui.impl.utils.path import normalizeGfImagePath
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
     'infoStyle': InfoStyles.DEFAULT.value,
     'showSmallLogo': settings.showSmallLogo}
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

    @property
    def timeLeft(self):
        pass

    def setImage(self, image):
        self._image = image
        _logger.debug('[%s] image [%s] set.', self, image)

    def _onEntered(self, event):
        super(StaticSlideState, self)._onEntered(event)
        self._image = self._image or self._images.get()
        _showImage(self._image, self._imageViewSettings)

    def _onExited(self):
        self._images.reset()
        super(StaticSlideState, self)._onExited()


class SlideState(BaseViewResourcesTickingState):
    __slots__ = ('_firstImageToShow', '_firstShownImage', '_lastShownImage', '_imageViewSettings', '_startFromFirstShownImage')

    def __init__(self, stateID, images, imageViewSettings, flags=StateFlags.UNDEFINED, tickingMode=TickingMode.MANUAL, onCompleteEvent=None, startFromFirstShownImage=False):
        super(SlideState, self).__init__(stateID=stateID, resources=images, flags=flags, tickingMode=tickingMode, minDurationEventTime=imageViewSettings.minimalDuration, onCompleteEvent=onCompleteEvent)
        self._startFromFirstShownImage = startFromFirstShownImage
        self._lastShownImage = None
        self._firstShownImage = None
        self._firstImageToShow = None
        self._imageViewSettings = imageViewSettings
        return

    @property
    def lastShownImage(self):
        return self._lastShownImage

    def setImage(self, image):
        self._firstImageToShow = image
        _logger.debug('[%s] image [%s] set.', self, image)

    def _stop(self):
        if self._startFromFirstShownImage:
            self.setImage(self._firstShownImage)
        super(SlideState, self)._stop()

    def _selectResource(self):
        if not self._firstImageToShow:
            return super(SlideState, self)._selectResource()
        else:
            image = self._firstImageToShow
            self._firstImageToShow = None
            _logger.debug('[%s] first image to show selected <%s>.', self, image)
            return image

    def _beforeView(self):
        self._resetWaiting()
        super(SlideState, self)._beforeView()

    def _view(self, image):
        if not self._firstShownImage:
            self._firstShownImage = image
        self._lastShownImage = image
        _showImage(image, self._imageViewSettings)

    def _onMinDurationTimeReached(self):
        self._releaseWaiting()
        super(SlideState, self)._onMinDurationTimeReached()
