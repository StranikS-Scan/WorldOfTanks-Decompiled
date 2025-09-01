# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/battle_results/components/shared.py
from account_helpers.AccountSettings import STATS_COMP7_SORTING
from gui.battle_results.components.shared import SortingBlock

class Comp7CoreSortingBlock(SortingBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(Comp7CoreSortingBlock, self).__init__(STATS_COMP7_SORTING, meta, field, *path)
