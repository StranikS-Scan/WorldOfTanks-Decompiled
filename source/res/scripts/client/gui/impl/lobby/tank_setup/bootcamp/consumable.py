# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/consumable.py
from BWUtil import AsyncReturn
from async import async
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.lobby.tank_setup.array_providers.consumable import ConsumableDeviceProvider
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabsController, ConsumableTabs
from gui.impl.lobby.tank_setup.sub_views.consumable_setup import ConsumableSetupSubView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent

class BootcampConsumableDeviceProvider(ConsumableDeviceProvider):

    def _fillStatus(self, model, item, slotID, isInstalledOrMounted):
        super(BootcampConsumableDeviceProvider, self)._fillStatus(model, item, slotID, isInstalledOrMounted)
        if not item.isInInventory:
            model.setIsDisabled(True)


class _BootcampConsumableTabsController(ConsumableTabsController):

    def _getAllProviders(self):
        return {ConsumableTabs.DEFAULT: BootcampConsumableDeviceProvider}


class BootcampConsumableSetupSubView(ConsumableSetupSubView):

    def onLoading(self, currentSlotID, *args, **kwargs):
        super(BootcampConsumableSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)
        self._viewModel.hints.addHintModel(TutorialHintConsts.APPLY_HANGAR_EQUIPMENT_MC)
        self._viewModel.hints.addHintModel(TutorialHintConsts.SETUP_VIEW_CARDS_EQUIPMENT_MC)
        if any(self._interactor.getCurrentLayout()):
            return
        items = self._provider.getItemsList()
        for item in items:
            if item.isInInventory:
                self._onSelectItem({'intCD': item.intCD,
                 'isAutoSelect': True})
                break

    def finalize(self):
        super(BootcampConsumableSetupSubView, self).finalize()
        self.__hideHints()

    @async
    def canQuit(self):
        result = yield super(BootcampConsumableSetupSubView, self).canQuit()
        if result:
            self.__hideHints()
        raise AsyncReturn(result)

    def _createTabsController(self):
        return _BootcampConsumableTabsController()

    @staticmethod
    def __hideHints():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.APPLY_HANGAR_EQUIPMENT_MC}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.SETUP_VIEW_CARDS_EQUIPMENT_MC}), EVENT_BUS_SCOPE.LOBBY)
