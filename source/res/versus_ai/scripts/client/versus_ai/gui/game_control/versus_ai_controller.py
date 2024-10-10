# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/game_control/versus_ai_controller.py
import typing
from functools import partial
import adisp
import BigWorld
from account_helpers.AccountSettings import AccountSettings, HAS_LEFT_VERSUS_AI
from constants import QUEUE_TYPE, PREBATTLE_TYPE, Configs
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency, server_settings
from PlayerEvents import g_playerEvents
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IVersusAIController, IWinbackController
from versus_ai.gui.versus_ai_gui_constants import NOOB_MIN_BATTLES_COUNT, FUNCTIONAL_FLAG
if typing.TYPE_CHECKING:
    from helpers.server_settings import VersusAIConfig

class VersusAIController(IVersusAIController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VersusAIController, self).__init__()
        self.__callbackID = None
        return

    def init(self):
        super(VersusAIController, self).init()
        g_playerEvents.onDossiersResync += self.__switchModeForNoob

    def fini(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_playerEvents.onDossiersResync -= self.__switchModeForNoob
        super(VersusAIController, self).fini()
        return

    def onLobbyInited(self, _):
        self.startGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__updateMode()

    def onAccountBecomeNonPlayer(self):
        super(VersusAIController, self).onAccountBecomeNonPlayer()
        self.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def onPrbEntitySwitching(self):
        if self.__isVersusAIMode():
            AccountSettings.setSettings(HAS_LEFT_VERSUS_AI, True)

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isVersusAIPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.VERSUS_AI)

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().versusAIConfig

    @staticmethod
    def __shouldBeDefaultModeIfWinbacker():
        winbackController = dependency.getInstanceIfHas(IWinbackController)
        return winbackController.versusAIModeShouldBeDefault() if winbackController else False

    def shouldBeDefaultMode(self):
        if not self.isEnabled():
            return False
        if self.__shouldBeDefaultModeIfWinbacker():
            return True
        if self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() >= NOOB_MIN_BATTLES_COUNT:
            AccountSettings.setSettings(HAS_LEFT_VERSUS_AI, True)
            return False
        return self.__canBeDefaultModeForNoob()

    def __shouldSwitchModeToRandomForNoob(self):
        return self.isEnabled() and not self.__shouldBeDefaultModeIfWinbacker() and not AccountSettings.getSettings(HAS_LEFT_VERSUS_AI) and self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() >= NOOB_MIN_BATTLES_COUNT

    def __canBeDefaultModeForNoob(self):
        return not AccountSettings.getSettings(HAS_LEFT_VERSUS_AI) and self.getConfig().isDefaultModeForNoob

    def __selectRandomBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            self.__callbackID = BigWorld.callback(0, partial(self.__doSelectRandomPrb, dispatcher))
            return

    def __switchModeForNoob(self):
        if self.__isVersusAIMode() and self.__shouldSwitchModeToRandomForNoob():
            self.__selectRandomBattle()

    @adisp.adisp_process
    def __doSelectRandomPrb(self, dispatcher):
        self.__callbackID = None
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        return

    def __isVersusAIMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            return state.isInPreQueue(queueType=QUEUE_TYPE.VERSUS_AI) or state.isInUnit(PREBATTLE_TYPE.VERSUS_AI)

    @server_settings.serverSettingsChangeListener(Configs.VERSUS_AI_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__updateMode()

    def __updateMode(self):
        if self.__isVersusAIMode():
            if not self.isEnabled() or self.__shouldSwitchModeToRandomForNoob():
                self.__selectRandomBattle()
