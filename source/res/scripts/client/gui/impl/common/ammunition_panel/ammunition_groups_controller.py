# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/ammunition_panel/ammunition_groups_controller.py
from collections import namedtuple
from post_progression_common import TankSetupGroupsId
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_group import AmmunitionItemsGroup
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_setup_selector import SetupStates
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import AmmunitionBlocksController
GroupData = namedtuple('GroupData', 'groupID sections')
GROUPS_MAP = {AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS: TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS,
 AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS: TankSetupGroupsId.EQUIPMENT_AND_SHELLS}
RANDOM_GROUPS = (GroupData(AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, (TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS)), GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, (TankSetupConstants.SHELLS, TankSetupConstants.CONSUMABLES)))
FRONTLINE_GROUPS = RANDOM_GROUPS + (GroupData(AmmunitionPanelConstants.NO_GROUP, (TankSetupConstants.BATTLE_ABILITIES,)),)
HALLOWEEN_GROUPS = (GroupData(AmmunitionPanelConstants.NO_GROUP, (TankSetupConstants.HWCONSUMABLES,)),) + RANDOM_GROUPS

class AmmunitionGroupsController(object):
    __slots__ = ('_vehicle', '_controller', '_autoCreating')

    def __init__(self, vehicle, autoCreating=True, ctx=None):
        self._vehicle = vehicle
        self._controller = self._createAmmunitionBlockController(vehicle, ctx)
        self._autoCreating = autoCreating

    def updateVehicle(self, vehicle):
        self._vehicle = vehicle
        self._controller.updateVehicle(vehicle)

    def updateCurrentSection(self, currentSection):
        self._controller.updateCurrentSection(currentSection)

    def createGroupsModels(self, groupsArray):
        groups = self._getGroups()
        if len(groupsArray) != len(groups):
            groupsArray.clear()
            for group in groups:
                viewModel = self._createViewModel()
                self._updateGroupModel(viewModel, group)
                groupsArray.addViewModel(viewModel)

        else:
            for idx, group in enumerate(groups):
                self._updateGroupModel(groupsArray[idx], group)

        self._autoCreating = False
        groupsArray.invalidate()

    def updateGroupsModels(self, groupsArray):
        if self._autoCreating:
            self.createGroupsModels(groupsArray)
            return
        else:
            for viewModel in groupsArray:
                hudGroupID = viewModel.getGroupId()
                groupID = GROUPS_MAP.get(hudGroupID, None)
                layoutIdx = self._vehicle.setupLayouts.getLayoutIndex(groupID)
                capacity = self._vehicle.setupLayouts.getGroupCapacity(groupID)
                viewModel.setCurrentIndex(layoutIdx)
                viewModel.setTotalCount(capacity)
                for group in self._getGroups():
                    if hudGroupID == group.groupID:
                        self._setupStates(viewModel.setupSelector, group)
                        break

                self._controller.updateTabModels(viewModel.getSections())

            groupsArray.invalidate()
            return

    def updateGroupSectionModel(self, sectionName, groupsArray):
        groupID = self.getGroupIdBySection(sectionName)
        for viewModel in groupsArray:
            if viewModel.getGroupId() == groupID:
                self._controller.updateTabModel(sectionName, viewModel.getSections())
                break

    def updateGroupModel(self, groupID, groupsArray):
        for viewModel in groupsArray:
            if viewModel.getGroupId() == groupID:
                self._controller.updateTabModels(viewModel.getSections())
                break

    def finalize(self):
        self._controller = None
        return

    def getSectionsByGroup(self, groupID):
        for group in self._getGroups():
            if groupID == group.groupID:
                return group.sections

        return None

    def getGroupIdBySection(self, sectionName):
        for group in self._getGroups():
            if sectionName in group.sections:
                return group.groupID

        return AmmunitionPanelConstants.NO_GROUP

    def _updateGroupModel(self, viewModel, group):
        hudGroupID = group.groupID
        viewModel.setGroupId(hudGroupID)
        groupID = GROUPS_MAP.get(hudGroupID, None)
        layoutIdx = self._vehicle.setupLayouts.getLayoutIndex(groupID)
        capacity = self._vehicle.setupLayouts.getGroupCapacity(groupID)
        viewModel.setCurrentIndex(layoutIdx)
        viewModel.setTotalCount(capacity)
        self._setupStates(viewModel.setupSelector, group)
        self._controller.addSections(group)
        self._controller.createTabModels(viewModel.getSections(), groupID=group.groupID)
        return

    def _setupStates(self, setupSelectorModel, groupSettings):
        isSwitchEnabled = self._isSwitchEnabled(groupSettings)
        setupSelectorModel.setIsSwitchEnabled(isSwitchEnabled)
        setupSelectorModel.setIsPrebattleSwitchDisabled(self._isPrebattleSwitchDisabled(groupSettings))
        states = setupSelectorModel.getStates()
        states.clear()
        if isSwitchEnabled:
            hudGroupID = groupSettings.groupID
            groupID = GROUPS_MAP.get(hudGroupID, None)
            capacity = self._vehicle.setupLayouts.getGroupCapacity(groupID)
            for layoutIdx in range(capacity):
                state = SetupStates.NORMAL
                for sectionName in groupSettings.sections:
                    if sectionName == TankSetupConstants.SHELLS and not self._vehicle.shells.setupLayouts.isAmmoFull(layoutIdx, self._vehicle.ammoMinSize):
                        state = SetupStates.WARNING
                        break

                states.addNumber(state)

        states.invalidate()
        return

    def _isSwitchEnabled(self, groupSettings):
        hudGroupID = groupSettings.groupID
        if hudGroupID == AmmunitionPanelConstants.NO_GROUP or self._vehicle is None:
            return False
        else:
            groupID = GROUPS_MAP.get(hudGroupID, None)
            return groupID is not None and self._vehicle.isSetupSwitchActive(groupID)

    def _isPrebattleSwitchDisabled(self, groupSettings):
        groupID = GROUPS_MAP.get(groupSettings.groupID)
        return False if groupID is None else self._vehicle.postProgression.isPrebattleSwitchDisabled(groupID)

    def _getGroups(self):
        return []

    def _createViewModel(self):
        return AmmunitionItemsGroup()

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return AmmunitionBlocksController(vehicle, ctx=ctx)
