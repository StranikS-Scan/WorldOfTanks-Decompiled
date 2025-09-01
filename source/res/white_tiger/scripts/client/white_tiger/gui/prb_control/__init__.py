# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/__init__.py


def registerWhiteTigerPrbParams():
    from gui.impl.gen import R
    from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
    from gui.shared.system_factory import registerModeSelectorTooltips
    from white_tiger.gui.impl.lobby.tooltips.progression_widget_tooltip_view import ProgressionWidgetTooltipView
    from white_tiger.gui.impl.lobby.tooltips.ticket_tooltip_view import TicketToolTipViewLegacy
    registerModeSelectorTooltips([ModeSelectorTooltipsConstants.WHITE_TIGER_PROGRESSION_VIEW, ModeSelectorTooltipsConstants.WHITE_TIGER_BATTLES_CALENDAR_TOOLTIP], {R.views.white_tiger.lobby.tooltips.WidgetTooltipView(): ProgressionWidgetTooltipView,
     R.views.white_tiger.lobby.tooltips.TicketTooltipView(): TicketToolTipViewLegacy})
