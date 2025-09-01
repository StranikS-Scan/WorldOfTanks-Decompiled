# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/personal_reserves_tab_view_model.py
from enum import IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import ReservesGroupModel

class TabAlias(IntEnum):
    STATS = 0
    RESERVES = 1


class PersonalReservesTabViewModel(ViewModel):
    __slots__ = ('onBoosterActivate',)

    def __init__(self, properties=2, commands=1):
        super(PersonalReservesTabViewModel, self).__init__(properties=properties, commands=commands)

    def getReserveGroups(self):
        return self._getArray(0)

    def setReserveGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getReserveGroupsType():
        return ReservesGroupModel

    def getTabSelection(self):
        return TabAlias(self._getNumber(1))

    def setTabSelection(self, value):
        self._setNumber(1, value.value)

    def _initialize(self):
        super(PersonalReservesTabViewModel, self)._initialize()
        self._addArrayProperty('reserveGroups', Array())
        self._addNumberProperty('tabSelection')
        self.onBoosterActivate = self._addCommand('onBoosterActivate')
