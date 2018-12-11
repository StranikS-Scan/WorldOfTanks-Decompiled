# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_break_filter_popover_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearBreakFilterPopoverModel(ViewModel):
    __slots__ = ('onCloseBtnClick',)

    @property
    def levelBtns(self):
        return self._getViewModel(0)

    @property
    def typeDecorationBtns(self):
        return self._getViewModel(1)

    def _initialize(self):
        super(NewYearBreakFilterPopoverModel, self)._initialize()
        self._addViewModelProperty('levelBtns', UserListModel())
        self._addViewModelProperty('typeDecorationBtns', UserListModel())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
