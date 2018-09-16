# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/commands.py
from tutorial.loader import g_loader
from tutorial.logger import LOG_ERROR
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import TutorialEvent

def overrideHangarMenuButtons(buttonsListVarID=None):
    g_eventBus.handleEvent(TutorialEvent(TutorialEvent.OVERRIDE_HANGAR_MENU_BUTTONS, targetID=_getListByVarID(buttonsListVarID)), scope=EVENT_BUS_SCOPE.LOBBY)


def overrideHeaderMenuButtons(buttonsListVarID=None):
    g_eventBus.handleEvent(TutorialEvent(TutorialEvent.OVERRIDE_HEADER_MENU_BUTTONS, targetID=_getListByVarID(buttonsListVarID)), scope=EVENT_BUS_SCOPE.LOBBY)


def setHangarHeaderEnabled(enabled):
    g_eventBus.handleEvent(TutorialEvent(TutorialEvent.SET_HANGAR_HEADER_ENABLED, targetID=enabled), scope=EVENT_BUS_SCOPE.LOBBY)


def overrideBattleSelectorHint(overrideType=None):
    g_eventBus.handleEvent(TutorialEvent(TutorialEvent.OVERRIDE_BATTLE_SELECTOR_HINT, targetID=overrideType), scope=EVENT_BUS_SCOPE.LOBBY)


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
