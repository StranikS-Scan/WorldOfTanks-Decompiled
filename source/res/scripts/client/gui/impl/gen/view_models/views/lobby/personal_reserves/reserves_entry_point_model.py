# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_reserves/reserves_entry_point_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.disabled_category import DisabledCategory

class ReservesEntryPointModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ReservesEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getReserves(self):
        return self._getArray(0)

    def setReserves(self, value):
        self._setArray(0, value)

    @staticmethod
    def getReservesType():
        return BoosterModel

    def getTotalReserves(self):
        return self._getNumber(1)

    def setTotalReserves(self, value):
        self._setNumber(1, value)

    def getTotalLimitedReserves(self):
        return self._getNumber(2)

    def setTotalLimitedReserves(self, value):
        self._setNumber(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def getIsClanMember(self):
        return self._getBool(4)

    def setIsClanMember(self, value):
        self._setBool(4, value)

    def getDisabledCategories(self):
        return self._getArray(5)

    def setDisabledCategories(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDisabledCategoriesType():
        return DisabledCategory

    def getExpiringReserveWillExpireSoon(self):
        return self._getBool(6)

    def setExpiringReserveWillExpireSoon(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(ReservesEntryPointModel, self)._initialize()
        self._addArrayProperty('reserves', Array())
        self._addNumberProperty('totalReserves', 0)
        self._addNumberProperty('totalLimitedReserves', 0)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isClanMember', False)
        self._addArrayProperty('disabledCategories', Array())
        self._addBoolProperty('expiringReserveWillExpireSoon', False)
