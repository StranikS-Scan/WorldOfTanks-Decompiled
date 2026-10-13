# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/comparison_window_view.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.items_parameters.params import VehicleParams
from halloween.gui.impl.gen.view_models.views.lobby.comparison_vehicle_model import ComparisonVehicleModel
from halloween.gui.impl.gen.view_models.views.lobby.comparison_view_model import ComparisonViewModel
from halloween.gui.impl.lobby.base_view import BaseView, HWLobbyWindow
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import COMPARISON_VIEW_ENTER, COMPARISON_VIEW_EXIT
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class ComparisonWindowView(BaseView):
    __slots__ = ()
    layoutID = R.views.halloween.mono.lobby.comparison()
    _itemsCache = dependency.descriptor(IItemsCache)
    _halloweenCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, model=ComparisonViewModel())
        super(ComparisonWindowView, self).__init__(settings)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.COMPARISON_VIEW)

    @property
    def viewModel(self):
        return super(ComparisonWindowView, self).getViewModel()

    def onPrbEntitySwitched(self):
        self._onClose()

    def _onLoading(self, *args, **kwargs):
        super(ComparisonWindowView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.onStartView(HWLogActions.LIFETIME)
        with self.viewModel.transaction() as model:
            vehicles = model.getVehicles()
            vehicles.clear()
            for vehicle in self._getVehicles():
                vehicleParams = VehicleParams(vehicle)
                relativePower = vehicleParams.relativePower
                speedLimit, _ = vehicleParams.speedLimits
                maxHealth = vehicleParams.maxHealth
                vehicleModel = ComparisonVehicleModel()
                vehicleModel.setVehicleName(getIconResourceName(vehicle.name))
                vehicleModel.setVehicleType(vehicle.type)
                vehicleModel.setUserName(vehicle.userName)
                vehicleModel.setRelativePower(relativePower)
                vehicleModel.setSpeedLimit(speedLimit)
                vehicleModel.setMaxHealth(maxHealth)
                vehicles.addViewModel(vehicleModel)

            vehicles.invalidate()

    def _getVehicles(self):
        return [ self._itemsCache.items.getItemByCD(intCD) for intCD in self._halloweenCtrl.getModeSettings().vehicles ]

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(ComparisonWindowView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(ComparisonWindowView, self)._initialize(*args, **kwargs)
        playSound(COMPARISON_VIEW_ENTER)

    def _finalize(self):
        self.__uiLogger.onStopView(HWLogActions.LIFETIME)
        super(ComparisonWindowView, self)._finalize()


class ComparisonWindow(HWLobbyWindow):

    def __init__(self, layoutID, parent=None):
        super(ComparisonWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=ComparisonWindowView(layoutID=layoutID), parent=parent)

    def _finalize(self):
        playSound(COMPARISON_VIEW_EXIT)
        super(ComparisonWindow, self)._finalize()
