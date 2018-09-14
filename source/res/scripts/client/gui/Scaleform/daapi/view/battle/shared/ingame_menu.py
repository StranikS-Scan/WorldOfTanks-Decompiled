# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
import constants
import BattleReplay
from adisp import process
from gui import DialogsInterface, GUI_SETTINGS
from gui import makeHtmlString
from gui.Scaleform.daapi.view.common.settings.new_settings_counter import getNewSettings
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.deserter_meta import IngameDeserterDialogMeta
from gui.Scaleform.daapi.view.meta.IngameMenuMeta import IngameMenuMeta
from gui.Scaleform.genConsts.GLOBAL_VARS_MGR_CONSTS import GLOBAL_VARS_MGR_CONSTS
from gui.Scaleform.genConsts.INTERFACE_STATES import INTERFACE_STATES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import event_dispatcher as battle_event_dispatcher
from gui.shared import event_dispatcher as shared_event_dispatcher
from gui.shared import events
from gui.shared.formatters import text_styles
from gui.shared.formatters.icons import makeImageTag
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IServerStatsController
from gui.Scaleform.locale.MENU import MENU

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
        shared_event_dispatcher.showSettingsWindow(redefinedKeyMode=True)

    def helpClick(self):
        self.destroy()
        battle_event_dispatcher.toggleHelp()

    def cancelClick(self):
        self.destroy()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def _populate(self):
        super(IngameMenu, self)._populate()
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        self.__setServerSettings()
        self.__setServerStats()
        self.__setMenuButtonsLabels()
        return

    def __updateNewSettingsCount(self):
        newSettingsCount = len(getNewSettings())
        if newSettingsCount > 0:
            self.as_setSettingsBtnCounterS(str(newSettingsCount))
        else:
            self.as_removeSettingsBtnCounterS()

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        super(IngameMenu, self)._dispose()
        return

    def __setServerSettings(self):
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

    def __setServerStats(self):
        if constants.IS_SHOW_SERVER_STATS:
            self.as_setServerStatsS(*self.serverStats.getFormattedStats())

    def __setMenuButtonsLabels(self):
        if self.app.varsManager.isTutorialRunning(GLOBAL_VARS_MGR_CONSTS.BATTLE):
            quitLabel = MENU.LOBBY_MENU_BUTTONS_REFUSE_TRAINING
        elif BattleReplay.isPlaying():
            quitLabel = MENU.INGAME_MENU_BUTTONS_REPLAYEXIT
        else:
            quitLabel = MENU.INGAME_MENU_BUTTONS_LOGOFF
        self.as_setMenuButtonsLabelsS(MENU.INGAME_MENU_BUTTONS_HELP, MENU.INGAME_MENU_BUTTONS_SETTINGS, MENU.INGAME_MENU_BUTTONS_BACK, quitLabel)

    @process
    def __doLeaveTutorial(self):
        result = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('refuseTraining', focusedID=DIALOG_BUTTON_ID.CLOSE))
        if result:
            self.fireEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING))
            self.destroy()

    @process
    def __doLeaveArena(self):
        exitResult = self.sessionProvider.getExitResult()
        if exitResult.playerInfo is not None:
            igrType = exitResult.playerInfo.igrType
        else:
            igrType = constants.IGR_TYPE.NONE
        if constants.IS_KOREA and GUI_SETTINGS.igrEnabled and igrType != constants.IGR_TYPE.NONE:
            i18nKey = 'quitBattleIGR'
        else:
            i18nKey = 'quitBattle'
        if exitResult.isDeserter:
            result = yield DialogsInterface.showDialog(IngameDeserterDialogMeta(i18nKey + '/deserter', focusedID=DIALOG_BUTTON_ID.CLOSE))
        elif BattleReplay.isPlaying():
            result = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('quitReplay', focusedID=DIALOG_BUTTON_ID.CLOSE))
        else:
            result = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('quitBattle', focusedID=DIALOG_BUTTON_ID.CLOSE))
        if result:
            self.__doExit()
        return

    def __doExit(self):
        self.sessionProvider.exit()
        self.destroy()
