# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_results/components/comp7_light_components.py
from __future__ import absolute_import
import typing
from comp7_core.gui.battle_results.components.comp7_core_components import checkIfDeserter
from account_helpers.AccountSettings import STATS_COMP7_LIGHT_SORTING
from fairplay_violation_types import FairplayViolations
from gui.battle_results.components import base
from gui.battle_results.components.shared import SortingBlock
from gui.impl import backport
from gui.impl.gen.resources import R
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo

class IsDeserterFlag(base.StatsItem):

    def _convert(self, result, reusable):
        return backport.text(R.strings.comp7_light.battleResult.header.deserter()) if checkIfDeserter(reusable, FairplayViolations.COMP7_LIGHT_DESERTER) else None


class Comp7LightSortingBlock(SortingBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(Comp7LightSortingBlock, self).__init__(STATS_COMP7_LIGHT_SORTING, meta, field, *path)
