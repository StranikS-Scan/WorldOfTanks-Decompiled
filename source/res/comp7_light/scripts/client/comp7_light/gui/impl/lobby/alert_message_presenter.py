# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/alert_message_presenter.py
from __future__ import absolute_import
from comp7_light.gui.impl.gen.view_models.views.lobby.alert_message_model import AlertMessageModel, State
from comp7_light.gui.shared import event_dispatcher
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class AlertMessagePresenter(ViewComponent[AlertMessageModel]):
    __comp7LightController = dependency.descriptor(IComp7LightController)

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
         (self.__comp7LightController.onStatusUpdated, self.__updateAlertData),
         (self.__comp7LightController.onStatusTick, self.__updateAlertData),
         (self.__comp7LightController.onModeConfigChanged, self.__updateAlertData))

    def __onClick(self):
        state = self.__getAlertState()
        if state == State.NOVEHICLES:
            event_dispatcher.showComp7LightNoVehiclesScreen()
        elif state == State.CEASEFIREAVAILABLE:
            event_dispatcher.showComp7LightPrimeTimeWindow()

    def __getAlertState(self):
        if not self.__comp7LightController.hasSuitableVehicles():
            return State.NOVEHICLES
        if not self.__comp7LightController.isInPrimeTime() and self.__comp7LightController.hasAvailablePrimeTimeServers():
            return State.CEASEFIREAVAILABLE
        if not self.__comp7LightController.isInPrimeTime():
            return State.CEASEFIREUNAVAILABLE
        return State.MODEOFFLINE if self.__comp7LightController.isOffline else State.NONE

    def __updateAlertData(self, _=None):
        with self.viewModel.transaction() as model:
            model.setState(self.__getAlertState())
