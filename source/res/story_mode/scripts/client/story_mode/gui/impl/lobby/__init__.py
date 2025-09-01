# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/__init__.py


def getStateMachineRegistrators():
    from story_mode.gui.impl.lobby.states import registerStates
    from story_mode.gui.impl.lobby.states import registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass
