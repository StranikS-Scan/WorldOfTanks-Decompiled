# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/consumables_presenter.py
from __future__ import absolute_import
import typing
import SoundGroups
from gui.impl.gen.view_models.views.lobby.loadout.consumables.consumables_model import ConsumablesModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutPresenterBase, LoadoutEntityProvider
from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
from gui.impl.lobby.tank_setup.array_providers.consumable import ConsumableDeviceProvider
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabs
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.impl.lobby.tank_setup.tank_setup_sounds import TankSetupSoundEvents
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.interactors.base import InteractingItem

class ConsumablesPresenter(LoadoutPresenterBase[ConsumablesModel]):
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, interactingItem):
        super(ConsumablesPresenter, self).__init__(interactingItem, model=ConsumablesModel)
        self._sectionName = TankSetupConstants.CONSUMABLES
        self._guiItemType = GUI_ITEM_TYPE.EQUIPMENT

    def createSlotActions(self):
        actions = {BaseSetupModel.ADD_ONE_SLOT_ACTION: self.__onAdd}
        actions.update(super(ConsumablesPresenter, self).createSlotActions())
        return actions

    def _getEvents(self):
        return super(ConsumablesPresenter, self)._getEvents() + ((self.__wallet.onWalletStatusChanged, self._onCurrencyUpdate),)

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, ConsumableInteractor, {ConsumableTabs.DEFAULT: ConsumableDeviceProvider})

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.GOLD), self._onCurrencyUpdate), ('stats.{}'.format(Currency.CREDITS), self._onCurrencyUpdate))

    def _updateModel(self, recreate=True):
        if not self._vehInteractingItem.getItem().consumables.installed or not self._provider:
            return
        interactor = self._provider.interactor
        with self.getViewModel().transaction() as consumableModel:
            consumableModel.setAutoloadEnabled(interactor.getAutoRenewal().getLocalValue())
            dataProvider = self._provider.dataProviders[ConsumableTabs.DEFAULT]
            if recreate:
                dataProvider.fillArray(consumableModel.getConsumables(), BaseVehSectionContext(self._currentSlotIndex))
            else:
                dataProvider.updateArray(consumableModel.getConsumables(), BaseVehSectionContext(self._currentSlotIndex))
        self._updateDealPanel()

    def _onRevertItem(self, args):
        SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.CONSUMABLES_DEMOUNT)
        super(ConsumablesPresenter, self)._onRevertItem(args)

    def __onAdd(self, args):
        itemIntCD = int(args.get('intCD'))
        self._interactor.buyMore(itemIntCD)
