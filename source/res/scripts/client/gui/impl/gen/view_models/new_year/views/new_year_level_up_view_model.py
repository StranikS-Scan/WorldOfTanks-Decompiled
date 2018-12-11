# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_level_up_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearLevelUpViewModel(ViewModel):
    __slots__ = ('onClose', 'onCollectRewards')

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    def getContainsVehicle(self):
        return self._getBool(2)

    def setContainsVehicle(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearLevelUpViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('containsVehicle', False)
        self.onClose = self._addCommand('onClose')
        self.onCollectRewards = self._addCommand('onCollectRewards')
