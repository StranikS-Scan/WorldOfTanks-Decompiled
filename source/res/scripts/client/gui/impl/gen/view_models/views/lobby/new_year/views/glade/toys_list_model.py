# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/toys_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.toy_model import ToyModel

class ToysListModel(ViewModel):
    __slots__ = ('onApplySelection', 'onListClose', 'onAllToysSeen')

    def __init__(self, properties=2, commands=3):
        super(ToysListModel, self).__init__(properties=properties, commands=commands)

    def getToys(self):
        return self._getArray(0)

    def setToys(self, value):
        self._setArray(0, value)

    @staticmethod
    def getToysType():
        return ToyModel

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ToysListModel, self)._initialize()
        self._addArrayProperty('toys', Array())
        self._addStringProperty('type', '')
        self.onApplySelection = self._addCommand('onApplySelection')
        self.onListClose = self._addCommand('onListClose')
        self.onAllToysSeen = self._addCommand('onAllToysSeen')
