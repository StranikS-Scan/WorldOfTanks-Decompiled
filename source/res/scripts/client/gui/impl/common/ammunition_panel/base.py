# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/ammunition_panel/base.py
import logging
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.impl.common.base_sub_model_view import BaseSubModelView
_logger = logging.getLogger(__name__)

class BaseAmmunitionPanel(BaseSubModelView):
    __slots__ = ('_vehicle', '_controller', '_ctx')

    def __init__(self, viewModel, vehicle, ctx=None):
        super(BaseAmmunitionPanel, self).__init__(viewModel)
        self._vehicle = vehicle
        self._ctx = ctx
        self._controller = self._createAmmunitionGroupsController(vehicle)

    @property
    def viewModel(self):
        return self._viewModel

    def onLoading(self, *args, **kwargs):
        super(BaseAmmunitionPanel, self).onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            if kwargs:
                self.changeSelectedSection(**kwargs)
            self._controller.createGroupsModels(model.getSectionGroups())

    def finalize(self):
        super(BaseAmmunitionPanel, self).finalize()
        self._controller.finalize()
        self._controller = None
        return

    def update(self, vehicle, fullUpdate=False):
        self.updateVehicle(vehicle)
        with self.viewModel.transaction() as model:
            if fullUpdate or vehicle is None:
                self._controller.createGroupsModels(model.getSectionGroups())
            else:
                self._controller.updateGroupsModels(model.getSectionGroups())
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)
        return

    def updateVehicle(self, vehicle):
        self._vehicle = vehicle
        self._controller.updateVehicle(vehicle)

    def updateSection(self, sectionName):
        with self.viewModel.transaction() as model:
            self._controller.updateGroupSectionModel(sectionName, model.getSectionGroups())
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    def changeSelectedSection(self, selectedSection, selectedSlot):
        if selectedSection or selectedSection == '':
            self.viewModel.setSelectedSection(selectedSection)
            self.viewModel.setSelectedSlot(selectedSlot)
            self._controller.updateCurrentSection(selectedSection)

    def isNewSetupLayoutIndexValid(self, hudGroupID, newLayoutIdx):
        groupID = GROUPS_MAP.get(hudGroupID, None)
        layoutIdx = self._vehicle.setupLayouts.getLayoutIndex(groupID)
        capacity = self._vehicle.setupLayouts.getGroupCapacity(groupID)
        return newLayoutIdx != layoutIdx and layoutIdx >= 0 and layoutIdx < capacity

    def getSectionsByGroup(self, groupID):
        return self._controller.getSectionsByGroup(groupID)

    def getGroupIdBySection(self, sectionName):
        hudGroupID = self._controller.getGroupIdBySection(sectionName)
        return GROUPS_MAP.get(hudGroupID, None)

    def _updateSwitchingProgress(self, isInProgress):
        self.viewModel.setIsSetupSwitchInProgress(isInProgress)

    def _createAmmunitionGroupsController(self, vehicle):
        raise NotImplementedError
