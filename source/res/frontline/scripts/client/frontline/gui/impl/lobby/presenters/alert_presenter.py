# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/alert_presenter.py
from frontline.gui.impl.gen.view_models.views.lobby.components.alert_message_model import AlertMessageModel
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showEpicBattlesPrimeTimeWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache

class AlertButtonAction(object):
    CHANGE_SERVER = 'change_Server'


class AlertPresenter(ViewComponent[AlertMessageModel]):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(AlertPresenter, self).__init__(model=AlertMessageModel)
        self._buttonType = ''

    @property
    def viewModel(self):
        return super(AlertPresenter, self).getViewModel()

    def _getEvents(self):
        baseEvents = super(AlertPresenter, self)._getEvents()
        return baseEvents + ((self.viewModel.onClick, self.__onClick),
         (g_currentVehicle.onChanged, self._updateModel),
         (g_currentPreviewVehicle.onChanged, self._updateModel),
         (self.__itemsCache.onSyncCompleted, self.__onInventoryUpdate),
         (self.__epicController.onPrimeTimeStatusUpdated, self._onPrimeTimeStatusUpdated))

    def _getListeners(self):
        return ((events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdateEventHandler, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        super(AlertPresenter, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as vm:
            additionalCriteria = ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
            if not self.__epicController.isCurrentCycleActive():
                vm.setMessage(backport.text(R.strings.fl_hangar.alert.modeEnded()))
            elif not self.__epicController.hasAvailablePrimeTimeServers():
                vm.setMessage(backport.text(R.strings.fl_hangar.alert.allServersAreUnavailable()))
            elif not self.__epicController.isInPrimeTime():
                vm.setMessage(backport.text(R.strings.fl_hangar.alert.serverIsUnavailable()))
                vm.setButtonLabel(backport.text(R.strings.fl_hangar.alert.changeServer()))
                self._buttonType = AlertButtonAction.CHANGE_SERVER
            elif not self.__epicController.hasSuitableVehicles(additionalCriteria):
                vm.setMessage(backport.text(R.strings.fl_hangar.alert.noAvailableVehicles()))
            elif not self.__epicController.isCurVehicleSuitable(additionalCriteria):
                vm.setMessage(backport.text(R.strings.fl_hangar.alert.incompatibleVehicle()))
            else:
                vm.setMessage('')

    def _onPrimeTimeStatusUpdated(self, *_):
        self._updateModel()

    def __onInventoryUpdate(self, _, diff):
        if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
            self._updateModel()
        return

    def __onClick(self):
        if self._buttonType == AlertButtonAction.CHANGE_SERVER:
            showEpicBattlesPrimeTimeWindow()

    def __onFightButtonUpdateEventHandler(self, _):
        self._updateModel()
