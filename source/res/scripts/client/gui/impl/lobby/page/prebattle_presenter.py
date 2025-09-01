# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/prebattle_presenter.py
from __future__ import absolute_import
import logging
import constants
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ACTIVE_TEST_PARTICIPATION_CONFIRMED
from adisp import adisp_process, adisp_async
from gui.impl.gen.view_models.views.lobby.page.header.prebattle_model import PrebattleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG, convertFlagsToNames, REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showActiveTestConfirmDialog
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_async, wg_await
_logger = logging.getLogger(__name__)
_FUNCTIONAL_FLAGS_MODES = FUNCTIONAL_FLAG.EPIC | FUNCTIONAL_FLAG.BATTLE_ROYALE | FUNCTIONAL_FLAG.MAPBOX | FUNCTIONAL_FLAG.MAPS_TRAINING

class PrebattlePresenter(ViewComponent[PrebattleModel], IGlobalListener, CallbackDelayer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(PrebattlePresenter, self).__init__(model=PrebattleModel)
        self.__battleVehicleInvId = 0
        self.__arenaCreated = False
        self.__enabled = True

    @property
    def viewModel(self):
        return super(PrebattlePresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self._onAction),
         (self.__platoonCtrl.onMembersUpdate, self._onPlatoonMembersUpdate),
         (g_currentVehicle.onChanged, self._onPrebattleUpdate),
         (g_currentPreviewVehicle.onChanged, self._onPrebattleUpdate),
         (g_playerEvents.onArenaCreated, self._onArenaCreated))

    def _onLoading(self, *args, **kwargs):
        super(PrebattlePresenter, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self._onPrebattleUpdate()

    def _finalize(self):
        self.stopGlobalListening()
        super(PrebattlePresenter, self)._finalize()

    def _getListeners(self):
        return ((events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onPrebattleUpdateEventHandler, EVENT_BUS_SCOPE.LOBBY),
         (events.LobbyHeaderControlsEvent.DISABLE, self.__onControlsDisable, EVENT_BUS_SCOPE.LOBBY),
         (events.LobbyHeaderControlsEvent.ENABLE, self.__onControlsEnable, EVENT_BUS_SCOPE.LOBBY),
         (events.CoolDownEvent.PREBATTLE, self.__onSetPrebattleCoolDown, EVENT_BUS_SCOPE.LOBBY))

    def onPrbEntitySwitched(self):
        self._onPrebattleUpdate()

    def onEnqueued(self, *args, **kwargs):
        self.__setVehicleInfo()
        self._onPrebattleUpdate()

    def onDequeued(self, *args, **kwargs):
        self.__battleVehicleInvId = 0
        self._onPrebattleUpdate()

    def onEnqueueError(self, *args, **kwargs):
        self.__arenaCreated = False
        self._onPrebattleUpdate()

    def onArenaJoinFailure(self, *args, **kwargs):
        self.__arenaCreated = False
        self._onPrebattleUpdate()

    def onKickedFromQueue(self, *args, **kwargs):
        self.__arenaCreated = False
        self._onPrebattleUpdate()

    def onKickedFromArena(self, *args, **kwargs):
        self.__arenaCreated = False
        self._onPrebattleUpdate()

    def _onAction(self, event):
        actionType = event.get('action')
        if actionType in (PrebattleModel.BATTLE_START_ACTION_TYPE, PrebattleModel.BATTLE_READY_ACTION_TYPE):
            self.__startBattleHandler()
        elif actionType == PrebattleModel.BATTLE_EXIT_ACTION_TYPE:
            if self.prbEntity.isInQueue():
                self.prbEntity.exitFromQueue()
            else:
                _logger.error('Can not exit queue')

    @adisp_process
    def __startBattleHandler(self):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield self.__lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if self.prbDispatcher:
                prbEntity = self.prbDispatcher.getEntity()
                result = yield self.__platoonCtrl.processPlatoonActions(0, prbEntity, g_currentVehicle)
                if not result:
                    activeTestOk = yield self.__processMMActiveTestConfirm(prbEntity)
                    if activeTestOk:
                        self.prbDispatcher.doAction(PrbAction('', 0))
            else:
                _logger.error('Prebattle dispatcher is not defined')

    def _onPlatoonMembersUpdate(self):
        self.__setVehicleInfo()
        self._onPrebattleUpdate()

    def _onArenaCreated(self):
        self.__arenaCreated = True
        self._onPrebattleUpdate()

    @adisp_async
    @wg_async
    def __processMMActiveTestConfirm(self, prbEntity, callback):
        config = self.__lobbyContext.getServerSettings().getActiveTestConfirmationConfig()
        toShow = bool(not AccountSettings.getSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED) and config.get('enabled') and prbEntity.getQueueType() == constants.QUEUE_TYPE.RANDOMS and g_currentVehicle.item.level == 10)
        if not self.__connectionMgr.isStandalone():
            toShow = toShow and self.__connectionMgr.peripheryID in config.get('peripheryIDs', ())
        if toShow:
            result = yield wg_await(showActiveTestConfirmDialog(config.get('startTime', 0.0), config.get('finishTime', 0.0), config.get('link', '')))
            if result:
                AccountSettings.setSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED, True)
            callback(result)
        callback(True)

    def __onSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.__setStates()
            self.delayCallback(event.coolDown, self.__setStates)

    def __onPrebattleUpdateEventHandler(self, _):
        self._onPrebattleUpdate()

    def __setVehicleInfo(self):
        vehicleItem = g_currentVehicle.item
        if vehicleItem:
            self.__battleVehicleInvId = vehicleItem.invID
            fillVehicleModel(self.viewModel.battleVehicle, vehicleItem)
        else:
            self.__battleVehicleInvId = 0

    def _onPrebattleUpdate(self):
        entity = self.prbEntity
        flags = entity.getFunctionalFlags() & (FUNCTIONAL_FLAG.MODES_BITMASK | _FUNCTIONAL_FLAGS_MODES)
        self.viewModel.setQueueType(constants.QUEUE_TYPE_NAMES[entity.getQueueType()])
        if flags != FUNCTIONAL_FLAG.UNDEFINED:
            self.viewModel.setCurrentMode(convertFlagsToNames(flags)[0])
        status = self.__getBattleStatus()
        self.viewModel.setBattleStatus(status)
        self.__setStates()

    def __getBattleStatus(self):
        if self.__arenaCreated:
            return PrebattleModel.BATTLE_STATE_READY
        if self.prbEntity.isInQueue() and (not self.__platoonCtrl.isInPlatoon() or self.prbEntity.isCommander() or self.prbEntity.getPlayerInfo().isReady):
            return PrebattleModel.BATTLE_STATE_SEARCHING
        return PrebattleModel.BATTLE_STATE_IDLE

    def __setStates(self):
        if not self.prbEntity or not self.prbDispatcher:
            return
        prbDispatcher = self.prbDispatcher
        pValidation = self.prbEntity.canPlayerDoAction()
        pFuncState = prbDispatcher.getFunctionalState()
        pInfo = prbDispatcher.getPlayerInfo()
        inCooldown = pFuncState.isReadyActionSupported() and not pInfo.isCreator and self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.SET_PLAYER_STATE)
        trueStates = {self.viewModel.ACTION_ENABLED: pValidation.isValid and self.__enabled and not inCooldown,
         self.viewModel.PLAYER_CREATOR: pInfo.isCreator,
         self.viewModel.PLAYER_READY: pInfo.isReady,
         self.viewModel.READINESS_AVAILABLE: pFuncState.isReadyActionSupported()}
        self.viewModel.getStates().update(trueStates)

    def __onControlsDisable(self):
        self.__enabled = False
        self._onPrebattleUpdate()

    def __onControlsEnable(self):
        self.__enabled = True
        self._onPrebattleUpdate()
