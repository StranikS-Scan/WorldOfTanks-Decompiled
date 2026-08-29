# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/__init__.py
from gui.impl.gen import R
from gui.shared.system_factory import registerModeSelectorTooltips
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from white_tiger.gui.impl.lobby.tooltips.wt_event_header_widget_tooltip_view import WtEventHeaderWidgetTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView

def registerWtOtherParams():
    registerModeSelectorTooltips([ModeSelectorTooltipsConstants.FUN_RANDOM_CALENDAR_TOOLTIP, ModeSelectorTooltipsConstants.FUN_RANDOM_REWARDS], {R.views.white_tiger.lobby.tooltips.ProgressionEntryPointTooltip(): WtEventHeaderWidgetTooltipView,
     R.views.white_tiger.lobby.tooltips.StampTooltipView(): WtEventStampTooltipView})
