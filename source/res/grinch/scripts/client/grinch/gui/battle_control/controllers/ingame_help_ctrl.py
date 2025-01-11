# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/controllers/ingame_help_ctrl.py
import typing
import CommandMapping
from grinch.gui.impl.battle.grinch_help_view import GrinchHelpWindow
from gui import InputHandler
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class GrinchIngameHelpController(IBattleController):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__window',)

    def __init__(self, setup):
        super(GrinchIngameHelpController, self).__init__()
        self.__window = None
        return

    def __handleKeyUpEvent(self, event):
        if CommandMapping.g_instance.isFired(CommandMapping.CMD_SHOW_HELP, event.key):
            self.__closeHelpWindow()

    def __openHelpWindow(self):
        if self.__window is not None:
            return
        else:
            self.__window = GrinchHelpWindow()
            self.__window.load()
            return

    def __closeHelpWindow(self):
        if self.__window is None:
            return
        else:
            self.__window.destroy()
            self.__window = None
            return

    def getControllerID(self):
        return BATTLE_CTRL_ID.INGAME_HELP_CTRL

    def startControl(self, *args):
        InputHandler.g_instance.onKeyUp += self.__handleKeyUpEvent

    def stopControl(self):
        InputHandler.g_instance.onKeyUp -= self.__handleKeyUpEvent
        self.__closeHelpWindow()

    def canShow(self):
        battleApp = self.__appLoader.getDefBattleApp()
        return False if battleApp is None else not bool(battleApp.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU)))

    def showIngameHelp(self, vehicle):
        self.__openHelpWindow()
        return True
