# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/list_filter_mixin.py
from copy import deepcopy
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_filter_model import ToggleFilterModel
from gui.impl.lobby.detachment.popovers.filters import TOGGLE_FILTER_ICONS_MAP
from shared_utils import CONST_CONTAINER
from uilogging.detachment.constants import ACTION
from uilogging.detachment.loggers import DetachmentNullToggleLogger

class FilterContext(CONST_CONTAINER):
    DETACHMENT = 'detachment'
    INSTRUCTORS = 'instructors'
    RECRUIT = 'recruit'
    PROFILE = 'profile'
    VEHICLE = 'vehicle'


class ToggleFilterMixin(object):
    _defaultToggleSetter = staticmethod(dict)
    _toggleFilters = {}
    uiLogger = DetachmentNullToggleLogger()

    @property
    def _isFilterActive(self):
        return any(self._toggleFilters.itervalues())

    def _fillList(self, model):
        pass

    def _subscribeFilterHandlers(self, model):
        filtersModel = self._getFiltersModel(model)
        filtersModel.onFilterReset += self.__onFilterReset
        filtersModel.onFilterChanged += self.__onToggleFilterChanged

    def _unsubscribeFilterHandlers(self, model):
        filtersModel = self._getFiltersModel(model)
        filtersModel.onFilterReset -= self.__onFilterReset
        filtersModel.onFilterChanged -= self.__onToggleFilterChanged

    def _getFiltersModel(self, model):
        raise NotImplementedError

    def _initFilters(self, model, filterOrder, tooltipContext, customIconMap=None, customTooltipResPath=None):
        tooltipResPath = customTooltipResPath or R.strings.tooltips.filterToggle
        iconMap = customIconMap or TOGGLE_FILTER_ICONS_MAP
        filtersModel = self._getFiltersModel(model)
        filterList = filtersModel.getFilters()
        filtersModel.setIsResetAvailable(self._isFilterActive)
        for filterName in filterOrder:
            filterModel = ToggleFilterModel()
            filterModel.setId(filterName)
            filterModel.setIcon(iconMap[filterName])
            filterModel.setTooltipHeader(tooltipResPath.dyn(filterName).dyn(tooltipContext).header())
            filterModel.setTooltipBody(tooltipResPath.dyn(filterName).dyn(tooltipContext).body())
            filterModel.setIsActive(self._toggleFilters[filterName])
            filterList.addViewModel(filterModel)

        filterList.invalidate()

    def _resetData(self):
        type(self)._toggleFilters = self._defaultToggleSetter()

    def _resetModel(self, model):
        self.__resetToggleFilters(model)
        filtersModel = self._getFiltersModel(model)
        filtersModel.setIsResetAvailable(self._isFilterActive)
        self._fillList(model)

    def __onFilterReset(self):
        self.uiLogger.log(ACTION.ALL_FILTERS_RESET)
        self._resetData()
        with self.viewModel.transaction() as model:
            self._resetModel(model)

    def __resetToggleFilters(self, model):
        filterList = self._getFiltersModel(model).getFilters()
        for filterModel in filterList:
            status = self._toggleFilters.get(filterModel.getId())
            if status is not None:
                filterModel.setIsActive(status)

        filterList.invalidate()
        return

    def __onToggleFilterChanged(self, event):
        with self.viewModel.transaction() as model:
            filtersModel = self._getFiltersModel(model)
            filterList = filtersModel.getFilters()
            affectedFilter = filterList[event['index']]
            status = not affectedFilter.getIsActive()
            self.uiLogger.logFilterChanged(affectedFilter, status)
            type(self)._toggleFilters[affectedFilter.getId()] = status
            affectedFilter.setIsActive(status)
            filterList.invalidate()
            filtersModel.setIsResetAvailable(self._isFilterActive)
            self._fillList(model)


class FiltersMixin(ToggleFilterMixin):
    _defaultPopoverSetter = staticmethod(dict)
    _popoverFilters = {}
    _defaultPopoverFilterItems = None

    @property
    def _isFilterActive(self):
        return super(FiltersMixin, self)._isFilterActive or self._isPopoverActive

    @property
    def _isPopoverActive(self):
        return self._popoverFilters.items() != self._defaultPopoverFilterItems

    @property
    def _hasPopoverFilters(self):
        return any((f for f in self._popoverFilters.values()))

    def _getFiltersModel(self, model):
        return model.filtersModel

    def _getPopoverModel(self, model):
        return model.popover

    def _initFilters(self, model, filterOrder, tooltipContext, customIconMap=None, customTooltipResPath=None):
        if self._defaultPopoverFilterItems is None:
            type(self)._defaultPopoverFilterItems = deepcopy(self._defaultPopoverSetter().items())
        super(FiltersMixin, self)._initFilters(model, filterOrder, tooltipContext, customIconMap, customTooltipResPath)
        self._setPopoverState(model)
        return

    def _resetData(self):
        super(FiltersMixin, self)._resetData()
        type(self)._popoverFilters = self._defaultPopoverSetter()
        self._addDefaultPopoverFilter()

    def _resetModel(self, model):
        super(FiltersMixin, self)._resetModel(model)
        self._setPopoverState(model)

    def _addDefaultPopoverFilter(self):
        pass

    def _setPopoverState(self, model, active=False):
        popoverModel = self._getPopoverModel(model)
        popoverModel.setIsActive(active or self._hasPopoverFilters)

    def _changePopoverFilterCallback(self):
        with self.viewModel.transaction() as model:
            filterModel = self._getFiltersModel(model)
            filterModel.setIsResetAvailable(self._isFilterActive)
            self._fillList(model)

    def _activatePopoverViewCallback(self, activate):
        with self.viewModel.transaction() as model:
            self._setPopoverState(model, activate)

    def _resetPopoverFilters(self):
        type(self)._popoverFilters.update(self._defaultPopoverSetter())
        self._addDefaultPopoverFilter()
