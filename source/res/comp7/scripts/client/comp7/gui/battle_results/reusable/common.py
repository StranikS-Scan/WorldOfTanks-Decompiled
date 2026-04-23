# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/reusable/common.py
from gui.battle_results.reusable.common import CommonInfo

class Comp7CommonInfo(CommonInfo):
    __slots__ = ('__bannedVehicles',)

    def __init__(self, *args, **kwargs):
        super(Comp7CommonInfo, self).__init__(*args, **kwargs)
        self.__bannedVehicles = kwargs.get('comp7BannedVehicles', {})

    @property
    def bannedVehicles(self):
        return self.__bannedVehicles
