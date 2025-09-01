# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_control/arena_info/vos_collections.py
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey

class Comp7LightSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
        return result if result else cmp(xvInfoVO.player, yvInfoVO.player)
