# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/views/no_vehicles_screen.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.views.no_vehicles_screen_model import NoVehiclesScreenModel
from gui.impl.gen.view_models.views.lobby.comp7.views.no_vehicles_screen_model import ErrorReason
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class NoVehiclesScreen(ViewImpl):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = NoVehiclesScreenModel()
        super(NoVehiclesScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NoVehiclesScreen, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(NoVehiclesScreen, self).createToolTip(event)

    def _finalize(self):
        self.__removeListeners()
        super(NoVehiclesScreen, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(NoVehiclesScreen, self)._onLoading(*args, **kwargs)
        self.__updateData()
        self.__addListeners()

    def __addListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime

    def __removeListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.__comp7Controller.onComp7ConfigChanged, self.__onComp7ConfigChanged), (self.__comp7Controller.onStatusUpdated, self.__onStatusUpdated))

    def __onClose(self):
        self.destroyWindow()

    def __onComp7ConfigChanged(self):
        self.__updateData()

    def __onStatusUpdated(self, _):
        if self.__comp7Controller.isAvailable():
            self.__onPollServerTime()
        else:
            self.destroyWindow()

    def __updateData(self):
        with self.viewModel.transaction() as model:
            self.__onPollServerTime()
            levelsArr = model.getVehicleLevels()
            levelsArr.clear()
            for level in self.__comp7Controller.getModeSettings().levels:
                levelsArr.addNumber(level)

            levelsArr.invalidate()
            errorReason = ErrorReason.DEFAULT
            if self.__comp7Controller.vehicleIsAvailableForBuy():
                errorReason = ErrorReason.NOT_BOUGHT_VEHICLES
            elif self.__comp7Controller.vehicleIsAvailableForRestore():
                errorReason = ErrorReason.CAN_RECOVER_VEHICLES
            model.setErrorReason(errorReason)

    def __onPollServerTime(self):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setScheduleInfo(vm.scheduleInfo)


class NoVehiclesScreenWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(NoVehiclesScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=NoVehiclesScreen(layoutID=R.views.lobby.comp7.views.NoVehiclesScreen()), parent=parent, layer=WindowLayer.TOP_SUB_VIEW)
