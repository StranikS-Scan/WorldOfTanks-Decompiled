# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/opt_device.py
from async import async
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.lobby.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.opt_device_setup import OptDeviceSetupSubView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent

class _BootcampSimpleOptDeviceProvider(SimpleOptDeviceProvider):

    def _fillStatus(self, model, item, slotID, isInstalledOrMounted):
        super(_BootcampSimpleOptDeviceProvider, self)._fillStatus(model, item, slotID, isInstalledOrMounted)
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
        self._viewModel.hints.addHintModel(TutorialHintConsts.APPLY_HANGAR_OPT_DEVICE_MC)
        self._viewModel.hints.addHintModel(TutorialHintConsts.SETUP_VIEW_CARDS_OPT_DEVICE_MC)
        self._viewModel.hints.addHintModel(TutorialHintConsts.SETUP_VIEW_SLOTS_OPT_DEVICE_MC)
        if any(self._interactor.getCurrentLayout()):
            return
        items = self._provider.getItemsList()
        for item in items:
            if item.isInInventory:
                self._onSelectItem({'intCD': item.intCD})
                break

    def finalize(self):
        super(BootcampOptDeviceSetupSubView, self).finalize()
        self.__hideHints()

    @async
    def canQuit(self):
        result = yield super(BootcampOptDeviceSetupSubView, self).canQuit()
        if result:
            self.__hideHints()
        raise AsyncReturn(result)

    def _createTabsController(self):
        return _BootcampOptDeviceTabsController()

    @staticmethod
    def __hideHints():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.APPLY_HANGAR_OPT_DEVICE_MC}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.SETUP_VIEW_CARDS_OPT_DEVICE_MC}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.SETUP_VIEW_SLOTS_OPT_DEVICE_MC}), EVENT_BUS_SCOPE.LOBBY)
