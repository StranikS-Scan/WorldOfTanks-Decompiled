# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle_roles.py
from gui.shared.tooltips import ToolTipBaseData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView

class VehicleRolesTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(VehicleRolesTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.VEHICLE_ROLES)

    def getDisplayableData(self, roleID, *args, **kwargs):
        return DecoratedTooltipWindow(VehicleRolesTooltipView(roleID), useDecorator=False)
