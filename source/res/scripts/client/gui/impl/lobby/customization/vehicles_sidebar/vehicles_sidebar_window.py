# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/vehicles_sidebar/vehicles_sidebar_window.py
import logging
from gui import GUI_NATIONS_ORDER_INDEX
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from frameworks.wulf import ViewSettings
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.customization.vehicles_sidebar.customization_3D_attachments import Customization3DAttachments
from gui.impl.gen.view_models.views.lobby.customization.vehicles_sidebar.vehicles_sidebar_model import VehiclesSidebarModel
from gui.impl.gen.view_models.views.lobby.customization.vehicles_sidebar.vehicles_sidebar_item_model import VehiclesSidebarItemModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.common.components_presenter import ComponentsPresenterView
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from uilogging.customization_3d_objects.logger import VehicleSidebarLogger
from uilogging.customization_3d_objects.logging_constants import CustomizationViewKeys
_logger = logging.getLogger(__name__)

class VehiclesSidebarView(ComponentsPresenterView, FullScreenDialogBaseView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, layoutID, parentScreen, *args, **kwargs):
        settings = ViewSettings(layoutID, model=VehiclesSidebarModel(), args=args, kwargs=kwargs)
        super(VehiclesSidebarView, self).__init__(settings)
        self.__uiLogger = VehicleSidebarLogger(parentScreen)

    def _onLoading(self, *args, **kwargs):
        super(VehiclesSidebarView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _onLoaded(self, *args, **kwargs):
        self.__uiLogger.onViewOpen(CustomizationViewKeys.VEHICLES_LIST)
        super(VehiclesSidebarView, self)._onLoaded(*args, **kwargs)

    def _finalize(self):
        self.__uiLogger.onViewClose(CustomizationViewKeys.VEHICLES_LIST)
        self.__uiLogger = None
        super(VehiclesSidebarView, self)._finalize()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getCallbacks(self):
        callbacks = super(VehiclesSidebarView, self)._getCallbacks()
        return callbacks

    def _getEvents(self):
        eventsTuple = super(VehiclesSidebarView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        vehiclesModel = model.getVehiclesSelection()
        vehiclesModel.clear()
        self.__updateVehiclesModel(model=model)
        vehiclesModel.invalidate()

    def _registerSubModels(self):
        return []

    def __updateVehiclesModel(self, model=None):
        vehiclesModel = model.getVehiclesSelection()
        vehicles = self.__service.getVehiclesWithAttachmentSlot()
        for vehicle in vehicles:
            vehicleModel = VehiclesSidebarItemModel()
            fillVehicleModel(vehicleModel, vehicle)
            vehicleModel.setInDepot(vehicle.isInInventory)
            vehicleModel.setNationOrder(GUI_NATIONS_ORDER_INDEX[vehicle.nationName])
            customization3DAttachments = Array()
            attachments = self.__service.getAppliedAttachments(vehicle.intCD)
            for attachment in attachments:
                customization3DAttachmentsModel = Customization3DAttachments()
                customization3DAttachmentsModel.setName(attachment.userName)
                customization3DAttachmentsModel.setAmount(attachment.installedCount(vehicle.intCD))
                customization3DAttachments.addViewModel(customization3DAttachmentsModel)

            vehicleModel.setCustomization3DAttachments(customization3DAttachments)
            vehiclesModel.addViewModel(vehicleModel)
