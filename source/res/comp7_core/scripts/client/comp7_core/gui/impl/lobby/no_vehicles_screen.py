# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/no_vehicles_screen.py
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showHangar

class NoVehiclesScreen(ViewImpl, IGlobalListener):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = self._modelClazz()
        super(NoVehiclesScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NoVehiclesScreen, self).getViewModel()

    @property
    def _modeController(self):
        raise NotImplementedError

    @property
    def _modelClazz(self):
        raise NotImplementedError

    @property
    def _seasonStateClazz(self):
        raise NotImplementedError

    @property
    def _yearStateClazz(self):
        raise NotImplementedError

    @property
    def _errorReasonClazz(self):
        raise NotImplementedError

    @property
    def _seasonNameClazz(self):
        raise NotImplementedError

    @property
    def _calendarDayTooltipID(self):
        raise NotImplementedError

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == self._calendarDayTooltipID:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(NoVehiclesScreen, self).createToolTip(event)

    def onPrbEntitySwitched(self):
        if not self._modeController.isModePrbActive():
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
        return ((self.viewModel.onClose, self.__onClose), (self._modeController.onModeConfigChanged, self.__onModeConfigChanged), (self._modeController.onStatusUpdated, self.__onStatusUpdated))

    def __onClose(self):
        showHangar()

    def __onModeConfigChanged(self):
        self.__updateData()

    def __onStatusUpdated(self, status):
        if comp7_core_model_helpers.isModeForcedDisabled(status, self._modeController):
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
            for level in self._modeController.getModeSettings().levels:
                levelsArr.addNumber(level)

            levelsArr.invalidate()
            if self._modeController.vehicleIsAvailableForRestore():
                errorReason = self._errorReasonClazz.CAN_RECOVER_VEHICLES
            elif self._modeController.vehicleIsAvailableForBuy():
                errorReason = self._errorReasonClazz.NOT_BOUGHT_VEHICLES
            else:
                errorReason = self._errorReasonClazz.DEFAULT
            model.setErrorReason(errorReason)

    def __onPollServerTime(self):
        with self.viewModel.transaction() as vm:
            comp7_core_model_helpers.setScheduleInfo(vm.scheduleInfo, self._modeController, self._calendarDayTooltipID, self._seasonStateClazz, self._yearStateClazz, self._seasonNameClazz)
