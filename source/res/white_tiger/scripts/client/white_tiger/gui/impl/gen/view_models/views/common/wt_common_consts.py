# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/common/wt_common_consts.py
from enum import Enum
from frameworks.wulf import ViewModel

class WTVehicleType(Enum):
    BOSS = 'boss'
    BOSS_2025 = 'boss_2025'
    BOSS_SPECIAL = 'boss_special'
    HUNTER = 'hunter'


class PortalType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'
    TANK = 'tank'


class WtCommonConsts(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(WtCommonConsts, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WtCommonConsts, self)._initialize()
