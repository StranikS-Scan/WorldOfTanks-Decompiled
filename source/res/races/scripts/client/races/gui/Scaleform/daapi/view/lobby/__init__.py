# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/lobby/__init__.py
from races.gui.Scaleform.daapi.view.lobby.races_banner_entry_point import RacesBannerEntryPoint
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
__all__ = []

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(HANGAR_ALIASES.RACES_BANNER_ENTRY_POINT, RacesBannerEntryPoint, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
