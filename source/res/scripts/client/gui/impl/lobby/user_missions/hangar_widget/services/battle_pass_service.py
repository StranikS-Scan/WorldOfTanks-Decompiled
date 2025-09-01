# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/battle_pass_service.py
from PlayerEvents import g_playerEvents
from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_eventBus, events
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.resource_well import IResourceWellController

class BattlePassService(IBattlePassService):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        super(BattlePassService, self).__init__()
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer

    def onPrbEntitySwitched(self):
        self._onBattlePassEvent()

    def isVisible(self):
        isVisible = not self.__battlePassController.isDisabled()
        isVisible &= self._isValidBattleTypeForBattlePass()
        return isVisible

    def startListening(self):
        self.startGlobalListening()
        self.__battlePassController.onBattlePassSettingsChange += self._onBattlePassEvent
        self.__battlePassController.onSeasonStateChanged += self._onBattlePassEvent
        self.__resourceWell.onEventUpdated += self._onBattlePassEvent

    def stopListening(self):
        self.stopGlobalListening()
        self.__battlePassController.onBattlePassSettingsChange -= self._onBattlePassEvent
        self.__battlePassController.onSeasonStateChanged -= self._onBattlePassEvent
        self.__resourceWell.onEventUpdated -= self._onBattlePassEvent

    def finalize(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.stopListening()

    def _isValidBattleTypeForBattlePass(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return False
        else:
            prbEntity = prbDispatcher.getEntity()
            return False if prbEntity is None else self.__battlePassController.isValidBattleType(prbEntity)

    def _onBattlePassEvent(self, *_):
        self.onBattlePassChanged()

    def __onLobbyInited(self, *_):
        self.startListening()

    def __onAccountBecomeNonPlayer(self):
        self.stopListening()
