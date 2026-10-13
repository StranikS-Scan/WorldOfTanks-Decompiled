# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/hw_loadout.py
from __future__ import absolute_import
import typing
from account_helpers.settings_core.options import KeyboardSetting
from account_helpers.settings_core.settings_constants import CONTROLS
from CurrentVehicle import g_currentVehicle
from constants import LoadoutParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import _LoadoutStatesObserver, LoadoutPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutEntityProvider
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabs
from gui.impl.pub import ToolTipWindow
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.halloween_account_settings import getSettings, AccountSettingsKeys
from halloween.gui.halloween_gui_constants import AmmoPanelSwitchPreset, HALLOWEEN_ABILITY_TOOLTIP, HALLOWEEN_MAIN_SHELL
from halloween.gui.impl.gen.view_models.views.lobby.ext_ammo_panel_view import ExtAmmoPanelView
from halloween.gui.impl.lobby.hw_ammunition_panel_view import HWHangarAmmunitionGroupsController, _CMD_ACCELERATION_ABILITY_KEY
from halloween.gui.impl.lobby.hw_helpers.anomalies_helpers import isAnomaliesSystemAvailable
from halloween.gui.impl.lobby.tank_setup import HWTankSetupConstants
from halloween.gui.impl.lobby.tank_setup.array_provider import HalloweenConsumableProvider
from halloween.gui.impl.lobby.tank_setup.interactor import HalloweenInteractor
from halloween.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltipView
from halloween.gui.impl.lobby.tooltips.anomalies_entry_point_tooltip import AnomaliesEntryPointTooltipView
from halloween.gui.shared.event_dispatcher import showModuleInfo
from halloween_common.halloween_constants import HW_BUILT_IN_EQUIPMENT
from helpers import dependency
from items import vehicles
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController
_TOOLTIPS_OVERRIDES = {TOOLTIPS_CONSTANTS.HANGAR_MODULE: HALLOWEEN_ABILITY_TOOLTIP,
 TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL: HALLOWEEN_MAIN_SHELL}
_PRESET_GROUP_SECTIONS = {AmmoPanelSwitchPreset.PRESET_1: [[TankSetupConstants.SHELLS, HWTankSetupConstants.HW_CONSUMABLES], [TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS]],
 AmmoPanelSwitchPreset.PRESET_2: [[HWTankSetupConstants.HW_CONSUMABLES, TankSetupConstants.SHELLS], [TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS]]}

def getCurrentPreset():
    preset = getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET)
    return _PRESET_GROUP_SECTIONS.get(preset, [])


class _HalloweenLoadoutStatesObserver(_LoadoutStatesObserver):
    _GROUP_SECTIONS_NAMES = _PRESET_GROUP_SECTIONS.get(AmmoPanelSwitchPreset.PRESET_1)

    @property
    def _stateID(self):
        from halloween.gui.impl.lobby.states import HalloweenLoadoutState
        return HalloweenLoadoutState.STATE_ID

    def onEnterState(self, state, event):
        self.onPanelSlotSelect(event.params.get(LoadoutParams.groupId), event.params.get(LoadoutParams.sectionName), event.params.get(LoadoutParams.slotIndex))


class HalloweenLoadoutPresenter(LoadoutPresenter):
    __settingsCore = dependency.descriptor(ISettingsCore)
    _VIEW_MODEL = ExtAmmoPanelView
    _STATES_OBSERVER = _HalloweenLoadoutStatesObserver

    def createToolTip(self, event):
        backportTooltipContentID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
        isBackportContentId = event.contentID == R.aliases.common.tooltip.Backport() or event.contentID == backportTooltipContentID
        if isBackportContentId and g_currentVehicle.isPresent():
            tooltipData = self._getBackportTooltipData(event)
            if tooltipData is not None:
                ovverideSpecialAlias = _TOOLTIPS_OVERRIDES.get(tooltipData.specialAlias, tooltipData.specialAlias)
                if ovverideSpecialAlias in [HALLOWEEN_ABILITY_TOOLTIP, TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT]:
                    window = ToolTipWindow(event, AbilityTooltipView(intCD=event.getArgument('intCD')), self.getParentWindow())
                    window.load()
                    return window
                tooltipData = TooltipData(tooltipData.tooltip, tooltipData.isSpecial, ovverideSpecialAlias, tooltipData.specialArgs, tooltipData.isWulfTooltip)
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        if event.contentID == R.views.halloween.mono.lobby.tooltips.anomalies_entry_point_tooltip() and not isAnomaliesSystemAvailable():
            locRes = R.strings.halloween_tooltips.anomaliesEntryPoint.locked
            return createSimpleTooltip(self.getParentWindow(), event, backport.text(locRes.header()), backport.text(locRes.body()))
        else:
            return super(HalloweenLoadoutPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.ability_tooltip():
            intCD = event.getArgument('intCD')
            showPriceBlock = event.getArgument('showPriceBlock')
            return AbilityTooltipView(intCD=intCD, showPriceBlock=showPriceBlock)
        return AnomaliesEntryPointTooltipView() if contentID == R.views.halloween.mono.lobby.tooltips.anomalies_entry_point_tooltip() and isAnomaliesSystemAvailable() else super(HalloweenLoadoutPresenter, self).createToolTipContent(event, contentID)

    def _createAmmunitionGroupsController(self, vehicle):
        return HWHangarAmmunitionGroupsController(vehicle)

    def _onLoading(self, *args):
        super(HalloweenLoadoutPresenter, self)._onLoading(*args)
        self.getViewModel().setAccelerationKeyName(KeyboardSetting(_CMD_ACCELERATION_ABILITY_KEY).getKeyName())
        intCD = vehicles.g_cache.getEquipmentByName(HW_BUILT_IN_EQUIPMENT[0]).compactDescr
        self.getViewModel().setAccelerationIntCD(intCD)

    def _getEvents(self):
        return super(HalloweenLoadoutPresenter, self)._getEvents() + ((self.__settingsCore.onSettingsApplied, self.__onSettingsApplied),)

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            self.getViewModel().setAccelerationKeyName(KeyboardSetting(_CMD_ACCELERATION_ABILITY_KEY).getKeyName())

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : ShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : HalloweenConsumablesPresenter(self._vehInteractingItem),
         R.aliases.halloween.shared.PresetsSwitcher(): lambda : HalloweenPresetSwitcher(self._getGroupController, self.getViewModel())}


class HalloweenPresetSwitcher(ViewComponent[ExtAmmoPanelView]):

    def __init__(self, groupController=None, panelViewModel=None):
        super(HalloweenPresetSwitcher, self).__init__(model=ExtAmmoPanelView)
        self.__groupController = groupController
        self.__panelViewModel = panelViewModel

    def _getEvents(self):
        return ((self.getViewModel().onSwitch, self.__onSwitch),)

    def __onSwitch(self):
        self.__groupController.setNextPreset(self.__panelViewModel)


class HalloweenConsumablesPresenter(ConsumablesPresenter):

    def __init__(self, interactingItem):
        super(HalloweenConsumablesPresenter, self).__init__(interactingItem)
        self._sectionName = HWTankSetupConstants.HW_CONSUMABLES

    def createSlotActions(self):
        actions = super(HalloweenConsumablesPresenter, self).createSlotActions()
        actions.update({BaseSetupModel.SHOW_INFO_SLOT_ACTION: self._onShowItemInfo})
        return actions

    def _onShowItemInfo(self, args):
        itemIntCD = int(args.get('intCD'))
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, HalloweenInteractor, {ConsumableTabs.DEFAULT: HalloweenConsumableProvider})
