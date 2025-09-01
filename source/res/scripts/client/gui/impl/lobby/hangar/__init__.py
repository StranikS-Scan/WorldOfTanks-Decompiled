# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/__init__.py
from __future__ import absolute_import

def getStateMachineRegistrators():
    from gui.impl.lobby.hangar.states_registration import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass
