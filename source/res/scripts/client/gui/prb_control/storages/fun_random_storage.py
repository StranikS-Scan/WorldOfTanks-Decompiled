# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/fun_random_storage.py
from constants import ARENA_GUI_TYPE
from gui.prb_control.storages.local_storage import SessionStorage
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomStorage(SessionStorage):
    _GUI_TYPE = ARENA_GUI_TYPE.FUN_RANDOM
    __funRandomController = dependency.descriptor(IFunRandomController)

    def isModeSelected(self):
        self._isSelected = self._isSelected and self.__funRandomController.isAvailable()
        return super(FunRandomStorage, self).isModeSelected()
