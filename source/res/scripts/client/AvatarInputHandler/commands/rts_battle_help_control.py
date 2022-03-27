# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/rts_battle_help_control.py
import CommandMapping
import Keys
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.impl.battle.rts.rts_help_view import RtsHelpView
from gui.impl.battle.rts.rts_help_view import HelpWindow
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
from helpers import dependency

class RtsBattleHelpControl(InputHandlerCommand):
    appLoader = dependency.descriptor(IAppLoader)
    _HELP_SCREEN_WHITELISTED_KEYS = [CommandMapping.CMD_MOVE_FORWARD,
     CommandMapping.CMD_MOVE_BACKWARD,
     CommandMapping.CMD_ROTATE_LEFT,
     CommandMapping.CMD_ROTATE_RIGHT]

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        visible = isRtsHelpVisible()
        if cmdMap.isFired(CommandMapping.CMD_SHOW_HELP, key) and isDown and mods == 0 and not visible:
            app = self.appLoader.getApp()
            isForbidden = app.hasGuiControlModeConsumers(BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU, VIEW_ALIAS.INGAME_MENU)
            if not isForbidden:
                showRTSBattleHelp()
            return True
        if visible:
            if isDown and mods == 0 and cmdMap.isFired(CommandMapping.CMD_SHOW_HELP, key) or key == Keys.KEY_ESCAPE:
                hideRTSBattleHelp()
                return True
            return not cmdMap.isFiredList(self._HELP_SCREEN_WHITELISTED_KEYS, key)


def isRtsHelpVisible():
    view = __getView()
    return view and not view.getParentWindow().isHidden()


def showRTSBattleHelp():
    view = __getView()
    if view:
        view.getParentWindow().show()
    else:
        HelpWindow().load()


def hideRTSBattleHelp():
    view = __getView()
    if view:
        view.getParentWindow().hide()


def __getView():
    guiLoader = dependency.instance(IGuiLoader)
    return guiLoader.windowsManager.getViewByLayoutID(R.views.battle.rts.HelpView())
