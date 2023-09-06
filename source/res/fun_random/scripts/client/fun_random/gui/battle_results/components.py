# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/components.py
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from gui.battle_results.components.common import RegularArenaFullNameItem, makeArenaFullName

class FunRandomArenaFullNameItem(RegularArenaFullNameItem, FunAssetPacksMixin):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaType = reusable.common.arenaType
        return makeArenaFullName(arenaType.getName(), self.getModeUserName())
