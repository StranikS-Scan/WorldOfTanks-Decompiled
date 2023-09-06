# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/base_prb_view.py
from logging import getLogger
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import LobbyHeader
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.skeletons.story_mode_controller import IStoryModeController
from frameworks.wulf import ViewSettings, ViewFlags
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class BasePrbView(ViewImpl):
    LAYOUT_ID = None
    MODEL_CLASS = None
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *_, **__):
        super(BasePrbView, self).__init__(settings=ViewSettings(layoutID=self.LAYOUT_ID, model=self.MODEL_CLASS(), flags=ViewFlags.LOBBY_SUB_VIEW))

    def _onLoading(self, *args, **kwargs):
        super(BasePrbView, self)._onLoading(*args, **kwargs)
        LobbyHeader.toggleMenuVisibility(HeaderMenuVisibilityState.NOTHING)

    def _finalize(self):
        if not self._isInCustomization():
            LobbyHeader.toggleMenuVisibility(HeaderMenuVisibilityState.ALL)
        super(BasePrbView, self)._finalize()

    def _isInCustomization(self):
        return self._appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION)) is not None

    @adisp_process
    def _quit(self):
        self.destroyWindow()
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None:
            result = yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                _logger.error('Failed to select random')
        return
