# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/init_client/client_loading_stub.py
import typing
import BigWorld
import game_loading_bindings
from shared_utils import safeCancelCallback
from helpers.time_utils import MS_IN_SECOND
from gui.game_loading import loggers
from gui.game_loading.state_machine.const import GameLoadingStates
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.states.slide import StaticSlideState
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.images import CdnImagesResources
_logger = loggers.getStatesLogger()

class ClientLoadingStubState(StaticSlideState):
    __slots__ = ('_minDurationTimerId',)

    def __init__(self, images):
        super(ClientLoadingStubState, self).__init__(GameLoadingStates.CLIENT_INIT_LOADING_STUB.value, images, ImageViewSettingsModel(showSmallLogo=False, showVfx=False))
        self._minDurationTimerId = None
        return

    def clear(self):
        self._cancelMinDurationTimer()
        super(ClientLoadingStubState, self).clear()

    def _onEntered(self):
        super(ClientLoadingStubState, self)._onEntered()
        game_loading_bindings.bringLoadingViewToTop()
        self._minDurationTimerId = BigWorld.callback(self._image.transition / float(MS_IN_SECOND), self._fireMinimumDurationEvent)

    def _onExited(self):
        self._cancelMinDurationTimer()
        super(ClientLoadingStubState, self)._onExited()

    def _fireMinimumDurationEvent(self):
        self._cancelMinDurationTimer()
        self._releaseWaiting()

    def _cancelMinDurationTimer(self):
        if self._minDurationTimerId is not None:
            safeCancelCallback(self._minDurationTimerId)
            self._minDurationTimerId = None
        return
