# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/battle_control/controllers/races_help_controller.py
import typing
from races.gui.impl.battle.races_hud.races_help_window import RacesHelpWindow
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class RacesHelpController(IBattleController):
    __slots__ = ('__window',)

    def __init__(self, setup):
        super(RacesHelpController, self).__init__()
        self.__window = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.INGAME_HELP_CTRL

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def showIngameHelp(self, vehicle):
        if self.__window:
            self.__closeHelpWindow()
        else:
            self.__openHelpWindow()
        return True

    def canShow(self):
        return True

    def __openHelpWindow(self):
        self.__window = RacesHelpWindow(closeCallback=self.__closeCallback)
        self.__window.load()

    def __closeCallback(self):
        self.__window = None
        return

    def __closeHelpWindow(self):
        self.__window.destroy()
        self.__window = None
        return
