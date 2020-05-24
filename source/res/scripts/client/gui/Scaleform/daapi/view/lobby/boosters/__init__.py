# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.boosters.BoostersPanelComponent import BoostersPanelComponent
    return (ViewSettings(VIEW_ALIAS.BOOSTERS_PANEL, BoostersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
