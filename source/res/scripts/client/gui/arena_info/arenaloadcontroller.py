# Embedded file name: scripts/client/gui/arena_info/ArenaLoadController.py
import BigWorld
from gui.arena_info import IArenaController

class ArenaLoadController(IArenaController):

    def spaceLoadStarted(self):
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattleLoading()
        BigWorld.wg_setReducedFpsMode(True)

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattle()
