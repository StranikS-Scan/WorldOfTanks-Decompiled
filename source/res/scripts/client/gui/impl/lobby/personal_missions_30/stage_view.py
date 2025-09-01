# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/stage_view.py
from typing import TYPE_CHECKING
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.assembling_video_view_model import AssemblingVideoViewModel
from gui.impl.lobby.personal_missions_30.views_helpers import setVideoOverlayOn, setVideoOverlayOff
from gui.impl.pub import ViewImpl, WindowImpl
if TYPE_CHECKING:
    from typing import Callable, Optional

class AssemblingVideoView(ViewImpl):

    def __init__(self, layoutID, operationID, stageNumber, closingCallback=None):
        self.operationID = operationID
        self.stageNumber = stageNumber
        self.closingCallback = closingCallback
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=AssemblingVideoViewModel())
        super(AssemblingVideoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AssemblingVideoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AssemblingVideoView, self)._onLoading()
        setVideoOverlayOn()
        with self.viewModel.transaction() as tx:
            tx.setOperationID(self.operationID)
            tx.setStageNumber(self.stageNumber)

    def _finalize(self):
        self.__startAssembling()
        setVideoOverlayOff()
        super(AssemblingVideoView, self)._finalize()

    def _getEvents(self):
        return super(AssemblingVideoView, self)._getEvents() + ((self.viewModel.startAssembling, self.__startAssembling),)

    def __startAssembling(self):
        if self.closingCallback is not None:
            self.closingCallback()
            self.closingCallback = None
        return


class AssemblingVideoViewWindow(WindowImpl):

    def __init__(self, operationID, stageNumber, closingCallback=None):
        super(AssemblingVideoViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=AssemblingVideoView(R.views.mono.personal_missions_30.assembling_video(), operationID, stageNumber, closingCallback=closingCallback), layer=WindowLayer.FULLSCREEN_WINDOW)
