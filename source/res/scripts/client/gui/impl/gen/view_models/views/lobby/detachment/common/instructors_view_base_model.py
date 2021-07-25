# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructors_view_base_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_category_model import InstructorsCategoryModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel

class InstructorsViewBaseModel(NavigationViewModel):
    __slots__ = ('onInstructorClick', 'onVoiceListenClick', 'onSubViewBackClick')

    def __init__(self, properties=9, commands=6):
        super(InstructorsViewBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def filtersModel(self):
        return self._getViewModel(2)

    @property
    def popover(self):
        return self._getViewModel(3)

    def getIsSubView(self):
        return self._getBool(4)

    def setIsSubView(self, value):
        self._setBool(4, value)

    def getLastUnpackedInvID(self):
        return self._getNumber(5)

    def setLastUnpackedInvID(self, value):
        self._setNumber(5, value)

    def getCategories(self):
        return self._getArray(6)

    def setCategories(self, value):
        self._setArray(6, value)

    def getUnpackedInstructorsList(self):
        return self._getArray(7)

    def setUnpackedInstructorsList(self, value):
        self._setArray(7, value)

    def getUnpackedInstructorsCount(self):
        return self._getNumber(8)

    def setUnpackedInstructorsCount(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(InstructorsViewBaseModel, self)._initialize()
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addBoolProperty('isSubView', False)
        self._addNumberProperty('lastUnpackedInvID', 0)
        self._addArrayProperty('categories', Array())
        self._addArrayProperty('unpackedInstructorsList', Array())
        self._addNumberProperty('unpackedInstructorsCount', 0)
        self.onInstructorClick = self._addCommand('onInstructorClick')
        self.onVoiceListenClick = self._addCommand('onVoiceListenClick')
        self.onSubViewBackClick = self._addCommand('onSubViewBackClick')
