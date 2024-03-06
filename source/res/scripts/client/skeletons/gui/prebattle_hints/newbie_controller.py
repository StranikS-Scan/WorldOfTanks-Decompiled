# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/prebattle_hints/newbie_controller.py
from skeletons.gui.prebattle_hints.controller import IPrebattleHintsControlStrategy

class INewbiePrebattleHintsController(IPrebattleHintsControlStrategy):

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def onConfirmationWindowShown(self):
        raise NotImplementedError
