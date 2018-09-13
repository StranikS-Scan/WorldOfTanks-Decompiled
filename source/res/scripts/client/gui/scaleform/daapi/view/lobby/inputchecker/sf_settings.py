# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/inputChecker/sf_settings.py
from gui.Scaleform.daapi.view.lobby.inputChecker.InputChecker import InputChecker
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, ViewSettings

class INPUT_CHECKER_ALIASES(object):
    INPUT_CHECKER = 'inputCheckerComponent'


def getViewSettings():
    return [ViewSettings(INPUT_CHECKER_ALIASES.INPUT_CHECKER, InputChecker, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return []
