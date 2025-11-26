# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/alert_message_presenter.py
import json
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from battle_royale.gui.constants import BattleRoyaleModeState
from battle_royale.gui.impl.gen.view_models.views.lobby.views.alert_message_model import AlertMessageModel, AlertType
from battle_royale.gui.shared.event_dispatcher import showBattleRoyalePrimeTime
_BATTLE_ROYALE_MODE_STATE_TO_ALERT_TYPE = {BattleRoyaleModeState.CeasefireCurrentServer: AlertType.CEASEFIRECURRENTSERVER,
 BattleRoyaleModeState.CeasefireAllServers: AlertType.CEASEFIREALLSERVERS,
 BattleRoyaleModeState.Finished: AlertType.MODEISFINISHED,
 BattleRoyaleModeState.Unavailable: AlertType.MODEISUNAVAILABLE,
 BattleRoyaleModeState.Regular: AlertType.NONE}

class AlertMessagePresenter(ViewComponent[AlertMessageModel], IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(AlertMessagePresenter, self).__init__(model=AlertMessageModel)

    @property
    def viewModel(self):
        return super(AlertMessagePresenter, self).getViewModel()

    def _getEvents(self):
        return super(AlertMessagePresenter, self)._getEvents() + ((self.viewModel.onChangeServer, self.__onChangeServer), (self.__battleRoyaleController.onWidgetUpdate, self.__update), (self.__battleRoyaleController.onPrimeTimeStatusUpdated, self.__update))

    def onPrbEntitySwitched(self):
        self.__update()

    def _onLoading(self, *args, **kwargs):
        super(AlertMessagePresenter, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self.__update()

    def _finalize(self):
        self.stopGlobalListening()
        return super(AlertMessagePresenter, self)._finalize()

    def __update(self, *_):
        with self.viewModel.transaction() as model:
            modeState = self.__battleRoyaleController.getModeState()
            model.setAlertType(_BATTLE_ROYALE_MODE_STATE_TO_ALERT_TYPE.get(modeState, AlertType.NONE))
            self.__updateBattleSchedule(model)

    def __updateBattleSchedule(self, model):
        battleScheduleModel = model.getBattleSchedule()
        currentSeason = self.__battleRoyaleController.getCurrentSeason()
        if currentSeason is None:
            return
        else:
            primeTimes = self.__battleRoyaleController.getPrimeTimes()
            currentCycleEnd = currentSeason.getCycleEndDate()
            todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
            todayEnd += 1
            for peripheryID, primeTime in primeTimes.items():
                todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, currentCycleEnd))
                peripheryName = self.__lobbyContext.getPeripheryName(peripheryID, checkAnother=False, useShortName=True)
                if peripheryName is not None:
                    battleScheduleModel.set(peripheryName, json.dumps(todayPeriods))

            return

    @staticmethod
    def __onChangeServer():
        showBattleRoyalePrimeTime()
