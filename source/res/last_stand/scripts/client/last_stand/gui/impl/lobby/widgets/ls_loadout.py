# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/ls_loadout.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle
from constants import LoadoutParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import _LoadoutStatesObserver, LoadoutPresenter
from gui.impl.pub.view_component import ViewComponent
from last_stand.gui.impl.gen.view_models.views.lobby.ext_ammo_panel_view import ExtAmmoPanelView
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutEntityProvider
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabs
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel
from last_stand.gui.impl.lobby.hangar_ammunition_panel_view import LSHangarAmmunitionGroupsController
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from last_stand.gui.impl.lobby.tank_setup.array_provider import LSConsumableProvider
from last_stand.gui.impl.lobby.tank_setup.interactor import LSConsumableInteractor
from last_stand.gui.ls_account_settings import getSettings, AccountSettingsKeys
from last_stand.gui.ls_gui_constants import AmmoPanelSwitchPreset, LS_ABILITY_TOOLTIP, LS_MAIN_SHELL
from last_stand.gui.shared.event_dispatcher import showModuleInfo
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import CONSUMABLES_VIEW_ENTER, CONSUMABLES_VIEW_EXIT
if typing.TYPE_CHECKING:
    from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController
_TOOLTIPS_OVERRIDES = {TOOLTIPS_CONSTANTS.HANGAR_MODULE: LS_ABILITY_TOOLTIP,
 TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL: LS_MAIN_SHELL}
_PRESET_GROUP_SECTIONS = {AmmoPanelSwitchPreset.PRESET_1: [[TankSetupConstants.SHELLS, LSTankSetupConstants.LS_CONSUMABLES], [TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS]],
 AmmoPanelSwitchPreset.PRESET_2: [[LSTankSetupConstants.LS_CONSUMABLES, TankSetupConstants.SHELLS], [TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS]]}

def getCurrentPreset():
    preset = getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET)
    return _PRESET_GROUP_SECTIONS.get(preset, [])


class _LastStandLoadoutStatesObserver(_LoadoutStatesObserver):

    @property
    def _stateID(self):
        from last_stand.gui.impl.lobby.states import LastStandLoadoutState
        return LastStandLoadoutState.STATE_ID

    def onEnterState(self, state, event):
        self.onPanelSlotSelect(event.params.get(LoadoutParams.groupId), event.params.get(LoadoutParams.sectionName), event.params.get(LoadoutParams.slotIndex))

    def onStateChanged(self, state, stateEntered, event=None):
        if state.getStateID() == self._stateID:
            playSound(CONSUMABLES_VIEW_ENTER if stateEntered else CONSUMABLES_VIEW_EXIT)
        super(_LastStandLoadoutStatesObserver, self).onStateChanged(state, stateEntered, event)


class LastStandLoadoutPresenter(LoadoutPresenter):
    _VIEW_MODEL = AmmunitionPanelModel
    _STATES_OBSERVER = _LastStandLoadoutStatesObserver

    def createToolTip(self, event):
        backportTooltipContentID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
        isBackportContentId = event.contentID == R.aliases.common.tooltip.Backport() or event.contentID == backportTooltipContentID
        if isBackportContentId and g_currentVehicle.isPresent():
            tooltipData = self._getBackportTooltipData(event)
            if tooltipData is not None:
                ovverideSpecialAlias = _TOOLTIPS_OVERRIDES.get(tooltipData.specialAlias, tooltipData.specialAlias)
                tooltipData = TooltipData(tooltipData.tooltip, tooltipData.isSpecial, ovverideSpecialAlias, tooltipData.specialArgs, tooltipData.isWulfTooltip)
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(LastStandLoadoutPresenter, self).createToolTip(event)

    def _createAmmunitionGroupsController(self, vehicle):
        return LSHangarAmmunitionGroupsController(vehicle)

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : ShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : LastStandConsumablesPresenter(self._vehInteractingItem),
         R.aliases.last_stand.shared.PresetsSwitcher(): lambda : LastStandPresetSwitcher(self._getGroupController, self.getViewModel())}


class LastStandPresetSwitcher(ViewComponent[ExtAmmoPanelView]):

    def __init__(self, groupController=None, panelViewModel=None):
        super(LastStandPresetSwitcher, self).__init__(model=ExtAmmoPanelView)
        self.__groupController = groupController
        self.__panelViewModel = panelViewModel

    def _getEvents(self):
        return ((self.getViewModel().onSwitch, self.__onSwitch),)

    def __onSwitch(self):
        self.__groupController.setNextPreset(self.__panelViewModel)


class LastStandConsumablesPresenter(ConsumablesPresenter):

    def __init__(self, interactingItem):
        super(LastStandConsumablesPresenter, self).__init__(interactingItem)
        self._sectionName = LSTankSetupConstants.LS_CONSUMABLES

    def createSlotActions(self):
        actions = super(LastStandConsumablesPresenter, self).createSlotActions()
        actions.update({BaseSetupModel.SHOW_INFO_SLOT_ACTION: self._onShowItemInfo})
        return actions

    def _onShowItemInfo(self, args):
        itemIntCD = int(args.get('intCD'))
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)

    def _getCallbacks(self):
        callbacks = super(LastStandConsumablesPresenter, self)._getCallbacks()
        return callbacks + (('LS_inventory', self._onLSInventoryUpdate),)

    def _onLSInventoryUpdate(self, invDiff):
        if g_currentVehicle.isPresent():
            g_currentVehicle.onChanged()

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, LSConsumableInteractor, {ConsumableTabs.DEFAULT: LSConsumableProvider})
