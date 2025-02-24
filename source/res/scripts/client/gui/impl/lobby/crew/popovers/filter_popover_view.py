# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/popovers/filter_popover_view.py
import typing
import Event
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import FilterToggleGroupModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_view_model import FilterPopoverViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.tooltips.dismissed_toggle_tooltip import DismissedToggleTooltip
from gui.impl.pub import PopOverViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.lobby.crew.filter import FilterGroupSettings as GroupSettings
    from typing import Iterable, Optional, Callable
    FilterGroups = Iterable[GroupSettings]

class FilterPopoverView(PopOverViewImpl):
    __slots__ = ('__title', '__groupSettings', '__onStateUpdated', '__state', '__canResetCallback', '__showResetBtn', 'onTooltipCreated')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, title, groupSettings, onStateUpdated, state=None, showResetBtn=True, canResetCallback=None):
        settings = ViewSettings(layoutID=R.views.lobby.crew.popovers.FilterPopoverView(), model=FilterPopoverViewModel())
        super(FilterPopoverView, self).__init__(settings)
        self.__title = title
        self.__groupSettings = groupSettings
        self.__onStateUpdated = onStateUpdated
        self.__state = state
        self.__showResetBtn = showResetBtn
        self.__canResetCallback = canResetCallback
        self.onTooltipCreated = Event.Event()

    @property
    def viewModel(self):
        return super(FilterPopoverView, self).getViewModel()

    def updateGroupSettings(self, groupSettings):
        self.__groupSettings = groupSettings
        self.__fillModel()

    def createToolTip(self, event):
        result = super(FilterPopoverView, self).createToolTip(event)
        self.onTooltipCreated(event, result)
        return result

    def createToolTipContent(self, event, contentID):
        return DismissedToggleTooltip() if contentID == R.views.lobby.crew.tooltips.DismissedToggleTooltip() else super(FilterPopoverView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onUpdateFilter, self.__onUpdateFilter), (self.viewModel.onResetFilter, self.__onResetFilter))

    def _onLoading(self, *args, **kwargs):
        super(FilterPopoverView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    @args2params(str, str)
    def __onUpdateFilter(self, groupID, toggleID):
        self.__state.update(groupID, toggleID)
        self.__fillModel()
        self.__onStateUpdated()

    def __onResetFilter(self):
        self.__state.clear()
        self.__fillModel()
        self.__onStateUpdated()

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setTitle(self.__title)
            if self.__canResetCallback is not None:
                tx.setCanResetFilter(self.__canResetCallback())
            groups = tx.getFilterGroups()
            groups.clear()
            groups.invalidate()
            for settingGroup in self.__groupSettings:
                vm = FilterToggleGroupModel()
                settingGroup.pack(vm, self.__state)
                groups.addViewModel(vm)

            tx.setShowResetBtn(self.__showResetBtn)
        return
