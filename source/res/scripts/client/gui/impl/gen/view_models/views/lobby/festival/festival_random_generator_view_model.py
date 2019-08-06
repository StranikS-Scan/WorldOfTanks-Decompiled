# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_random_generator_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class FestivalRandomGeneratorViewModel(ViewModel):
    __slots__ = ('onRandomNameChanged',)

    @property
    def randomPacks(self):
        return self._getViewModel(0)

    def getCurrentRandomName(self):
        return self._getString(1)

    def setCurrentRandomName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(FestivalRandomGeneratorViewModel, self)._initialize()
        self._addViewModelProperty('randomPacks', ListModel())
        self._addStringProperty('currentRandomName', '')
        self.onRandomNameChanged = self._addCommand('onRandomNameChanged')
