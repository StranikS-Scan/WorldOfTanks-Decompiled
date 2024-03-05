# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_modifiers_panel import Comp7ModifiersPanelInject
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_vehicle_parameters import Comp7VehicleParameters
    return (ComponentSettings(HANGAR_ALIASES.COMP7_MODIFIERS_PANEL, Comp7ModifiersPanelInject, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.COMP7_VEHICLE_PARAMETERS, Comp7VehicleParameters, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
