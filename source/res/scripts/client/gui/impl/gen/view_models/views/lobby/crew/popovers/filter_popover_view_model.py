# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/popovers/filter_popover_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import FilterToggleGroupModel

class FilterPopoverViewModel(ViewModel):
    __slots__ = ('onUpdateFilter', 'onResetFilter')

    def __init__(self, properties=4, commands=2):
        super(FilterPopoverViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getFilterGroups(self):
        return self._getArray(1)

    def setFilterGroups(self, value):
        self._setArray(1, value)

    @staticmethod
    def getFilterGroupsType():
        return FilterToggleGroupModel

    def getCanResetFilter(self):
        return self._getBool(2)

    def setCanResetFilter(self, value):
        self._setBool(2, value)

    def getShowResetBtn(self):
        return self._getBool(3)

    def setShowResetBtn(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(FilterPopoverViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('filterGroups', Array())
        self._addBoolProperty('canResetFilter', False)
        self._addBoolProperty('showResetBtn', False)
        self.onUpdateFilter = self._addCommand('onUpdateFilter')
        self.onResetFilter = self._addCommand('onResetFilter')
