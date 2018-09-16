# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_load_ctrl.py
import BigWorld
import constants
from gui.app_loader import g_appLoader
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController

class IArenaLoadCtrlListener(object):

    def arenaLoadCompleted(self):
        pass


class ArenaLoadController(IArenaVehiclesController, ViewComponentsController):
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        super(ArenaLoadController, self).__init__()
        self.__arenaVisitor = None
        self.__isCompleted = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaVisitor = arenaVisitor

    def stopControl(self):
        self.__arenaVisitor = None
        return

    def setViewComponents(self, *components):
        super(ArenaLoadController, self).setViewComponents(*components)
        if self._viewComponents and self.__isCompleted:
            for cmp in self._viewComponents:
                cmp.arenaLoadCompleted()

    def spaceLoadStarted(self):
        self.gameSession.incBattlesCounter()
        g_appLoader.createBattle(arenaGuiType=self.__arenaVisitor.getArenaGuiType())
        BigWorld.wg_setReducedFpsMode(True)

    def invalidateArenaInfo(self):
        g_appLoader.showBattleLoading()

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        self.__isCompleted = True
        g_appLoader.showBattlePage()
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        BigWorld.enableLoadingTimer(False)
        BigWorld.wg_clearTextureReuseList()
        if self._viewComponents:
            for cmp in self._viewComponents:
                cmp.arenaLoadCompleted()
