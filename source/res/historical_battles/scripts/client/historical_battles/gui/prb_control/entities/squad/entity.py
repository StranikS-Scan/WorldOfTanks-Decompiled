# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/entity.py
import cPickle
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import DialogsInterface
from gui.prb_control import settings
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.shared.utils.decorators import ReprInjector
from historical_battles_common.hb_constants_extension import PREBATTLE_TYPE, QUEUE_TYPE, CLIENT_UNIT_CMD
from historical_battles.gui.prb_control.entities.squad.hb_vehicles_watcher import HistoricalBattlesUnitVehiclesWatcher
from historical_battles.gui.prb_control.entities.squad.scheduler import HistoricalBattleSquadScheduler
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from historical_battles.gui.prb_control.entities.squad.actions_validator import HistoricalBattleSquadActionsValidator
from historical_battles.gui.prb_control.entities.squad.actions_handler import HistoricalBattleSquadActionsHandler
from historical_battles.gui.prb_control.entities.squad.ctx import SetFrontmanUnitCtx, SetFrontUnitCtx
from historical_battles.gui.shared.event_dispatcher import showHBHangar, showHistoricalBattleQueueView
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

@ReprInjector.withParent()
class HistoricalSquadSettingsCtx(SquadSettingsCtx):

    def __init__(self, waitingID='', accountsToInvite=None):
        super(HistoricalSquadSettingsCtx, self).__init__(PREBATTLE_TYPE.HISTORICAL_BATTLES, waitingID, FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite, False)


class HistoricalBattleSquadEntryPoint(SquadEntryPoint):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, accountsToInvite=None):
        super(HistoricalBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.HISTORICAL_BATTLES, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        front = self._gameEventController.frontController.getSelectedFront()
        unitMgr.createSquadByQueueType(front.getFrontQueueType(), self._buildModeExtraParams())

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.HISTORICAL_BATTLES, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _buildModeExtraParams(self):
        frontID = self._gameEventController.frontController.getSelectedFrontID()
        return cPickle.dumps({'frontID': frontID}, -1)


class HistoricalBattleSquadEntity(SquadEntity):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(HistoricalBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.HISTORICAL_BATTLES, PREBATTLE_TYPE.HISTORICAL_BATTLES)

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    @property
    def needsCheckVehicleForBattle(self):
        return False

    @property
    def gameEventController(self):
        return self._gameEventController

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        self._gameEventController.onSelectedFrontChanged += self.onSelectedFrontChanged
        if self.getPlayerInfo().isReady and self.getFlags().isInQueue():
            showHistoricalBattleQueueView()
        else:
            self.loadHangar()
        return super(HistoricalBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        self._gameEventController.onSelectedFrontChanged -= self.onSelectedFrontChanged
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        super(HistoricalBattleSquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        super(HistoricalBattleSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        front = self.gameEventController.frontController.getSelectedFront()
        return front.getFrontQueueType()

    def loadHangar(self):
        showHBHangar()

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES_SQUAD, PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(HistoricalBattleSquadEntity, self).doSelectAction(action)

    def canPlayerDoAction(self):
        return self._actionsValidator.canPlayerDoAction() or ValidationResult()

    def togglePlayerReadyAction(self, launchChain=False):
        notReady = not self.getPlayerInfo().isReady
        if notReady:
            frontman = self._gameEventController.frontController.getSelectedFrontman()
            ctx = SetFrontmanUnitCtx(vTypeCD=frontman.getSelectedVehicle().intCD, frontmanID=frontman.getID(), vehInvID=frontman.getSelectedVehicle().invID, waitingID='prebattle/change_settings')
            ctx.setReady = True
            self.setFrontmanReady(ctx)
        else:
            ctx = SetFrontmanUnitCtx(waitingID='prebattle/player_not_ready')
            ctx.setReady = False
            self.setFrontmanReady(ctx)

    def onSelectedFrontChanged(self):
        front = self._gameEventController.frontController.getSelectedFront()
        pInfo = self.getPlayerInfo()
        if not pInfo.isCommander():
            return
        ctx = SetFrontUnitCtx(front.getID(), waitingID='prebattle/change_settings')
        self._setFront(ctx)

    def getConfirmDialogMeta(self, ctx):
        if not self._gameEventController.isEnabled():
            self.__showDialog(ctx)
            return None
        else:
            return super(HistoricalBattleSquadEntity, self).getConfirmDialogMeta(ctx)

    def setVehicle(self, *args, **kwargs):
        pass

    def setFrontmanReady(self, ctx, callback=None):
        pInfo = self.getPlayerInfo()
        if not pInfo.isInSlot:
            LOG_ERROR('Player is not in slot', ctx)
            if callback:
                callback(False)
            return
        if pInfo.isReady is ctx.setReady:
            LOG_DEBUG('Player already ready', ctx)
            if callback:
                callback(True)
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canSetVehicle():
            LOG_ERROR('Player can not set vehicle or frontman', pPermissions)
            if callback:
                callback(False)
            return
        if not pPermissions.canSetReady():
            LOG_ERROR('Player can not set ready state', pPermissions)
            if callback:
                callback(False)
            return
        if not self.isVehiclesReadyToBattle():
            LOG_DEBUG('Frontman are not ready to battle', ctx)
            if callback:
                callback(False)
            return
        self._setFrontmanReady(ctx, callback=callback)

    def _doStartBattleRequest(self, ctx, flags, callback):
        self._requestsProcessor.doRequest(ctx, 'startBattle', startBattleUnitCmd=CLIENT_UNIT_CMD.START_UNIT_HISTORICAL_BATTLES, vehInvID=ctx.selectVehInvID, gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=ctx.getDemoArenaTypeID(), callback=callback, stopAutoSearch=flags.isInSearch())

    def setPlayerReady(self, ctx, callback=None):
        pass

    def setVehicleList(self, *args, **kwargs):
        pass

    def resetPlayerState(self):
        pass

    def _setVehicle(self, *args, **kwargs):
        pass

    def _setFrontmanReady(self, ctx, callback=None):
        vehTypeCD = ctx.getVehTypeCD()
        frontmanID = ctx.getFrontmanID()
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown()):
            return
        readyStr = str(int(ctx.setReady))
        if ctx.setReady:
            self._requestsProcessor.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_UNIT_FRONTMAN, frontmanID, vehTypeCD, readyStr, callback=callback)
            self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())
        else:
            self._requestsProcessor.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_UNIT_FRONTMAN, 0, 0, readyStr, callback=callback)
            self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())

    def _setReady(self, *args, **kwargs):
        pass

    def _setFront(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change front', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_UNIT_FRONT, ctx.getFrontID(), 0, '', callback=callback)
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_SETTINGS, coolDown=ctx.getCooldown())

    def _createActionsValidator(self):
        return HistoricalBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return HistoricalBattleSquadActionsHandler(self)

    def _createVehicelsWatcher(self):
        return HistoricalBattlesUnitVehiclesWatcher(self)

    def _createScheduler(self):
        return HistoricalBattleSquadScheduler(self)

    def __showDialog(self, ctx):
        DialogsInterface.showDialog(rally_dialog_meta.createLeaveInfoMeta(ctx, 'eventDisabled'), lambda _: None)
