# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_notifier.py
import logging
from account_helpers.settings_core.settings_constants import GAME
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_control.controllers.arena_load_ctrl import IArenaLoadCtrlListener
from gui.battle_control.controllers.battle_notifier_ctrl import IBattleNotifierListener
from gui.impl.battle.battle_notifier.battle_notifier_view import BattleNotifierView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class BattleNotifier(InjectComponentAdaptor, IArenaLoadCtrlListener, IBattleNotifierListener):
    __slots__ = ('__isArenaLoaded', '__isEnabledByServer')
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(BattleNotifier, self).__init__()
        self.__isArenaLoaded = False
        self.__isEnabledByServer = self.lobbyContext.getServerSettings().isBattleNotifierEnabled()

    def _onPopulate(self):
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._updateInjectedViewState()

    def _makeInjectView(self):
        return BattleNotifierView()

    def arenaLoadCompleted(self):
        self.__isArenaLoaded = True
        if self._injectView is not None:
            self._injectView.arenaLoadCompleted()
        return

    def resultsNotificationReceived(self, results):
        if self._injectView is not None:
            self._injectView.addBattleResults(results)
        return

    def __onSettingsChanged(self, diff):
        if GAME.ENABLE_BATTLE_NOTIFIER in diff.keys():
            self._updateInjectedViewState()

    def _updateInjectedViewState(self):
        if not self.__isEnabledByServer:
            return
        else:
            isEnabledInBattle = self.settingsCore.getSetting(GAME.ENABLE_BATTLE_NOTIFIER)
            if isEnabledInBattle and self.getInjectView() is None:
                self._createInjectView()
                if self.__isArenaLoaded:
                    self._injectView.arenaLoadCompleted()
            if not isEnabledInBattle:
                self._destroyInjected()
            return

    def _dispose(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(BattleNotifier, self)._dispose()
