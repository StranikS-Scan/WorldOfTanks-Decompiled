# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/__init__.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from fun_random.gui import fun_gui_constants
from fun_random.gui.prb_control.formatters.invites import FunPrbInviteHtmlTextFormatter
from fun_random.gui.prb_control.storages.fun_random_storage import FunRandomStorage
from fun_random.gui.impl.lobby.tooltips.fun_random_progression_tooltip_view import FunRandomProgressionTooltipView
from gui.prb_control.storages import makeQueueName
from gui.impl.gen import R
from gui.shared.system_factory import registerPrbInviteHtmlFormatter, registerPrbStorage, registerModeSelectorTooltips
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants

def registerFunRandomOthersParams(personality):
    registerModeSelectorTooltips([ModeSelectorTooltipsConstants.FUN_RANDOM_CALENDAR_TOOLTIP, ModeSelectorTooltipsConstants.FUN_RANDOM_REWARDS], {R.views.fun_random.lobby.tooltips.FunRandomProgressionTooltipView(): FunRandomProgressionTooltipView})
    registerPrbStorage(makeQueueName(QUEUE_TYPE.FUN_RANDOM), FunRandomStorage())
    registerPrbInviteHtmlFormatter(PREBATTLE_TYPE.FUN_RANDOM, FunPrbInviteHtmlTextFormatter)
