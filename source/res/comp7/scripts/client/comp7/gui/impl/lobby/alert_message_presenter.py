# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/alert_message_presenter.py
from __future__ import absolute_import
from comp7.gui.impl.gen.view_models.views.lobby.alert_message_model import AlertMessageModel, State
from comp7.gui.shared import event_dispatcher as comp7_events
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.pub.view_component import ViewComponent
from gui.periodic_battles.models import PeriodType
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class AlertMessagePresenter(ViewComponent[AlertMessageModel]):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(AlertMessagePresenter, self).__init__(model=AlertMessageModel)

    def _onLoading(self, *args, **kwargs):
        super(AlertMessagePresenter, self)._onLoading(*args, **kwargs)
        self.__updateAlertData()

    @property
    def viewModel(self):
        return super(AlertMessagePresenter, self).getViewModel()

    def _getCallbacks(self):
        return (('inventory.1.compDescr', self.__updateAlertData),)

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick),
         (self.__comp7Controller.onBanUpdated, self.__updateAlertData),
         (self.__comp7Controller.onQualificationStateUpdated, self.__updateAlertData),
         (self.__comp7Controller.onStatusUpdated, self.__updateAlertData),
         (self.__comp7Controller.onStatusTick, self.__updateAlertData),
         (self.__comp7Controller.onModeConfigChanged, self.__updateAlertData),
         (self.__comp7Controller.onOfflineStatusUpdated, self.__updateAlertData))

    def __onClick(self):
        state = self.__getAlertState()
        if state == State.NOVEHICLES:
            comp7_events.showComp7NoVehiclesScreen()
        elif state == State.CEASEFIREAVAILABLE:
            comp7_events.showComp7PrimeTimeWindow()

    def __getAlertState(self):
        periodInfo = self.__comp7Controller.getPeriodInfo()
        if self.__comp7Controller.isBanned:
            return State.BAN
        if not self.__comp7Controller.hasSuitableVehicles():
            return State.NOVEHICLES
        if self.__comp7Controller.isInPreannounceState():
            return State.PREANNOUNCE
        if periodInfo.periodType in (PeriodType.AFTER_SEASON,
         PeriodType.AFTER_CYCLE,
         PeriodType.BETWEEN_SEASONS,
         PeriodType.ALL_NOT_AVAILABLE_END,
         PeriodType.NOT_AVAILABLE_END,
         PeriodType.STANDALONE_NOT_AVAILABLE_END):
            return State.SEASONEND
        if self.__comp7Controller.isQualificationResultsProcessing():
            return State.QUALIFICATION
        if not self.__comp7Controller.isInPrimeTime() and self.__comp7Controller.hasAvailablePrimeTimeServers():
            return State.CEASEFIREAVAILABLE
        if not self.__comp7Controller.isInPrimeTime():
            return State.CEASEFIREUNAVAILABLE
        return State.MODEOFFLINE if self.__comp7Controller.isOffline else State.NONE

    def __updateAlertData(self, _=None):
        preannouncedSeason = self.__comp7Controller.getPreannouncedSeason()
        with self.viewModel.transaction() as model:
            model.setState(self.__getAlertState())
            model.setBanTimeleftInSeconds(int(round(self.__comp7Controller.banDuration)))
            fillIntsArray(self.__comp7Controller.getModeSettings().levels, model.getLevels())
            if preannouncedSeason is not None:
                model.setStartEventTimestamp(preannouncedSeason.getStartDate())
        return
