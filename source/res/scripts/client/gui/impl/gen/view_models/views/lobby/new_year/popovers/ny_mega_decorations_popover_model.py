# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_mega_decorations_popover_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_popover_decoration_slot_model import NyPopoverDecorationSlotModel

class NyMegaDecorationsPopoverModel(ViewModel):
    __slots__ = ('onSelectedDecoration', 'onSlotStatusIsNewChanged')

    def __init__(self, properties=10, commands=2):
        super(NyMegaDecorationsPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def slot(self):
        return self._getViewModel(0)

    def getDecorationName(self):
        return self._getResource(1)

    def setDecorationName(self, value):
        self._setResource(1, value)

    def getObjectBonus(self):
        return self._getReal(2)

    def setObjectBonus(self, value):
        self._setReal(2, value)

    def getTotalBonus(self):
        return self._getReal(3)

    def setTotalBonus(self, value):
        self._setReal(3, value)

    def getHasDecoration(self):
        return self._getBool(4)

    def setHasDecoration(self, value):
        self._setBool(4, value)

    def getSelected(self):
        return self._getBool(5)

    def setSelected(self, value):
        self._setBool(5, value)

    def getPartsCurrent(self):
        return self._getNumber(6)

    def setPartsCurrent(self, value):
        self._setNumber(6, value)

    def getPartsTotal(self):
        return self._getNumber(7)

    def setPartsTotal(self, value):
        self._setNumber(7, value)

    def getDecorationTypeIcon(self):
        return self._getResource(8)

    def setDecorationTypeIcon(self, value):
        self._setResource(8, value)

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(9)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(NyMegaDecorationsPopoverModel, self)._initialize()
        self._addViewModelProperty('slot', NyPopoverDecorationSlotModel())
        self._addResourceProperty('decorationName', R.invalid())
        self._addRealProperty('objectBonus', 0.0)
        self._addRealProperty('totalBonus', 0.0)
        self._addBoolProperty('hasDecoration', False)
        self._addBoolProperty('selected', False)
        self._addNumberProperty('partsCurrent', 0)
        self._addNumberProperty('partsTotal', 0)
        self._addResourceProperty('decorationTypeIcon', R.invalid())
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self.onSelectedDecoration = self._addCommand('onSelectedDecoration')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
