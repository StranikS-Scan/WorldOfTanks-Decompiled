# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/manual_view_base.py
import logging
from gui.Scaleform.daapi import LobbySubView
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency
from skeletons.gui.game_control import IManualController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class ManualViewBase(LobbySubView):
    __sound_env__ = LobbySubViewEnv
    __background_alpha__ = 1
    lobbyContext = dependency.descriptor(ILobbyContext)
    manualController = dependency.descriptor(IManualController)

    def __init__(self, ctx=None):
        super(ManualViewBase, self).__init__()
        self._ctx = ctx
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def closeView(self):
        raise NotImplementedError

    def _close(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.destroy()

    def __onServerSettingChanged(self, diff):
        if 'isManualEnabled' in diff:
            if not bool(diff['isManualEnabled']):
                self.closeView()
        if 'isBootcampEnabled' in diff:
            self.closeView()
