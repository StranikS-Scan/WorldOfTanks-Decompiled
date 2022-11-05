# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/__init__.py
from constants import ARENA_GUI_TYPE, PREBATTLE_TYPE, QUEUE_TYPE
from fun_random.gui import fun_gui_constants
from fun_random.gui.impl.lobby.tooltips.fun_random_progression_tooltip_view import FunRandomProgressionTooltipView
from fun_random.gui.prb_control.entities.pre_queue.entity import FunRandomEntity, FunRandomEntryPoint
from fun_random.gui.prb_control.entities.squad.entity import FunRandomSquadEntity, FunRandomSquadEntryPoint
from fun_random.gui.prb_control.formatters.invites import FunPrbInviteHtmlTextFormatter
from fun_random.gui.prb_control.storages.fun_random_storage import FunRandomStorage
from fun_random.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addFunRandomBattleType
from fun_random.gui.impl.lobby.feature.fun_random_entry_point_view import isFunRandomEntryPointAvailable
from fun_random.gui.impl.lobby.mode_selector.items.fun_random_mode_selector_item import FunRandomSelectorItem
from fun_random.gui.impl.lobby.platoon.view.fun_platoon_members_view import FunRandomMembersView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from gui.prb_control.prb_utils import initPrbGetter, initPrebbatleSelector, addPrebattleRequestType
from gui.prb_control.storages import makeQueueName
from gui.shared.system_factory import registerModeSelectorItem, registerModeSelectorTooltips, registerPrbInviteHtmlFormatter, registerPrbStorage, registerPlatoonView, registerUnitEntryPointByType, registerUnitEntity, registerEntryPointValidator
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES

def registerFunRandomPrebattles(personality):
    initPrbGetter(fun_gui_constants.ATTR_NAME, ARENA_GUI_TYPE.FUN_RANDOM, PREBATTLE_TYPE.FUN_RANDOM, fun_gui_constants.PrebattleActionName.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM, fun_gui_constants.FunctionalFlag.FUN_RANDOM, personality)
    initPrebbatleSelector(fun_gui_constants.ATTR_NAME, QUEUE_TYPE.FUN_RANDOM, fun_gui_constants.SelectorBattleTypes.FUN_RANDOM, fun_gui_constants.PrebattleActionName.FUN_RANDOM, (ModeSelectorColumns.COLUMN_1, 20), FunRandomEntity, FunRandomEntryPoint, addFunRandomBattleType, personality)
    registerModeSelectorItem(fun_gui_constants.PrebattleActionName.FUN_RANDOM, FunRandomSelectorItem)
    registerModeSelectorTooltips([ModeSelectorTooltipsConstants.FUN_RANDOM_CALENDAR_TOOLTIP, ModeSelectorTooltipsConstants.FUN_RANDOM_REWARDS], {R.views.fun_random.lobby.tooltips.FunRandomProgressionTooltipView(): FunRandomProgressionTooltipView})
    registerPlatoonView(PREBATTLE_TYPE.FUN_RANDOM, FunRandomMembersView)
    registerUnitEntryPointByType(PREBATTLE_TYPE.FUN_RANDOM, FunRandomSquadEntryPoint)
    registerUnitEntity(PREBATTLE_TYPE.FUN_RANDOM, FunRandomSquadEntity)
    registerPrbStorage(makeQueueName(QUEUE_TYPE.FUN_RANDOM), FunRandomStorage())
    registerPrbInviteHtmlFormatter(PREBATTLE_TYPE.FUN_RANDOM, FunPrbInviteHtmlTextFormatter)
    addPrebattleRequestType(fun_gui_constants.PRB_REQ_TYPE_ATTR_NAME, fun_gui_constants.RequestType.CHANGE_FUN_SUB_MODE, personality)
    registerEntryPointValidator(FUNRANDOM_ALIASES.FUN_RANDOM_ENTRY_POINT, isFunRandomEntryPointAvailable)
