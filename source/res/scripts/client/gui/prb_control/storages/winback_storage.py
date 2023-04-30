# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/winback_storage.py
from gui.prb_control.storages.local_storage import SessionStorage
from helpers import dependency
from skeletons.gui.game_control import IWinbackController

class WinbackStorage(SessionStorage):
    __winbackController = dependency.descriptor(IWinbackController)

    def isModeSelected(self):
        return super(WinbackStorage, self).isModeSelected() and self.isModeAvailable()

    def isModeAvailable(self):
        return self.__winbackController.isModeAvailable()

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isWinback()
