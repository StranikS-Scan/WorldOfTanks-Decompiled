# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/newbie_entry_point_controller.py
import logging
import typing
import BigWorld
from ExtensionsManager import g_extensionsManager
from helpers import dependency
from PlayerEvents import g_playerEvents
from story_mode.skeletons.story_mode_controller import IStoryModeController
from skeletons.gui.game_control import INewbieEntryPointController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class NewbieEntryPointController(INewbieEntryPointController):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def init(self):
        g_playerEvents.onAccountShowGUISkipped += self._onAccountShowGUISkipped

    def fini(self):
        g_playerEvents.onAccountShowGUISkipped -= self._onAccountShowGUISkipped

    def isNewbieStartPageEnabled(self):
        return g_extensionsManager.isExtensionEnabled('newbie_start_page') and self._lobbyContext.getServerSettings().newbieStartPageConfig.isEnabled

    def isStoryModeEnabled(self):
        return self._storyModeCtrl.isEnabled() and self._storyModeCtrl.joinToQueueFromLogin()

    def goToStoryModeQueue(self, guiCtx):
        if not self.isStoryModeEnabled():
            return
        self._storyModeCtrl.onAccountShowGUISkipped(guiCtx)

    def goToHangar(self, guiCtx):
        if guiCtx.get('skipShowGUI'):
            guiCtx['skipShowGUI'] = False
        g_playerEvents.onAccountShowGUI(guiCtx)

    def _onAccountShowGUISkipped(self, guiCtx):
        if self.isNewbieStartPageEnabled() and guiCtx.get('showIntroScreen', False):
            from newbie_start_page.gui.shared.event_dispatcher import showNewbieStartPage
            showNewbieStartPage(guiCtx)
        elif self.isStoryModeEnabled():
            self.goToStoryModeQueue(guiCtx)
        else:
            self.goToHangar(guiCtx)

    def setExperienceLevel(self, expLevel):
        if not self.isNewbieStartPageEnabled():
            _logger.error('Newbie start page is disabled.')
            return
        BigWorld.player().NewbieStartPageComponent.setInitialPlayerExperienceLevel(expLevel)
