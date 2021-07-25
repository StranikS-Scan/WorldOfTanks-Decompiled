# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/toggle_sort_filter_popover_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.radio_button_model import RadioButtonModel
from gui.impl.gen.view_models.views.lobby.detachment.common.radio_buttons_group_model import RadioButtonsGroupModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_sort_filter_popover_model import ToggleSortFilterPopoverModel
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewStatus

class ToggleSortFilterPopoverView(ToggleFilterPopoverViewStatus):
    __slots__ = ('__sortsGroupSettings', '__activeSorts', '__changeSortingCallback')

    def __init__(self, sortsGroupSettings, activeSorts, sortingCallback, *args, **kwargs):
        self.__sortsGroupSettings = sortsGroupSettings
        self.__activeSorts = activeSorts
        self.__changeSortingCallback = sortingCallback
        settings = ViewSettings(R.views.lobby.detachment.popovers.ToggleSortFilterPopover())
        settings.model = ToggleSortFilterPopoverModel()
        super(ToggleSortFilterPopoverView, self).__init__(settings=settings, *args, **kwargs)

    @property
    def viewModel(self):
        return super(ToggleSortFilterPopoverView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ToggleSortFilterPopoverView, self)._initialize()
        self.__addSortListeners()

    def _finalize(self):
        self.__removeSortListeners()
        super(ToggleSortFilterPopoverView, self)._finalize()

    def __addSortListeners(self):
        self.viewModel.onSortClick += self._onSortClick

    def __removeSortListeners(self):
        self.viewModel.onToggleClick -= self._onSortClick

    def _fillModel(self, model):
        super(ToggleSortFilterPopoverView, self)._fillModel(model)
        self.__fillSorts(model)

    def __fillSorts(self, model):
        filtersGroupsList = model.getSorts()
        filtersGroupsList.clear()
        for sortsGroup in self.__sortsGroupSettings:
            sortId = sortsGroup['id']
            groupModel = RadioButtonsGroupModel()
            groupModel.setId(sortId)
            groupModel.setLabel(sortsGroup['label'])
            groupModel.setSelectedId(self.__activeSorts[sortId])
            filtersList = groupModel.getList()
            filtersList.clear()
            for sortSettings in sortsGroup['sorts']:
                sortModel = RadioButtonModel()
                sortModel.setId(sortSettings.id)
                sortModel.setLabel(sortSettings.label)
                filtersList.addViewModel(sortModel)

            filtersGroupsList.addViewModel(groupModel)

        filtersGroupsList.invalidate()

    def _onSortClick(self, event):
        with self.viewModel.transaction() as model:
            groupIndex = event['groupIndex']
            sortIndex = event['sortIndex']
            filtersSortsGroups = model.getSorts()
            groupModel = filtersSortsGroups.getValue(groupIndex)
            groupID = groupModel.getId()
            sortID = groupModel.getList().getValue(sortIndex).getId()
            groupModel.setSelectedId(sortID)
            filtersSortsGroups.invalidate()
        self.__changeSortingCallback({groupID: sortID})
