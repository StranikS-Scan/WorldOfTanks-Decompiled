# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/branch_selection_view_model.py
from frameworks.wulf import Array, ViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.nation_view_model import NationViewModel

class BranchSelectionViewModel(ViewModel):
    __slots__ = ('onConfirm', 'onClose', 'onShowInfo')

    def __init__(self, properties=3, commands=3):
        super(BranchSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getBranches(self):
        return self._getArray(0)

    def setBranches(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBranchesType():
        return NationViewModel

    def getSelectionStep(self):
        return self._getNumber(1)

    def setSelectionStep(self, value):
        self._setNumber(1, value)

    def getMaxSelectionSteps(self):
        return self._getNumber(2)

    def setMaxSelectionSteps(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BranchSelectionViewModel, self)._initialize()
        self._addArrayProperty('branches', Array())
        self._addNumberProperty('selectionStep', 1)
        self._addNumberProperty('maxSelectionSteps', 1)
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
        self.onShowInfo = self._addCommand('onShowInfo')
