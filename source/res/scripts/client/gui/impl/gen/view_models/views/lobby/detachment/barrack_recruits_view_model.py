# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/barrack_recruits_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_model import RecruitModel

class BarrackRecruitsViewModel(NavigationViewModel):
    __slots__ = ('onRestore', 'onMobilize')

    def __init__(self, properties=8, commands=5):
        super(BarrackRecruitsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def filtersModel(self):
        return self._getViewModel(2)

    @property
    def popover(self):
        return self._getViewModel(3)

    @property
    def recruits(self):
        return self._getViewModel(4)

    def getEndTimeConvert(self):
        return self._getNumber(5)

    def setEndTimeConvert(self, value):
        self._setNumber(5, value)

    def getMobilizeCount(self):
        return self._getNumber(6)

    def setMobilizeCount(self, value):
        self._setNumber(6, value)

    def getAutoScrollId(self):
        return self._getNumber(7)

    def setAutoScrollId(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(BarrackRecruitsViewModel, self)._initialize()
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addViewModelProperty('recruits', UserListModel())
        self._addNumberProperty('endTimeConvert', 0)
        self._addNumberProperty('mobilizeCount', 0)
        self._addNumberProperty('autoScrollId', 0)
        self.onRestore = self._addCommand('onRestore')
        self.onMobilize = self._addCommand('onMobilize')
