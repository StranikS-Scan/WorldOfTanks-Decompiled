# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_load_ctrl.py
import BigWorld
from gui import game_control
from gui.app_loader import g_appLoader
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class ArenaLoadController(IArenaLoadController):

    def __init__(self):
        super(ArenaLoadController, self).__init__()
        self.__arenaVisitor = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaVisitor = arenaVisitor

    def stopControl(self):
        self.__arenaVisitor = None
        return

    def spaceLoadStarted(self):
        game_control.g_instance.gameSession.incBattlesCounter()
        g_appLoader.showBattleLoading(arenaGuiType=self.__arenaVisitor.getArenaGuiType())
        BigWorld.wg_setReducedFpsMode(True)

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        g_appLoader.showBattle()
        BigWorld.wg_clearTextureReuseList()
