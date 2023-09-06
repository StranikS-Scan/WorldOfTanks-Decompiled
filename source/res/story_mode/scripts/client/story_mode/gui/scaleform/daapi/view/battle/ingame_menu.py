# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/ingame_menu.py
import BattleReplay
from BWUtil import AsyncReturn
from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow, showLeaverReplayWindow, closeDialogWindow as closePrematureLeaveWindow
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.INGAMEMENU_CONSTANTS import INGAMEMENU_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowLogger
from wg_async import wg_async, wg_await
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.genConsts.INTERFACE_STATES import INTERFACE_STATES
from helpers import dependency
from gui.Scaleform.locale.MENU import MENU

class StoryModeIngameMenu(IngameMenu):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, ctx=None):
        super(StoryModeIngameMenu, self).__init__(ctx)
        self._uiLogger = WindowLogger(LogWindows.ESCAPE_MENU)

    @wg_async
    def quitBattleClick(self):
        self.as_setVisibilityS(False)
        self._uiLogger.logClick(LogButtons.QUIT)
        confirmExitDialog = showLeaverReplayWindow if BattleReplay.isPlaying() else self._openConfirmExitDialog
        wantToExit = yield wg_await(confirmExitDialog())
        if wantToExit:
            self._uiLogger.logClick(LogButtons.SKIP)
            self._storyModeCtrl.skipOnboarding()
        else:
            self.destroy()

    def onCounterNeedUpdate(self):
        pass

    def settingsClick(self):
        self._uiLogger.logClick(LogButtons.SETTINGS)
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STORY_MODE_SETTINGS_WINDOW)), scope=EVENT_BUS_SCOPE.BATTLE)

    def helpClick(self):
        self._uiLogger.logClick(LogButtons.HELP)
        super(StoryModeIngameMenu, self).helpClick()

    def cancelClick(self):
        self._uiLogger.logClick(LogButtons.CLOSE)
        super(StoryModeIngameMenu, self).cancelClick()

    def _populate(self):
        super(StoryModeIngameMenu, self)._populate()
        self._uiLogger.logOpen(info=None if self.__isForceOnboarding else LogButtons.GARAGE)
        return

    def _dispose(self):
        self._uiLogger.logClose()
        closePrematureLeaveWindow()
        super(StoryModeIngameMenu, self)._dispose()

    def _setServerSettings(self):
        if self.__isForceOnboarding or BattleReplay.isPlaying():
            serverName = ''
            tooltipFullData = ''
            state = INTERFACE_STATES.HIDE_ALL_SERVER_INFO
            self.as_setServerSettingS(serverName, tooltipFullData, state)
        else:
            super(StoryModeIngameMenu, self)._setServerSettings()

    def _setServerStats(self):
        if not (self.__isForceOnboarding or BattleReplay.isPlaying()):
            super(StoryModeIngameMenu, self)._setServerStats()

    def _setMenuButtonsLabels(self):
        if BattleReplay.isPlaying():
            quitRes = R.strings.menu.ingame_menu.buttons.replayExit()
        elif self.__isForceOnboarding:
            quitRes = R.strings.sm_battle.ingameMenu.buttons.quit()
        else:
            quitRes = R.strings.menu.ingame_menu.buttons.logoff()
        self.as_setMenuButtonsLabelsS(helpLabel=MENU.INGAME_MENU_BUTTONS_HELP, settingsLabel=MENU.INGAME_MENU_BUTTONS_SETTINGS, cancelLabel=MENU.INGAME_MENU_BUTTONS_BACK, quitLabel=backport.text(quitRes))

    def _setMenuButtons(self):
        if self.__isForceOnboarding and not BattleReplay.isPlaying():
            buttons = (INGAMEMENU_CONSTANTS.SETTINGS, INGAMEMENU_CONSTANTS.QUIT, INGAMEMENU_CONSTANTS.CANCEL)
        else:
            buttons = (INGAMEMENU_CONSTANTS.QUIT,
             INGAMEMENU_CONSTANTS.SETTINGS,
             INGAMEMENU_CONSTANTS.HELP,
             INGAMEMENU_CONSTANTS.CANCEL)
        self.as_setMenuButtonsS(buttons)

    @wg_async
    def _openConfirmExitDialog(self):
        window = showResDialogWindow(title=R.strings.sm_battle.confirmExit.title(), confirm=R.strings.sm_battle.confirmExit.exit(), cancel=R.strings.sm_battle.confirmExit.stay())
        result = yield wg_await(window)
        raise AsyncReturn(result)

    @property
    def __isForceOnboarding(self):
        return self.sessionProvider.arenaVisitor.extra.getValue('isForceOnboarding')
