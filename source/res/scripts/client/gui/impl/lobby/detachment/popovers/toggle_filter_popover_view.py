# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/toggle_filter_popover_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_button_base_model import ToggleButtonBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_filter_popover_model import ToggleFilterPopoverModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_group_model import ToggleGroupModel
from gui.impl.lobby.detachment.popovers.popover_tracker_impl import PopoverTrackerImpl
from uilogging.detachment.loggers import DetachmentPopoverLogger
from uilogging.detachment.constants import ACTION

class ToggleFilterPopoverViewBase(PopoverTrackerImpl):
    uiLogger = DetachmentPopoverLogger()
    __slots__ = ('__title', '__header', '__filterGroupSettings', '__changeFiltersCallback', '__customResetFunc', '__activeFilters')

    def __init__(self, header, title, filterGroupSettings, changeFiltersCallback, onLifecycleChange, activeFilters, customResetFunc=None, settings=None, *args, **kwargs):
        if not isinstance(settings, ViewSettings):
            settings = ViewSettings(R.views.lobby.detachment.popovers.ToggleFilterPopover())
            settings.model = ToggleFilterPopoverModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ToggleFilterPopoverViewBase, self).__init__(settings, onLifecycleChange)
        self.__header = header
        self.__title = title
        self.__filterGroupSettings = filterGroupSettings
        self.__changeFiltersCallback = changeFiltersCallback
        self.__customResetFunc = customResetFunc
        self.__activeFilters = activeFilters

    @property
    def viewModel(self):
        return super(ToggleFilterPopoverViewBase, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ToggleFilterPopoverViewBase, self)._initialize()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        self.uiLogger.reset()
        super(ToggleFilterPopoverViewBase, self)._finalize()

    def __addListeners(self):
        self.viewModel.onToggleClick += self._onToggleClick
        self.viewModel.onResetClick += self.__onResetClick

    def __removeListeners(self):
        self.viewModel.onToggleClick -= self._onToggleClick
        self.viewModel.onResetClick -= self.__onResetClick

    def _onLoading(self):
        super(ToggleFilterPopoverViewBase, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setHeader(self.__header)
            model.filterStatus.setTitle(self.__title)
            self._fillModel(model)

    def _fillModel(self, model):
        self.__fillGroups(model)

    def __fillGroups(self, model):
        filtersGroupsList = model.getGroups()
        filtersGroupsList.clear()
        for group in self.__filterGroupSettings:
            groupModel = ToggleGroupModel()
            groupModel.setId(group['id'])
            groupModel.setLabel(group['label'])
            groupModel.setType(group['toggleType'])
            filtersList = groupModel.getFilters()
            filtersList.clear()
            for filterSettings in group['toggles']:
                filterModel = ToggleButtonBaseModel()
                filterModel.setId(filterSettings.id)
                filterModel.setIcon(filterSettings.icon)
                if filterSettings.tooltipHeader is not None:
                    filterModel.setTooltipHeader(filterSettings.tooltipHeader)
                if filterSettings.tooltipBody is not None:
                    filterModel.setTooltipBody(filterSettings.tooltipBody)
                filterModel.setIsActive(filterSettings.id in self.__activeFilters[group['id']])
                filtersList.addViewModel(filterModel)

            filtersGroupsList.addViewModel(groupModel)

        filtersGroupsList.invalidate()
        return

    def _onToggleClick(self, event):
        with self.viewModel.transaction() as model:
            filtersGroupList = model.getGroups()
            groupModel = filtersGroupList.getValue(event['groupIndex'])
            filterModel = groupModel.getFilters().getValue(event['toggleIndex'])
            status = not filterModel.getIsActive()
            filterModel.setIsActive(status)
            self.uiLogger.logFilterChanged(groupModel, filterModel, status)
            filtersGroupList.invalidate()
            if status:
                self.__activeFilters[groupModel.getId()].add(filterModel.getId())
            else:
                self.__activeFilters[groupModel.getId()].remove(filterModel.getId())
        self.__changeFiltersCallback()

    def _resetFilters(self):
        if self.__customResetFunc is not None:
            self.__customResetFunc()
        else:
            for key in self.__activeFilters.iterkeys():
                self.__activeFilters[key] = set()

        return

    @uiLogger.dLog(ACTION.POPOVER_FILTERS_RESET)
    def __onResetClick(self):
        self._resetFilters()
        self.__changeFiltersCallback()
        with self.viewModel.transaction() as model:
            self._fillModel(model)


class ToggleFilterPopoverViewStatus(ToggleFilterPopoverViewBase):
    __slots__ = ('__type', '__countData')

    def __init__(self, header, title, filterStatusType, filterGroupSettings, changeFiltersCallback, onLifecycleChange, activeFilters, countData, *args, **kwargs):
        super(ToggleFilterPopoverViewStatus, self).__init__(header, title, filterGroupSettings, changeFiltersCallback, onLifecycleChange, activeFilters, *args, **kwargs)
        self.__type = filterStatusType
        self.__countData = countData

    def _onLoading(self):
        super(ToggleFilterPopoverViewStatus, self)._onLoading()
        self.viewModel.filterStatus.setType(self.__type)

    def _fillModel(self, model):
        super(ToggleFilterPopoverViewStatus, self)._fillModel(model)
        model.filterStatus.setCurrent(self.__countData['currentCount'])
        model.filterStatus.setTotal(self.__countData['totalCount'])

    def _onToggleClick(self, event):
        super(ToggleFilterPopoverViewStatus, self)._onToggleClick(event)
        self.viewModel.filterStatus.setCurrent(self.__countData['currentCount'])
