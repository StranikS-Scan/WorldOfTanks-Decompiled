# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/vehicle_preview/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview.hb_vehicle_preview import HBVehiclePreviewPanel, HBVehicleRestorePanel

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(VEHPREVIEW_CONSTANTS.HB_PANEL_LINKAGE, HBVehiclePreviewPanel, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(VEHPREVIEW_CONSTANTS.HB_RESTORE_PANEL_LINKAGE, HBVehicleRestorePanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
