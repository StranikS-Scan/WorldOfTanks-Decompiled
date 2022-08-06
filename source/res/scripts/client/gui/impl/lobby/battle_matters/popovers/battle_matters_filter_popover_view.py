# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/popovers/battle_matters_filter_popover_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.battle_matters.popovers.battle_matters_filter_popover_view_model import BattleMattersFilterPopoverViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.popovers.filter_control_view_model import FilterControlViewModel
from gui.impl.pub.view_impl import PopOverViewImpl
from gui.impl.gen import R

class BattleMattersFilterPopoverView(PopOverViewImpl):
    __slots__ = ('__filters', '__updateCallback')

    def __init__(self, filtersDict=None, updateCallback=None):
        settings = ViewSettings(R.views.lobby.battle_matters.popovers.BattleMattersFilterPopoverView())
        settings.flags = ViewFlags.VIEW
        settings.model = BattleMattersFilterPopoverViewModel()
        self.__filters = filtersDict or {}
        self.__updateCallback = updateCallback
        super(BattleMattersFilterPopoverView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersFilterPopoverView, self).getViewModel()

    def onToggleFilter(self, event):
        changesFromEvent = {'Types': event.get(BattleMattersFilterPopoverViewModel.ARG_CONTROL_TYPE, {}),
         'Nations': event.get(BattleMattersFilterPopoverViewModel.ARG_CONTROL_NATION, {})}
        changes = {k:{v: not self.__filters[k][v]} for k, v in changesFromEvent.iteritems() if k and v}
        self._updateFilter(changes)

    def _onLoading(self, *args, **kwargs):
        super(BattleMattersFilterPopoverView, self)._onLoading(*args, **kwargs)
        self._update()

    def _finalize(self):
        self.__updateCallback = None
        self.__filters = None
        return

    def _update(self):
        with self.viewModel.transaction() as tx:
            for key in self.__filters:
                filterArray = getattr(tx, 'get' + key)()
                filterArray.clear()
                filters = self.__filters[key]
                for filterName, filterValue in filters.iteritems():
                    currentControl = FilterControlViewModel()
                    currentControl.setName(filterName)
                    currentControl.setIsSelected(filterValue)
                    filterArray.addViewModel(currentControl)

                filterArray.invalidate()

    def _getEvents(self):
        return ((self.viewModel.onToggleFilter, self.onToggleFilter),)

    def _changeVMValue(self, vm, valuesDict, valueName):
        allVMs = getattr(vm, 'get' + valueName)()
        for singleVM in allVMs:
            name = singleVM.getName()
            if name in valuesDict:
                singleVM.setIsSelected(valuesDict[name])

    def _updateFilter(self, changes):
        for filterName in self.__filters:
            self.__filters[filterName].update(changes.get(filterName, {}))

        with self.viewModel.transaction() as tx:
            for change in changes:
                self._changeVMValue(tx, changes[change], change)

        if self.__updateCallback:
            self.__updateCallback(self.__filters)
