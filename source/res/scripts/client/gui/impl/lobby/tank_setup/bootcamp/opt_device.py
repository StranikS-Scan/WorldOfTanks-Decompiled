# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/opt_device.py
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.opt_device_setup import OptDeviceSetupSubView

class _BootcampSimpleOptDeviceProvider(SimpleOptDeviceProvider):

    def _fillStatus(self, model, item, slotID):
        super(_BootcampSimpleOptDeviceProvider, self)._fillStatus(model, item, slotID)
        if not item.isInInventory:
            model.setIsDisabled(True)


class _BootcampOptDeviceTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return OptDeviceTabs.SIMPLE

    @tabUpdateFunc(OptDeviceTabs.SIMPLE)
    def _updateSimple(self, viewModel, isFirst=False):
        pass

    def _getAllProviders(self):
        return {OptDeviceTabs.SIMPLE: _BootcampSimpleOptDeviceProvider}


class BootcampOptDeviceSetupSubView(OptDeviceSetupSubView):

    def onLoading(self, currentSlotID, *args, **kwargs):
        super(BootcampOptDeviceSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)
        if any(self._interactor.getCurrentLayout()):
            return
        items = self._provider.getItemsList()
        for item in items:
            if item.isInInventory:
                self._onSelectItem({'intCD': item.intCD,
                 'isAutoSelect': True})
                break

    def _createTabsController(self):
        return _BootcampOptDeviceTabsController()
