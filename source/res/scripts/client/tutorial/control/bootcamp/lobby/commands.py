# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/commands.py
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from tutorial.loader import g_loader
from tutorial.logger import LOG_ERROR

def overrideHangarMenuButtons(buttonsListVarID=None):
    _getTutorialManager().overrideHangarMenuButtons(_getListByVarID(buttonsListVarID))


def overrideHeaderMenuButtons(buttonsListVarID=None):
    _getTutorialManager().overrideHeaderMenuButtons(_getListByVarID(buttonsListVarID))


def setHangarHeaderEnabled(enabled):
    _getTutorialManager().setHangarHeaderEnabled(enabled)


def overrideBattleSelectorHint(overrideType=None):
    _getTutorialManager().overrideBattleSelectorHint(overrideType)


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def _getTutorialManager(appLoader=None):
    return appLoader.getApp().tutorialManager


def _getListByVarID(varID):
    if varID is not None:
        tutorial = g_loader.tutorial
        varVal = tutorial.getVars().get(varID)
        if varVal is None:
            LOG_ERROR('variable not found', varID)
            return
        if isinstance(varVal, list):
            return varVal
        LOG_ERROR('variable value is not a list', varID, varVal)
    return
