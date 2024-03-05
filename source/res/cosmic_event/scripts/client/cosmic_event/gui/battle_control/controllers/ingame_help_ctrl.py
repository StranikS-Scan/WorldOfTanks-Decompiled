# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/ingame_help_ctrl.py
import typing
import CommandMapping
from cosmic_event.gui.impl.battle.cosmic_hud.cosmic_battle_help_view import CosmicHelpWindow
from gui import InputHandler
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class CosmicIngameHelpController(IBattleController):
    __slots__ = ('__window',)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, setup):
        super(CosmicIngameHelpController, self).__init__()
        self.__window = None
        return

    def __handleKeyUpEvent(self, event):
        if CommandMapping.g_instance.isFired(CommandMapping.CMD_SHOW_HELP, event.key):
            self.__closeHelpWindow()

    def __openHelpWindow(self):
        if self.__window is not None:
            return
        else:
            self.__window = CosmicHelpWindow()
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

    def showIngameHelp(self, vehicle):
        self.__openHelpWindow()
        return True

    def canShow(self):
        battleApp = self.__appLoader.getDefBattleApp()
        return False if battleApp is None else not bool(battleApp.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU)))
