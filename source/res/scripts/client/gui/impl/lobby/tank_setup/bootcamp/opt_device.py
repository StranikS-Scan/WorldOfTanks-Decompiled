# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/opt_device.py
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.opt_device_setup import OptDeviceSetupSubView
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, BC_LOG_ACTIONS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger

class _BootcampSimpleOptDeviceProvider(SimpleOptDeviceProvider):

    def _fillStatus(self, model, item, slotID):
        super(_BootcampSimpleOptDeviceProvider, self)._fillStatus(model, item, slotID)
        if not item.isInInventory:
            model.setIsDisabled(True)


class _BootcampOptDeviceTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return OptDeviceTabs.SIMPLE

    def getTabCurrency(self, _):
        pass

    @tabUpdateFunc(OptDeviceTabs.SIMPLE)
    def _updateSimple(self, viewModel, isFirst=False):
        pass

    def _getAllProviders(self):
        return {OptDeviceTabs.SIMPLE: _BootcampSimpleOptDeviceProvider}


class BootcampOptDeviceSetupSubView(OptDeviceSetupSubView):
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_DEVICE_SETUP_SUB_VIEW)

    def onLoading(self, currentSlotID, *args, **kwargs):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.SHOW)
        super(BootcampOptDeviceSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)
        if any(self._interactor.getCurrentLayout()):
            return
        items = self._provider.getItemsList()
        for item in items:
            if item.isInInventory:
                self._onSelectItem({'intCD': item.intCD,
                 'isAutoSelect': True})
                break

    def finalize(self):
        if self._currentTabName:
            self.uiBootcampLogger.log(BC_LOG_ACTIONS.CLOSE)
        super(BootcampOptDeviceSetupSubView, self).finalize()

    def _onSelectItem(self, args):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.SELECT, item_id=args.get('intCD'))
        super(BootcampOptDeviceSetupSubView, self)._onSelectItem(args)

    def _createTabsController(self):
        return _BootcampOptDeviceTabsController()

    def _onDealConfirmed(self, _=None):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.CONFIRM)
        super(BootcampOptDeviceSetupSubView, self)._onDealConfirmed(_)
