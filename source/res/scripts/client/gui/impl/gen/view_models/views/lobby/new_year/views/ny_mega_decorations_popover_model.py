# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_mega_decorations_popover_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_popover_mega_decoration_slot_model import NewYearPopoverMegaDecorationSlotModel

class NyMegaDecorationsPopoverModel(ViewModel):
    __slots__ = ('onSelectedDecoration', 'onSlotStatusIsNewChanged')

    def __init__(self, properties=7, commands=2):
        super(NyMegaDecorationsPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def slot(self):
        return self._getViewModel(0)

    def getDecorationTypeIcon(self):
        return self._getResource(1)

    def setDecorationTypeIcon(self, value):
        self._setResource(1, value)

    def getDecorationName(self):
        return self._getResource(2)

    def setDecorationName(self, value):
        self._setResource(2, value)

    def getObjectBonus(self):
        return self._getReal(3)

    def setObjectBonus(self, value):
        self._setReal(3, value)

    def getTotalBonus(self):
        return self._getReal(4)

    def setTotalBonus(self, value):
        self._setReal(4, value)

    def getHasDecoration(self):
        return self._getBool(5)

    def setHasDecoration(self, value):
        self._setBool(5, value)

    def getSelected(self):
        return self._getBool(6)

    def setSelected(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyMegaDecorationsPopoverModel, self)._initialize()
        self._addViewModelProperty('slot', NewYearPopoverMegaDecorationSlotModel())
        self._addResourceProperty('decorationTypeIcon', R.invalid())
        self._addResourceProperty('decorationName', R.invalid())
        self._addRealProperty('objectBonus', 0.0)
        self._addRealProperty('totalBonus', 0.0)
        self._addBoolProperty('hasDecoration', False)
        self._addBoolProperty('selected', False)
        self.onSelectedDecoration = self._addCommand('onSelectedDecoration')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
