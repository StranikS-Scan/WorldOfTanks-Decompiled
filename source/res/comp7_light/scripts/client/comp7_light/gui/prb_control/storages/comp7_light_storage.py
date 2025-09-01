# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/storages/comp7_light_storage.py
from comp7_light_constants import ARENA_GUI_TYPE
from gui.prb_control.storages.local_storage import SessionStorage
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightStorage(SessionStorage):
    _GUI_TYPE = ARENA_GUI_TYPE.COMP7_LIGHT
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def isModeSelected(self):
        return self.__comp7LightController.isAvailable() and super(Comp7LightStorage, self).isModeSelected()

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.guiType == self._GUI_TYPE
