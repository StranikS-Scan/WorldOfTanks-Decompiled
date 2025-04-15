# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/resources_loading_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from resource_well.gui.feature.resource_well_helpers import fillVehicleCounter
from resource_well.gui.feature.resources_sort import getResourceComparator
from resource_well.gui.impl.gen.view_models.views.lobby.loading_resource_model import LoadingResourceModel
from resource_well.gui.impl.gen.view_models.views.lobby.resources_loading_confirm_model import ResourcesLoadingConfirmModel, OperationType
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from skeletons.gui.resource_well import IResourceWellController
_FULL_PROGRESS = 100

class ResourcesLoadingConfirm(FullScreenDialogView):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID, resources, isReturnOperation):
        settings = ViewSettings(R.views.resource_well.lobby.feature.ResourcesLoadingConfirm(), model=ResourcesLoadingConfirmModel())
        super(ResourcesLoadingConfirm, self).__init__(settings)
        self.__rewardID = rewardID
        self.__resources = sorted(resources, cmp=getResourceComparator(), key=lambda x: x[0])
        self.__tooltips = []
        if isReturnOperation:
            if self.__resourceWell.getCurrentRewardID() == self.__rewardID:
                self.__operation = OperationType.RETURN
            else:
                self.__operation = OperationType.SWITCH
        else:
            self.__operation = OperationType.CONTRIBUTE
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(ResourcesLoadingConfirm, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ResourcesLoadingConfirm, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips[int(tooltipId)]

    def _onLoading(self, *args, **kwargs):
        super(ResourcesLoadingConfirm, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            self.__fillResources(resourceModels=model.getResources())
            model.setOperationType(self.__operation)
            pointsDiff = sum((resource.rate * count for resource, count in self.__resources))
            currentPoints = self.__resourceWell.getCurrentPoints()
            maxPoints = self.__resourceWell.config.getRewardConfig(self.__rewardID).points
            model.setProgressDiff((pointsDiff + currentPoints) * _FULL_PROGRESS / maxPoints)
            if self.__operation == OperationType.SWITCH:
                rewardVehicle = self.__resourceWell.getRewardVehicle(self.__rewardID)
                model.setVehicleName(rewardVehicle.shortUserName)
        switchHangarFilteredFilter(on=True)

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        super(ResourcesLoadingConfirm, self)._finalize()

    def _addListeners(self):
        self.viewModel.confirm += self._onAccept
        self.viewModel.cancel += self.__onCancelAction
        self.viewModel.close += self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated += self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated += self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged += self.__onEventStateUpdated

    def _removeListeners(self):
        self.viewModel.confirm -= self._onAccept
        self.viewModel.cancel -= self.__onCancelAction
        self.viewModel.close -= self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated -= self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged -= self.__onEventStateUpdated

    def _getAdditionalData(self):
        return self.__additionalData

    def _setBaseParams(self, model):
        pass

    def __fillResources(self, resourceModels):
        resourceModels.clear()
        index = len(self.__tooltips)
        for tooltipId, (resource, count) in enumerate(self.__resources, index):
            resourceModel = LoadingResourceModel()
            self.__fillResourceModel(resource, count, resourceModel)
            resourceModel.setTooltipId(str(tooltipId))
            self.__tooltips.append(resource.tooltip)
            resourceModels.addViewModel(resourceModel)

        resourceModels.invalidate()

    def __fillResourceModel(self, resource, count, resourceModel):
        resourceModel.setType(resource.type)
        resourceModel.setSubType(resource.guiName)
        resourceModel.setCount(count)

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self._onCancel()

    def __onCancelAction(self):
        self.__additionalData['isUserCancelAction'] = True
        self._onCancel()
