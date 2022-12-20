# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from entry_point import EpicBattlesEntryPoint

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_ENTRY_POINT, EpicBattlesEntryPoint, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
