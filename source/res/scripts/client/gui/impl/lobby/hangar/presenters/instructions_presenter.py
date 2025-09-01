# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/instructions_presenter.py
from __future__ import absolute_import
import typing
import SoundGroups
from gui.impl.gen.view_models.views.lobby.loadout.instructions.instructions_model import InstructionsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutPresenterBase, LoadoutEntityProvider
from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
from gui.impl.lobby.tank_setup.array_providers.battle_booster import OptDeviceBattleBoosterProvider, CrewBattleBoosterProvider
from gui.impl.lobby.tank_setup.configurations.battle_booster import BattleBoosterTabs
from gui.impl.lobby.tank_setup.interactors.battle_booster import BattleBoosterInteractor
from gui.impl.lobby.tank_setup.tank_setup_sounds import TankSetupSoundEvents
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.interactors.base import InteractingItem

class InstructionsPresenter(LoadoutPresenterBase[InstructionsModel]):
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, interactingItem):
        super(InstructionsPresenter, self).__init__(interactingItem, model=InstructionsModel)
        self._sectionName = TankSetupConstants.BATTLE_BOOSTERS
        self._guiItemType = GUI_ITEM_TYPE.EQUIPMENT

    def createSlotActions(self):
        actions = {BaseSetupModel.ADD_ONE_SLOT_ACTION: self.__onAdd}
        actions.update(super(InstructionsPresenter, self).createSlotActions())
        return actions

    def _getEvents(self):
        return super(InstructionsPresenter, self)._getEvents() + ((self.__wallet.onWalletStatusChanged, self._onCurrencyUpdate),)

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, BattleBoosterInteractor, {BattleBoosterTabs.OPT_DEVICE: OptDeviceBattleBoosterProvider,
         BattleBoosterTabs.CREW: CrewBattleBoosterProvider})

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.GOLD), self._onCurrencyUpdate), ('stats.{}'.format(Currency.CREDITS), self._onCurrencyUpdate), ('stats.{}'.format(Currency.CRYSTAL), self._onCurrencyUpdate))

    def _updateInteractor(self, item=None):
        super(InstructionsPresenter, self)._updateInteractor(item)
        instructionsLayout = self._interactor.getCurrentLayout()
        instructionsInstalled = self._interactor.getInstalledLayout()
        for i, instruction in enumerate(instructionsLayout):
            if instruction is not None and instruction.isHidden and not instruction.isInInventory and instruction not in instructionsInstalled:
                self._interactor.changeSlotItem(i, None)
                self._interactor.getAutoRenewal().setLocalValue(False)

        return

    def _updateModel(self, recreate=True):
        if not self._vehInteractingItem.getItem().battleBoosters.installed and not self._vehInteractingItem.getItem().battleAbilities.installed or not self._provider:
            return
        interactor = self._provider.interactor
        dataProviders = self._provider.dataProviders
        equipmentInstructionsDataProvider = dataProviders[BattleBoosterTabs.OPT_DEVICE]
        crewInstructionsDataProvider = dataProviders[BattleBoosterTabs.CREW]
        with self.getViewModel().transaction() as instructModel:
            instructModel.setAutoloadEnabled(interactor.getAutoRenewal().getLocalValue())
            if recreate:
                equipmentInstructionsDataProvider.fillArray(instructModel.getEquipmentInstructions(), BaseVehSectionContext(self._currentSlotIndex))
                crewInstructionsDataProvider.fillArray(instructModel.getCrewInstructions(), BaseVehSectionContext(self._currentSlotIndex))
            else:
                equipmentInstructionsDataProvider.updateArray(instructModel.getEquipmentInstructions(), BaseVehSectionContext(self._currentSlotIndex))
                crewInstructionsDataProvider.updateArray(instructModel.getCrewInstructions(), BaseVehSectionContext(self._currentSlotIndex))
        self._updateDealPanel()

    def _onRevertItem(self, args):
        SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.INSTRUCTIONS_DEMOUNT)
        super(InstructionsPresenter, self)._onRevertItem(args)

    def __onAdd(self, args):
        itemIntCD = int(args.get('intCD'))
        self._interactor.buyMore(itemIntCD)
