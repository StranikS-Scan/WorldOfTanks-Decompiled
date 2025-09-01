# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/__init__.py


def getStateMachineRegistrators():
    from last_stand.gui.impl.lobby.states import registerStates
    from last_stand.gui.impl.lobby.states import registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass
