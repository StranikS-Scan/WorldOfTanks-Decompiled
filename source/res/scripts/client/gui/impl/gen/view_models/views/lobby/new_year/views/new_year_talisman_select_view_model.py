# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_talisman_select_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_talisman_select_state_model import NewYearTalismanSelectStateModel

class NewYearTalismanSelectViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onViewResized')

    def __init__(self, properties=3, commands=2):
        super(NewYearTalismanSelectViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedCount(self):
        return self._getNumber(0)

    def setSelectedCount(self, value):
        self._setNumber(0, value)

    def getTalismans(self):
        return self._getArray(1)

    def setTalismans(self, value):
        self._setArray(1, value)

    def getTalismanPositionSet(self):
        return self._getArray(2)

    def setTalismanPositionSet(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(NewYearTalismanSelectViewModel, self)._initialize()
        self._addNumberProperty('selectedCount', 0)
        self._addArrayProperty('talismans', Array())
        self._addArrayProperty('talismanPositionSet', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onViewResized = self._addCommand('onViewResized')
