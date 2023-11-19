# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/base_prb_view.py
from logging import getLogger
from adisp import adisp_process
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.skeletons.story_mode_controller import IStoryModeController
from frameworks.wulf import ViewSettings, ViewFlags
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class BasePrbView(ViewImpl, LobbyHeaderVisibility):
    LAYOUT_ID = None
    MODEL_CLASS = None
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *_, **__):
        super(BasePrbView, self).__init__(settings=ViewSettings(layoutID=self.LAYOUT_ID, model=self.MODEL_CLASS(), flags=ViewFlags.LOBBY_SUB_VIEW))

    def _onLoading(self, *args, **kwargs):
        super(BasePrbView, self)._onLoading(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)

    def _finalize(self):
        self.resumeLobbyHeader(self.uniqueID)
        super(BasePrbView, self)._finalize()

    @adisp_process
    def _quit(self):
        self.destroyWindow()
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None:
            result = yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                _logger.error('Failed to select random')
        return
