# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/dialogs/alternate_configuration_dialog.py
import json
from functools import partial
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.veh_post_progression.tooltips.setup_tooltip_view import SetupTooltipView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory
from helpers import dependency
from items import vehicles
from post_progression_common import ACTION_TYPES, GROUP_ID_BY_FEATURE
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree import alternate_configuration_dialog_model
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree import alternate_configuration_dialog_loadout_model
_FEATURE_TO_LOADOUT_TYPE = {'shells_consumables_switch': alternate_configuration_dialog_loadout_model.LoadoutType.SHELLSCONSUMABLESSWITCH,
 'opt_dev_boosters_switch': alternate_configuration_dialog_loadout_model.LoadoutType.OPTDEVBOOSTERSSWITCH}
_LOADOUT_TYPE_TO_FEATURE = {loadoutType:feature for feature, loadoutType in _FEATURE_TO_LOADOUT_TYPE.items()}

class AlternateConfigurationDialog(FullScreenDialogBaseView):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.lobby.veh_skill_tree.dialogs.alternate_configuration())
        settings.model = alternate_configuration_dialog_model.AlternateConfigurationDialogModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__vehicle = None
        self.__feature = None
        self.__nodeID = None
        super(AlternateConfigurationDialog, self).__init__(settings, *args, **kwargs)
        return

    @property
    def viewModel(self):
        return super(AlternateConfigurationDialog, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.veh_post_progression.tooltip.SetupTooltipView():
            nodeID = event.getArgument('nodeID')
            eventType = event.getArgument('type')
            if self.__vehicle and nodeID and eventType:
                step = self.__vehicle.postProgression.getStep(nodeID)
                loadoutType = alternate_configuration_dialog_loadout_model.LoadoutType(eventType)
                feature = vehicles.g_cache.postProgression().getAction(ACTION_TYPES.FEATURE, GROUP_ID_BY_FEATURE[_LOADOUT_TYPE_TO_FEATURE[loadoutType]])
                return SetupTooltipView(step=step, feature=feature, isLevelShown=False)
        return super(AlternateConfigurationDialog, self).createToolTipContent(event, contentID)

    def _onLoading(self, vehIntCD, feature, nodeID, *args, **kwargs):
        super(AlternateConfigurationDialog, self)._onLoading(*args, **kwargs)
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehIntCD)
        self.__feature = feature
        self.__nodeID = nodeID
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onAffirmate, self.__onAffirmate), (self.__itemsCache.onSyncCompleted, self.__onInventoryResync))

    def __onInventoryResync(self, reason, diff):
        if self.__vehicle and self.__vehicle.intCD in diff.get(GUI_ITEM_TYPE.VEHICLE, {}):
            self.__vehicle = self.__itemsCache.items.getItemByCD(self.__vehicle.intCD)
            self.__update()

    def __onClose(self):
        self.destroyWindow()

    @args2params(str)
    def __onAffirmate(self, loadoutStates):
        for loadoutIndex, newState in enumerate(json.loads(loadoutStates)):
            loadoutModel = self.viewModel.getLoadouts()[loadoutIndex]
            groupID = GROUP_ID_BY_FEATURE[_LOADOUT_TYPE_TO_FEATURE[loadoutModel.getType()]]
            oldState = not self.__vehicle.postProgression.isPrebattleSwitchDisabled(groupID)
            if newState != oldState:
                BigWorld.callback(loadoutIndex, partial(self.__switchPrebattleAmmoPanelAvailability, groupID, newState))

        self.destroyWindow()

    def __switchPrebattleAmmoPanelAvailability(self, groupID, newState):
        factory.doAction(factory.SWITCH_PREBATTLE_AMMO_PANEL_AVAILABILITY, self.__vehicle, groupID, newState)

    def __update(self):
        if self.__vehicle is None or self.__feature is None or self.__nodeID is None:
            return
        else:
            with self.viewModel.transaction() as vm:
                self.__fillLoadouts(vm)
                fillVehicleInfo(vm.vehicleInfo, self.__vehicle)
                vm.setNodeID(self.__nodeID)
            return

    def __fillLoadouts(self, viewModel):
        loadouts = viewModel.getLoadouts()
        loadouts.clear()
        featureName = self.__feature.getTechName()
        self.__fillLoadout(loadouts, featureName)
        loadouts.invalidate()

    def __fillLoadout(self, loadouts, featureName):
        groupID = GROUP_ID_BY_FEATURE[featureName]
        loadout = alternate_configuration_dialog_loadout_model.AlternateConfigurationDialogLoadoutModel()
        loadout.setType(_FEATURE_TO_LOADOUT_TYPE[featureName])
        loadout.setIconName(vehicles.g_cache.postProgression().getAction(ACTION_TYPES.FEATURE, groupID).imgName)
        loadout.setIsSelected(not self.__vehicle.postProgression.isPrebattleSwitchDisabled(groupID))
        loadouts.addViewModel(loadout)
