# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/no_vehicles_screen.py
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.no_vehicles_screen_model import ErrorReason, NoVehiclesScreenModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class NoVehiclesScreen(ViewImpl, IGlobalListener):
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
            if tooltipId == COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(NoVehiclesScreen, self).createToolTip(event)

    def onPrbEntitySwitched(self):
        if not self.__comp7Controller.isComp7PrbActive():
            self.destroyWindow()

    def _finalize(self):
        self.__removeListeners()
        super(NoVehiclesScreen, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(NoVehiclesScreen, self)._onLoading(*args, **kwargs)
        self.__updateData()
        self.__addListeners()

    def __addListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime
        self.startGlobalListening()
        g_eventBus.addListener(events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, scope=EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime
        self.stopGlobalListening()
        g_eventBus.removeListener(events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, scope=EVENT_BUS_SCOPE.LOBBY)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.__comp7Controller.onComp7ConfigChanged, self.__onComp7ConfigChanged), (self.__comp7Controller.onStatusUpdated, self.__onStatusUpdated))

    def __onClose(self):
        showHangar()

    def __onComp7ConfigChanged(self):
        self.__updateData()

    def __onStatusUpdated(self, status):
        if comp7_model_helpers.isModeForcedDisabled(status):
            showHangar()
        else:
            self.__onPollServerTime()

    def __onHeaderMenuClick(self, *_):
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
