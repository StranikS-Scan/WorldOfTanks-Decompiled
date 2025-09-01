# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/__init__.py


def getStateMachineRegistrators():
    from gui.impl.lobby.mode_selector.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass
