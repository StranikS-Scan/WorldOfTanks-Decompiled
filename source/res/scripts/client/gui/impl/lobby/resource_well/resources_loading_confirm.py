# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/resources_loading_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.resource_well_helper import fillVehicleCounter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.loading_resource_model import LoadingResourceModel
from gui.impl.gen.view_models.views.lobby.resource_well.resources_loading_confirm_model import ResourcesLoadingConfirmModel, OperationType
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.resource_well.resources_sort import getResourceComparator
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
_FULL_PROGRESS = 100

class ResourcesLoadingConfirm(FullScreenDialogView):
    __slots__ = ('__resources', '__operation', '__additionalData', '__tooltips')
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, resources, isReturnOperation):
        settings = ViewSettings(R.views.lobby.resource_well.ResourcesLoadingConfirm())
        settings.model = ResourcesLoadingConfirmModel()
        super(ResourcesLoadingConfirm, self).__init__(settings)
        self.__resources = sorted(resources, cmp=getResourceComparator(), key=lambda x: x[0])
        self.__tooltips = []
        self.__operation = OperationType.RETURN if isReturnOperation else OperationType.CONTRIBUTE
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(ResourcesLoadingConfirm, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__tooltips[int(event.getArgument('tooltipId'))]
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
            return super(ResourcesLoadingConfirm, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(ResourcesLoadingConfirm, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            self.__fillResources(resourceModels=model.getResources())
            model.setOperationType(self.__operation)
            pointsDiff = sum((resource.rate * count for resource, count in self.__resources))
            currentPoints = self.__resourceWell.getCurrentPoints()
            model.setProgressDiff((pointsDiff + currentPoints) * _FULL_PROGRESS / self.__resourceWell.getMaxPoints())
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

    def _removeListeners(self):
        self.viewModel.confirm -= self._onAccept
        self.viewModel.cancel -= self.__onCancelAction
        self.viewModel.close -= self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated -= self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated

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
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self._onCancel()

    def __onCancelAction(self):
        self.__additionalData['isUserCancelAction'] = True
        self._onCancel()
