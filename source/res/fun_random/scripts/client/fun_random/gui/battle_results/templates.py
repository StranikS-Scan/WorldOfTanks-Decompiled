# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/templates.py
from fun_random.gui.battle_results import components
from gui.battle_results.components.base import ListMeta
from gui.battle_results.settings import BATTLE_RESULTS_RECORD
from gui.battle_results.templates import regular
FUN_RANDOM_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(3)
FUN_RANDOM_COMMON_STATS_BLOCK.addComponent(3, components.FunRandomArenaFullNameItem('arenaStr'))
FUN_RANDOM_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(8, 17)
FUN_RANDOM_PERSONAL_STATS_BLOCK.addComponent(8, components.FunRandomPersonalVehiclesStatsBlock(ListMeta(), 'statValues', BATTLE_RESULTS_RECORD.PERSONAL))
FUN_RANDOM_PERSONAL_STATS_BLOCK.addComponent(17, components.FunRandomDynamicPremiumState('dynamicPremiumState'))
