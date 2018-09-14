# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/fallout.py
from gui.battle_results.components import base
from gui.battle_results.components import common
from gui.battle_results.components import personal
from gui.battle_results.components import shared
from gui.battle_results.templates import regular
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
regular.FINISH_RESULT_VO_META.bind(common.FalloutFinishResultBlock)
FALLOUT_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(0, 3, 7, 9, 10)
FALLOUT_COMMON_STATS_BLOCK.addComponent(0, shared.FalloutSortingBlock())
FALLOUT_COMMON_STATS_BLOCK.addComponent(3, common.FalloutArenaFullNameItem('arenaStr'))
FALLOUT_COMMON_STATS_BLOCK.addComponent(7, common.FalloutFinishResultBlock())
FALLOUT_COMMON_STATS_BLOCK.addComponent(9, personal.PersonalVehicleNamesBlock(base.ListMeta(), 'playerVehicleNames'))
FALLOUT_COMMON_STATS_BLOCK.addComponent(10, personal.FalloutVehiclesBlock(base.ListMeta(), 'playerVehicles', _RECORD.PERSONAL))
