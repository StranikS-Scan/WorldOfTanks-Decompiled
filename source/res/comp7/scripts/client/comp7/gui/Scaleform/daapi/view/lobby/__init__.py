# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_modifiers_panel import Comp7ModifiersPanelInject
    from gui.impl.lobby.comp7.tournaments_widget import TournamentsWidgetComponent
    return (ComponentSettings(HANGAR_ALIASES.COMP7_MODIFIERS_PANEL, Comp7ModifiersPanelInject, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.COMP7_TOURNAMENT_BANNER, TournamentsWidgetComponent, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
