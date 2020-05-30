# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/craftmachine_controller.py
import logging
from adisp import process
from constants import EnhancementsConfig as config
from helpers import dependency
from gui.wgcg.craftmachine.contexts import CraftmachineModulesInfoCtx
from skeletons.gui.game_control import ICraftmachineController
from skeletons.gui.web import IWebController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class CraftmachineController(ICraftmachineController):
    __webController = dependency.descriptor(IWebController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(CraftmachineController, self).__init__()
        self.__modules = {}
        self.__enabledSync = True
        self.__enabled = False

    def onConnected(self):
        self.__lobbyCtx.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def onDisconnected(self):
        self.__lobbyCtx.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def onLobbyInited(self, event):
        self.__onServerSettingsChange(self.__lobbyCtx.getServerSettings().getSettings())

    def onAccountBecomePlayer(self):
        if self.__enabled and self.__enabledSync:
            self.__updateModulesInfo()

    def getModuleName(self, module):
        return self.__modules.get(str(module), '')

    def __onServerSettingsChange(self, diff):
        clansDiff = diff.get(config.SECTION_NAME, {})
        if config.ENABLED in clansDiff:
            self.__enabled = clansDiff[config.ENABLED]
            self.onAccountBecomePlayer()

    @process
    def __updateModulesInfo(self):
        response = yield self.__webController.sendRequest(ctx=CraftmachineModulesInfoCtx())
        if response.isSuccess():
            self.__enabledSync = False
            data = response.getData() or {}
            for key, element in data.iteritems():
                self.__modules[key] = element.get('localizations', {}).get('name', '')

        else:
            _logger.warning('Failed to update modules data for craftmachine. Code: %s.', response.getCode())
