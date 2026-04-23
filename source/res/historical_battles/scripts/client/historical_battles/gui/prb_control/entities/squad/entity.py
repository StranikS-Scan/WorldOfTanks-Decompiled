# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/entity.py
import typing
import AccountUnitAPI
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import DialogsInterface
from gui.prb_control import settings
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils.decorators import ReprInjector
from historical_battles_common.hb_constants_extension import PREBATTLE_TYPE, QUEUE_TYPE, CLIENT_UNIT_CMD, INVALID_DIVISION_ID, INVALID_FRONT_ID
from historical_battles.gui.prb_control.entities.squad.hb_vehicles_watcher import HistoricalBattlesUnitVehiclesWatcher
from historical_battles.gui.prb_control.entities.squad.scheduler import HistoricalBattleSquadScheduler
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from historical_battles.gui.prb_control.entities.squad.actions_validator import HistoricalBattleSquadActionsValidator
from historical_battles.gui.prb_control.entities.squad.actions_handler import HistoricalBattleSquadActionsHandler
from historical_battles.gui.prb_control.entities.squad.ctx import SetFrontUnitCtx, SetDivisionUnitCtx
from historical_battles.gui.shared.event_dispatcher import showHistoricalBattleQueueView
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from th_async import th_async, th_await
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from typing import Optional, Callable

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
        unitMgr.createSquadByQueueType(front.getFrontQueueType(), modeExtrasStr=self._buildModeExtraParams())

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.HISTORICAL_BATTLES, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _buildModeExtraParams(self):
        frontID = self._gameEventController.frontController.getSelectedFrontID()
        return AccountUnitAPI.dumpExtras({'frontID': frontID})


class HistoricalBattleSquadEntity(SquadEntity):
    _gameEventController = dependency.descriptor(IGameEventController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(HistoricalBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.HISTORICAL_BATTLES, PREBATTLE_TYPE.HISTORICAL_BATTLES)
        self.__isInfoDialogShown = False

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
        self.storage.queueType = self.__getSyncedQueueType()
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
        return QUEUE_TYPE.UNKNOWN if not front else front.getFrontQueueType()

    def loadHangar(self):
        showHangar()

    def showDialog(self, meta, callback, parent=None):
        if not self.__isInfoDialogShown:
            self.__showDefaultDialog(meta, callback, parent=parent)
        elif callback:
            callback(False)

    @th_async
    def __showDefaultDialog(self, meta, callback, parent=None):
        from gui.shared.event_dispatcher import showDynamicButtonInfoDialogBuilder
        key = meta.getKey()
        res = self.__resourceSplitter(key)
        if res:
            app = self.__appLoader.getApp()
            if parent is None:
                parent = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            result = yield th_await(showDynamicButtonInfoDialogBuilder(res, None, '', parent, loadCallback=self.__loadDialogCallback, destroyCallback=self.__destroyDialogCallback))
            callback(result)
        return

    def __loadDialogCallback(self):
        self.__isInfoDialogShown = True

    def __destroyDialogCallback(self):
        self.__isInfoDialogShown = False

    def __resourceSplitter(self, resourceStr):
        resourceList = resourceStr.split('/')
        if not resourceList:
            return None
        else:
            current = R.strings.dialogs.dyn(resourceList[0])
            i = 1
            while i < len(resourceList):
                current = current.dyn(resourceList[i])
                i += 1

            return current

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
            subdivision = self._gameEventController.frontController.getSelectedSubdivision()
            vehicle = subdivision.getTanksForCurrentProgressionLevel()[0]
            ctx = SetDivisionUnitCtx(vTypeCD=vehicle.intCD, divisionID=subdivision.getID(), vehInvID=vehicle.invID, waitingID='prebattle/change_settings')
            ctx.setReady = True
            self.setDivisionReady(ctx)
        else:
            ctx = SetDivisionUnitCtx(waitingID='prebattle/player_not_ready')
            ctx.setReady = False
            self.setDivisionReady(ctx)

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

    def setDivisionReady(self, ctx, callback=None):
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
            LOG_ERROR('Player can not set vehicle or division', pPermissions)
            if callback:
                callback(False)
            return
        if not pPermissions.canSetReady():
            LOG_ERROR('Player can not set ready state', pPermissions)
            if callback:
                callback(False)
            return
        if not self.isVehiclesReadyToBattle():
            LOG_DEBUG('Division is not ready to battle', ctx)
            if callback:
                callback(False)
            return
        self._setDivisionReady(ctx, callback=callback)

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

    def _setDivisionReady(self, ctx, callback=None):
        vehTypeCD = ctx.getVehTypeCD()
        divisionID = ctx.getDivisionID()
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown()):
            return
        readyStr = str(int(ctx.setReady))
        if not ctx.setReady:
            divisionID = INVALID_DIVISION_ID
            vehTypeCD = 0
        self._requestsProcessor.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_UNIT_DIVISION, divisionID, vehTypeCD, readyStr, callback=callback)
        self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())

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

    def __getSyncedQueueType(self):
        pInfo = self.getPlayerInfo()
        if pInfo.isCommander():
            front = self.gameEventController.frontController.getSelectedFront()
            return front.getFrontQueueType()
        players = self.getPlayers()
        for playerInfo in players.itervalues():
            if playerInfo.isCommander():
                enqueueData = playerInfo.extraData.get('eventEnqueueData', {})
                frontID = enqueueData.get('frontID', INVALID_FRONT_ID)
                if frontID == INVALID_FRONT_ID:
                    LOG_ERROR("Invalid players info. Couldn't get frontID")
                else:
                    self._gameEventController.updateFrontData(frontID)

        front = self._gameEventController.frontController.getSelectedFront()
        return front.getFrontQueueType()
