# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/composer.py
from fun_random.gui.battle_results.templates import FUN_RANDOM_COMMON_STATS_BLOCK, FUN_RANDOM_PERSONAL_STATS_BLOCK
from gui.battle_results.composer import StatsComposer
from gui.battle_results import templates

class FunRandomStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(FunRandomStatsComposer, self).__init__(reusable, FUN_RANDOM_COMMON_STATS_BLOCK.clone(), FUN_RANDOM_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
