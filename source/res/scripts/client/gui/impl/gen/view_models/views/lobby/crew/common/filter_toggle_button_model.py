# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/filter_toggle_button_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.dynamic_tooltip_model import DynamicTooltipModel

class FilterToggleButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(FilterToggleButtonModel, self).__init__(properties=properties, commands=commands)

    @property
    def tooltip(self):
        return self._getViewModel(0)

    @staticmethod
    def getTooltipType():
        return DynamicTooltipModel

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getCounter(self):
        return self._getNumber(4)

    def setCounter(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(FilterToggleButtonModel, self)._initialize()
        self._addViewModelProperty('tooltip', DynamicTooltipModel())
        self._addStringProperty('id', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isSelected', False)
        self._addNumberProperty('counter', 0)
