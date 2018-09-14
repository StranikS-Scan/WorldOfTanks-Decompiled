# Embedded file name: scripts/client/gui/battle_control/ArenaLoadController.py
import BigWorld
from gui import game_control
from gui.battle_control.arena_info.interfaces import IArenaLoadController
import BattleReplay

class ArenaLoadController(IArenaLoadController):

    def __init__(self, isMultiTeam = False):
        super(ArenaLoadController, self).__init__()
        self.__isMultiTeam = isMultiTeam

    def spaceLoadStarted(self):
        game_control.g_instance.gameSession.incBattlesCounter()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattleLoading(self.__isMultiTeam)
        BigWorld.wg_setReducedFpsMode(True)

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattle()
        BigWorld.wg_clearTextureReuseList()
        BigWorld.wg_synchronizeParicleSystem()
        if BattleReplay.isPlaying:
            BattleReplay.g_replayCtrl.onArenaLoaded()
