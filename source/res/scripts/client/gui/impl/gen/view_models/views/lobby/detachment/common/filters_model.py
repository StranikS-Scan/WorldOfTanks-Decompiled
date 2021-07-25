# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/filters_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_filter_model import ToggleFilterModel

class FiltersModel(FilterStatusModel):
    __slots__ = ('onFilterChanged', 'onFilterReset')

    def __init__(self, properties=6, commands=2):
        super(FiltersModel, self).__init__(properties=properties, commands=commands)

    def getFilters(self):
        return self._getArray(5)

    def setFilters(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(FiltersModel, self)._initialize()
        self._addArrayProperty('filters', Array())
        self.onFilterChanged = self._addCommand('onFilterChanged')
        self.onFilterReset = self._addCommand('onFilterReset')
