# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/upgrades_panel.py
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.veh_post_progression.models.progression import PostProgressionCompletion
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_upgrades_panel_view_model import CompareUpgradesPanelViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.upgrades_model import UpgradesState, UpgradesModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import getFullProgressionState
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache

class CompareUpgradesPanelView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=R.views.mono.lobby.veh_skill_tree.comparison()):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=CompareUpgradesPanelViewModel())
        super(CompareUpgradesPanelView, self).__init__(settings)
        self.__vehItem = None
        return

    @property
    def viewModel(self):
        return super(CompareUpgradesPanelView, self).getViewModel()

    def update(self):
        selectedState = self.__getSelectedState()
        with self.viewModel.transaction() as vm:
            upgrades = vm.getUpgrades()
            upgrades.clear()
            upgrades.addViewModel(self.__createUpgradesModel(UpgradesState.ZERO_UPGRADES, selectedState == UpgradesState.ZERO_UPGRADES))
            if self.__hasPartialUpgrades():
                upgrades.addViewModel(self.__createUpgradesModel(UpgradesState.PARTIAL_UPGRADES, selectedState == UpgradesState.PARTIAL_UPGRADES))
            upgrades.addViewModel(self.__createUpgradesModel(UpgradesState.FULL_UPGRADES, selectedState == UpgradesState.FULL_UPGRADES))
            upgrades.invalidate()

    def _getEvents(self):
        events = super(CompareUpgradesPanelView, self)._getEvents()
        return events + ((self.viewModel.onSelectUpgrades, self.__onSelectUpgrades),)

    def _onLoading(self, *args, **kwargs):
        super(CompareUpgradesPanelView, self)._onLoading(*args, **kwargs)
        self.__vehItem = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicleItem()
        self.update()

    def _finalize(self):
        self.__vehItem = None
        super(CompareUpgradesPanelView, self)._finalize()
        return

    @args2params(UpgradesState)
    def __onSelectUpgrades(self, upgradeState):
        if upgradeState == UpgradesState.ZERO_UPGRADES:
            cmp_helpers.getCmpConfiguratorMainView().removePostProgression()
        elif upgradeState == UpgradesState.FULL_UPGRADES:
            fullState = getFullProgressionState(self.__vehItem.getItem())
            cmp_helpers.getCmpConfiguratorMainView().installPostProgression(fullState)
        elif upgradeState == UpgradesState.PARTIAL_UPGRADES:
            self.__vehItem.getItem().clearPostProgression()
            state = self.__vehItem.getItem().postProgression.getState()
            cmp_helpers.getCmpConfiguratorMainView().installPostProgression(state)

    def __getSelectedState(self):
        vehicle = self.__vehItem.getItem()
        completition = vehicle.postProgression.getCompletion()
        if completition == PostProgressionCompletion.FULL:
            return UpgradesState.FULL_UPGRADES
        elif completition == PostProgressionCompletion.EMPTY:
            return UpgradesState.ZERO_UPGRADES
        else:
            return UpgradesState.PARTIAL_UPGRADES if self.__hasPartialUpgrades() and completition == PostProgressionCompletion.PARTIAL else None

    def __hasPartialUpgrades(self):
        originalVehicle = self.__itemsCache.items.getItemByCD(self.__vehItem.getItem().intCD)
        return originalVehicle.isUnlocked and originalVehicle.postProgression.getCompletion() == PostProgressionCompletion.PARTIAL

    @staticmethod
    def __createUpgradesModel(state, isSelected):
        upgradesModel = UpgradesModel()
        upgradesModel.setState(state)
        upgradesModel.setIsSelected(isSelected)
        return upgradesModel
