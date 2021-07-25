# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/popovers/toggle_sort_filter_popover_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.radio_buttons_group_model import RadioButtonsGroupModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_filter_popover_model import ToggleFilterPopoverModel

class ToggleSortFilterPopoverModel(ToggleFilterPopoverModel):
    __slots__ = ('onSortClick',)

    def __init__(self, properties=4, commands=3):
        super(ToggleSortFilterPopoverModel, self).__init__(properties=properties, commands=commands)

    def getSorts(self):
        return self._getArray(3)

    def setSorts(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(ToggleSortFilterPopoverModel, self)._initialize()
        self._addArrayProperty('sorts', Array())
        self.onSortClick = self._addCommand('onSortClick')
