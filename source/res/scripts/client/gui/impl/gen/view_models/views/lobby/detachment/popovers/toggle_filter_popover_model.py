# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/popovers/toggle_filter_popover_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_group_model import ToggleGroupModel

class ToggleFilterPopoverModel(ViewModel):
    __slots__ = ('onToggleClick', 'onResetClick')

    def __init__(self, properties=3, commands=2):
        super(ToggleFilterPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def filterStatus(self):
        return self._getViewModel(0)

    def getHeader(self):
        return self._getResource(1)

    def setHeader(self, value):
        self._setResource(1, value)

    def getGroups(self):
        return self._getArray(2)

    def setGroups(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(ToggleFilterPopoverModel, self)._initialize()
        self._addViewModelProperty('filterStatus', FilterStatusModel())
        self._addResourceProperty('header', R.invalid())
        self._addArrayProperty('groups', Array())
        self.onToggleClick = self._addCommand('onToggleClick')
        self.onResetClick = self._addCommand('onResetClick')
