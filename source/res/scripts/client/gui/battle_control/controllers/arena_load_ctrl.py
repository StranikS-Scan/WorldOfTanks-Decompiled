# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_load_ctrl.py
import BigWorld
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency, uniprof
from skeletons.gameplay import IGameplayLogic, PlayerEventID
from skeletons.gui.game_control import IGameSessionController

class IArenaLoadCtrlListener(object):

    def arenaLoadCompleted(self):
        pass


class ArenaLoadController(IArenaVehiclesController, ViewComponentsController):
    gameSession = dependency.descriptor(IGameSessionController)
    gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self):
        super(ArenaLoadController, self).__init__()
        self.__arenaVisitor = None
        self.__isCompleted = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaVisitor = arenaVisitor
        BigWorld.wg_updateColorGrading()
        BigWorld.wg_enableGUIBackground(True, False)
        BigWorld.wg_setGUIBackground(battleCtx.getArenaScreenIcon())

    def stopControl(self):
        BigWorld.wg_enableGUIBackground(False, True)
        self._clear()

    def setViewComponents(self, *components):
        super(ArenaLoadController, self).setViewComponents(*components)
        if self._viewComponents and self.__isCompleted:
            for component in self._viewComponents:
                component.arenaLoadCompleted()

    def spaceLoadStarted(self):
        self.gameSession.incBattlesCounter()
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_ARENA_LOADING, arenaGuiType=self.__arenaVisitor.getArenaGuiType())
        BigWorld.wg_setReducedFpsMode(True)

    def invalidateArenaInfo(self):
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_ARENA_INFO, arenaGuiType=self.__arenaVisitor.getArenaGuiType())

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        self.__isCompleted = True
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_ARENA_LOADED, arenaGuiType=self.__arenaVisitor.getArenaGuiType())
        avatar_getter.setClientReady()
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        BigWorld.enableLoadingTimer(False)
        uniprof.exitFromRegion('avatar.arena.loading')
        BigWorld.wg_enableGUIBackground(False, False)
        uniprof.enterToRegion('avatar.arena.battle')
        BigWorld.wg_clearTextureReuseList()
        if self._viewComponents:
            for component in self._viewComponents:
                component.arenaLoadCompleted()

    def _clear(self):
        self.__arenaVisitor = None
        self.__isCompleted = False
        return


class ArenaLoadPlayer(ArenaLoadController):

    def stopControl(self):
        self._clear()


def createArenaLoadController(setup):
    return ArenaLoadPlayer() if setup.isReplayPlaying else ArenaLoadController()
