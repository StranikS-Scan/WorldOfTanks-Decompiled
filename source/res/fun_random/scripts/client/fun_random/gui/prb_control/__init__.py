# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/__init__.py
from constants import ARENA_GUI_TYPE, PREBATTLE_TYPE, QUEUE_TYPE
from fun_random.gui.prb_control import prb_config
from fun_random.gui.prb_control.entities.pre_queue.entity import FunRandomEntity, FunRandomEntryPoint
from fun_random.gui.prb_control.entities.squad.entity import FunRandomSquadEntity, FunRandomSquadEntryPoint
from fun_random.gui.prb_control.formatters.invites import FunPrbInviteHtmlTextFormatter
from fun_random.gui.prb_control.storages.fun_random_storage import FunRandomStorage
from fun_random.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addFunRandomBattleType
from fun_random.gui.impl.lobby.feature.fun_random_entry_point_view import isFunRandomEntryPointAvailable
from fun_random.gui.impl.lobby.mode_selector.items.fun_random_mode_selector_item import FunRandomSelectorItem
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.prb_control.prb_utils import initPrbGetter, initPrebbatleSelector
from gui.prb_control.storages import makeQueueName
from gui.shared.system_factory import registerModSelectorItem, registerPrbInviteHtmlFormatter, registerUnitEntryPoint, registerUnitEntryPointByType, registerUnitEntity, registerPrbStorage, registerEntryPointValidator
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES

def registerFunRandomPrebattles(personality):
    initPrbGetter(prb_config.ATTR_NAME, ARENA_GUI_TYPE.FUN_RANDOM, PREBATTLE_TYPE.FUN_RANDOM, prb_config.PrebattleActionName.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM, prb_config.FunctionalFlag.FUN_RANDOM, personality)
    initPrebbatleSelector(prb_config.ATTR_NAME, QUEUE_TYPE.FUN_RANDOM, prb_config.SelectorBattleTypes.FUN_RANDOM, prb_config.PrebattleActionName.FUN_RANDOM, (ModeSelectorColumns.COLUMN_1, 20), FunRandomEntity, FunRandomEntryPoint, addFunRandomBattleType, personality)
    registerModSelectorItem(prb_config.PrebattleActionName.FUN_RANDOM, FunRandomSelectorItem)
    registerUnitEntryPoint(prb_config.PrebattleActionName.FUN_RANDOM_SQUAD, FunRandomSquadEntryPoint)
    registerUnitEntryPointByType(PREBATTLE_TYPE.FUN_RANDOM, FunRandomSquadEntryPoint)
    registerUnitEntity(PREBATTLE_TYPE.FUN_RANDOM, FunRandomSquadEntity)
    registerPrbStorage(makeQueueName(QUEUE_TYPE.FUN_RANDOM), FunRandomStorage())
    registerPrbInviteHtmlFormatter(PREBATTLE_TYPE.FUN_RANDOM, FunPrbInviteHtmlTextFormatter)
    registerEntryPointValidator(FUNRANDOM_ALIASES.FUN_RANDOM_ENTRY_POINT, isFunRandomEntryPointAvailable)
