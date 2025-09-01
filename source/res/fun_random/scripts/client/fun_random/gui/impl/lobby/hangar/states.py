# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/states.py


def registerStates(machine):
    from gui.impl.lobby.hangar.states import LegacyHangarState
    from fun_random.gui.fun_gui_constants import FUNCTIONAL_FLAG
    LegacyHangarState.addLegacyHangarFunctionalFlag(FUNCTIONAL_FLAG.FUN_RANDOM)


def registerTransitions(machine):
    pass
