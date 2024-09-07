# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/early_access.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.early_access.tooltips.early_access_currency_tooltip_view import EarlyAccessCurrencyTooltipView
from gui.impl.lobby.early_access.tooltips.early_access_entry_point_tooltip_view import EarlyAccessEntryPointTooltipView
from gui.impl.lobby.early_access.tooltips.early_access_vehicle_locked_tooltip import EarlyAccessVehicleLockedTooltip
from gui.impl.pub import ViewImpl
from gui.shared.tooltips import ToolTipBaseData
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessCommonInfoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EarlyAccessCommonInfoTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_COMMON_INFO)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(ViewImpl(ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessCommonDescriptionTooltip(), model=ViewModel())), useDecorator=False)


class EarlyAccessPausedTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EarlyAccessPausedTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_PAUSED)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(ViewImpl(ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessEntryPointPausedTooltip(), model=ViewModel())), useDecorator=False)


class EarlyAccessVehicleLockedTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EarlyAccessVehicleLockedTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_VEHICLE_LOCKED)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EarlyAccessVehicleLockedTooltip(), useDecorator=False)


class EarlyAccessCarouselVehiclePostProgressionTooltipData(ToolTipBaseData):
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self, context):
        super(EarlyAccessCarouselVehiclePostProgressionTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_CAROUSEL_VEHICLE_POST_PROGRESSION)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EarlyAccessEntryPointTooltipView(showOnlyPostProgression=True), useDecorator=False)


class EarlyAccessCurrencyTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EarlyAccessCurrencyTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_CURRENCY)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EarlyAccessCurrencyTooltipView(), useDecorator=False)


class EarlyAccessEntryPointTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(EarlyAccessEntryPointTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.EARLY_ACCESS_ENTRY_POINT)

    def getDisplayableData(self, vehicleCD, *args, **kwargs):
        return DecoratedTooltipWindow(EarlyAccessEntryPointTooltipView(vehicleCD), useDecorator=False)
