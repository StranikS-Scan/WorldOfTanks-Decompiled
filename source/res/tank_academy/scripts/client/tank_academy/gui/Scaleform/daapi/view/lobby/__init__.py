# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from tank_academy.gui.impl.lobby.tank_academy.tank_academy_entry_point_view import TankAcademyEntryPointWidget
    return (ComponentSettings(HANGAR_ALIASES.TANK_ACADEMY_ENTRY_POINT, TankAcademyEntryPointWidget, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
