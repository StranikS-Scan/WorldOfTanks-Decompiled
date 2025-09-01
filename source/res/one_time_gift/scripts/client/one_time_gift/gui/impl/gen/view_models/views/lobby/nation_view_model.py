# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/nation_view_model.py
from frameworks.wulf import Array, ViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_view_model import BranchViewModel

class NationViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NationViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def getBranches(self):
        return self._getArray(1)

    def setBranches(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBranchesType():
        return BranchViewModel

    def _initialize(self):
        super(NationViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addArrayProperty('branches', Array())
