# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/inputChecker/__init__.py
from gui.Scaleform.daapi.view.lobby.inputChecker.InputChecker import InputChecker
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings

class INPUT_CHECKER_ALIASES(object):
    INPUT_CHECKER = 'inputCheckerComponent'


def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(INPUT_CHECKER_ALIASES.INPUT_CHECKER, InputChecker, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
