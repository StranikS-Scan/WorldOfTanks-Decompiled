# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
import BigWorld
import constants
import BattleReplay
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.INGAMEMENU_CONSTANTS import INGAMEMENU_CONSTANTS
from gui.battle_control.battle_session import BattleExitResult
from wg_async import wg_async, wg_await
from gui import DialogsInterface, GUI_SETTINGS
from gui import makeHtmlString
from account_helpers.counter_settings import getCountNewSettings
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.meta.IngameMenuMeta import IngameMenuMeta
from gui.Scaleform.genConsts.GLOBAL_VARS_MGR_CONSTS import GLOBAL_VARS_MGR_CONSTS
from gui.Scaleform.genConsts.INTERFACE_STATES import INTERFACE_STATES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import event_dispatcher as battle_event_dispatcher
from gui.shared import event_dispatcher as shared_event_dispatcher
from gui.shared import events
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IServerStatsController
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.battle.shared.premature_leave import showLeaverAliveWindow, showExitWindow, showLeaverReplayWindow, showComp7LeaverAliveWindow
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS

class IngameMenu(IngameMenuMeta, BattleGUIKeyHandler):
    serverStats = dependency.descriptor(IServerStatsController)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def onWindowClose(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def quitBattleClick(self):
        if self.app.varsManager.isTutorialRunning(GLOBAL_VARS_MGR_CONSTS.BATTLE):
            self.__doLeaveTutorial()
        else:
            self.__doLeaveArena()

    def settingsClick(self):
        shared_event_dispatcher.showSettingsWindow(redefinedKeyMode=True, isBattleSettings=True)

    def helpClick(self):
        battle_event_dispatcher.toggleHelp()

    def cancelClick(self):
        self.destroy()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def _populate(self):
        super(IngameMenu, self)._populate()
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._setServerSettings()
        self._setServerStats()
        self._setMenuButtonsLabels()
        self._setMenuButtons()
        return

    def __updateNewSettingsCount(self):
        newSettingsCount = getCountNewSettings()
        if newSettingsCount > 0:
            self.as_setCounterS([{'componentId': INGAMEMENU_CONSTANTS.SETTINGS,
              'count': str(newSettingsCount)}])
        else:
            self.as_removeCounterS([INGAMEMENU_CONSTANTS.SETTINGS])

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(IngameMenu, self)._dispose()
        return

    def _setServerSettings(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            serverName = ''
            tooltipFullData = ''
            state = INTERFACE_STATES.HIDE_ALL_SERVER_INFO
        else:
            tooltipBody = i18n.makeString(TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_FULL_BODY)
            tooltipFullData = makeTooltip(TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_FULL_HEADER, tooltipBody % {'servername': self.connectionMgr.serverUserName})
            serverName = makeHtmlString('html_templates:lobby/serverStats', 'serverName', {'name': self.connectionMgr.serverUserName})
            if constants.IS_SHOW_SERVER_STATS:
                state = INTERFACE_STATES.SHOW_ALL
            else:
                state = INTERFACE_STATES.HIDE_SERVER_STATS
        self.as_setServerSettingS(serverName, tooltipFullData, state)

    def _setServerStats(self):
        if constants.IS_SHOW_SERVER_STATS:
            self.as_setServerStatsS(*self.serverStats.getFormattedStats())

    def _setMenuButtonsLabels(self):
        if self.app.varsManager.isTutorialRunning(GLOBAL_VARS_MGR_CONSTS.BATTLE):
            quitLabel = MENU.LOBBY_MENU_BUTTONS_REFUSE_TRAINING
        elif BattleReplay.isPlaying():
            quitLabel = MENU.INGAME_MENU_BUTTONS_REPLAYEXIT
        else:
            quitLabel = MENU.INGAME_MENU_BUTTONS_LOGOFF
        self.as_setMenuButtonsLabelsS(MENU.INGAME_MENU_BUTTONS_HELP, MENU.INGAME_MENU_BUTTONS_SETTINGS, MENU.INGAME_MENU_BUTTONS_BACK, quitLabel)

    def _setMenuButtons(self):
        buttons = [INGAMEMENU_CONSTANTS.QUIT,
         INGAMEMENU_CONSTANTS.SETTINGS,
         INGAMEMENU_CONSTANTS.HELP,
         INGAMEMENU_CONSTANTS.CANCEL]
        self.as_setMenuButtonsS(buttons)

    @adisp_process
    def __doLeaveTutorial(self):
        result = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('refuseTraining', focusedID=DIALOG_BUTTON_ID.CLOSE))
        if result:
            self.fireEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING))
            self.destroy()

    @wg_async
    def __doLeaveArena(self):
        self.as_setVisibilityS(False)
        exitResult = self._getExitResult()
        if BattleReplay.isPlaying():
            result = yield wg_await(showLeaverReplayWindow())
        elif exitResult.isDeserter:
            isPlayerIGR = self.__isPlayerIGR(exitResult.playerInfo)
            result = yield wg_await(self._showLeaverAliveWindow(isPlayerIGR))
        else:
            result = yield wg_await(showExitWindow())
        if result:
            self.__doExit()
        else:
            self.destroy()

    def __doExit(self):
        self.sessionProvider.exit()
        self.destroy()

    def _getExitResult(self):
        return self.sessionProvider.getExitResult()

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        player = BigWorld.player()
        return showComp7LeaverAliveWindow() if player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.COMP7) else showLeaverAliveWindow(isPlayerIGR)

    @staticmethod
    def __isPlayerIGR(playerInfo):
        igrType = playerInfo.igrType if playerInfo else constants.IGR_TYPE.NONE
        return True if constants.IS_KOREA and GUI_SETTINGS.igrEnabled and igrType != constants.IGR_TYPE.NONE else False

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.INGAME_HELP:
            self.destroy()
