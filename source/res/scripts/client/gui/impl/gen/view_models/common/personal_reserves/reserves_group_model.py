# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/personal_reserves/reserves_group_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel

class GroupCategory(Enum):
    XP = 'xp'
    CREDITS = 'credits'
    COMBINED_XP = 'combined'
    EVENT = 'event'
    CLAN = 'clan'


class ReservesGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ReservesGroupModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return GroupCategory(self._getString(0))

    def setCategory(self, value):
        self._setString(0, value.value)

    def getReserves(self):
        return self._getArray(1)

    def setReserves(self, value):
        self._setArray(1, value)

    @staticmethod
    def getReservesType():
        return BoosterModel

    def _initialize(self):
        super(ReservesGroupModel, self)._initialize()
        self._addStringProperty('category')
        self._addArrayProperty('reserves', Array())
