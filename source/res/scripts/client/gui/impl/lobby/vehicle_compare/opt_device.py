# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/opt_device.py
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider, DeluxeOptDeviceProvider
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabsController, OptDeviceTabs, OptDeviceSelectedFilters, getOptDeviceTabByItem
from gui.impl.lobby.vehicle_compare.base_sub_view import CompareBaseSetupSubView
from gui.shared.utils.requesters import REQ_CRITERIA

class _CompareSimpleOptDeviceProvider(SimpleOptDeviceProvider):

    def _fillBuyPrice(self, *args, **kwargs):
        pass

    def _fillBuyStatus(self, *args, **kwargs):
        pass


class _CompareDeluxeOptDeviceProvider(DeluxeOptDeviceProvider):

    def _fillBuyPrice(self, *args, **kwargs):
        pass

    def _fillBuyStatus(self, *args, **kwargs):
        pass

    def _getItemCriteria(self):
        return REQ_CRITERIA.OPTIONAL_DEVICE.TROPHY ^ REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE


class _CompareOptDeviceTabsController(OptDeviceTabsController):

    def _getAllProviders(self):
        return {OptDeviceTabs.SIMPLE: _CompareSimpleOptDeviceProvider,
         OptDeviceTabs.SPECIAL: _CompareDeluxeOptDeviceProvider}


class CompareOptDeviceSetupSubView(CompareBaseSetupSubView):

    def updateSlots(self, slotID, fullUpdate=True):
        self._filter.resetFilters(self._viewModel.filter)
        item = self._interactor.getCurrentLayout()[slotID]
        if item is not None:
            self._setTab(getOptDeviceTabByItem(item))
        super(CompareOptDeviceSetupSubView, self).updateSlots(slotID, fullUpdate)
        return

    def _createTabsController(self):
        return _CompareOptDeviceTabsController()

    def _createFilter(self):
        return OptDeviceSelectedFilters()

    def _onTabChanged(self, args):
        self._filter.resetFilters(self._viewModel.filter)
        super(CompareOptDeviceSetupSubView, self)._onTabChanged(args)
