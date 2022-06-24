# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/completed_progression_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.completed_progression_view_model import CompletedProgressionViewModel
from gui.impl.lobby.resource_well.tooltips.serial_number_tooltip import SerialNumberTooltip
from gui.impl.pub import ViewImpl
from gui.resource_well.resource_well_helpers import getSerialNumber
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar, showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD
from uilogging.resource_well.loggers import ResourceWellCompletedScreenLogger

class CompletedProgressionView(ViewImpl):
    __slots__ = ('__vehicle', '__backCallback')
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)
    __uiLogger = ResourceWellCompletedScreenLogger()

    def __init__(self, layoutID, backCallback):
        settings = ViewSettings(R.views.lobby.resource_well.CompletedProgressionView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CompletedProgressionViewModel()
        self.__backCallback = backCallback
        self.__vehicle = getVehicleByIntCD(self.__resourceWell.getRewardVehicle())
        super(CompletedProgressionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CompletedProgressionView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SerialNumberTooltip(parentLayout=self.layoutID) if contentID == R.views.lobby.resource_well.tooltips.SerialNumberTooltip() else super(CompletedProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(CompletedProgressionView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _onLoaded(self, *args, **kwargs):
        super(CompletedProgressionView, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onViewOpened()

    def _finalize(self):
        self.__uiLogger.onViewClosed()
        super(CompletedProgressionView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showEventInfo),
         (self.viewModel.onClose, self.__close),
         (self.viewModel.onShowVehicle, self.__showVehicle),
         (self.__resourceWell.onEventUpdated, self.__onEventUpdated))

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            serialNumber = getSerialNumber(resourceWell=self.__resourceWell)
            model.setIsTop(bool(serialNumber))
            model.setPersonalNumber(serialNumber)
            fillVehicleInfo(model.vehicleInfo, self.__vehicle)

    def __close(self):
        if callable(self.__backCallback):
            self.__backCallback()
        else:
            showHangar()
        self.destroyWindow()

    def __showEventInfo(self):
        showBrowserOverlayView(GUI_SETTINGS.resourceWell.get('infoPage'), VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW)

    def __showVehicle(self):
        if self.__vehicle.isInInventory:
            selectVehicleInHangar(self.__vehicle.intCD)
        else:
            showHangar()

    def __onEventUpdated(self):
        if not self.__resourceWell.isActive():
            showHangar()
