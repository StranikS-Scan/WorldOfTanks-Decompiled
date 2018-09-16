# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/strongholds/__init__.py
from functools import partial
from adisp import process
from constants import JOIN_FAILURE, PREBATTLE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import dependency
from gui import DialogsInterface
from gui.SystemMessages import pushMessage, SM_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.stronghold.unit.ctx import CreateUnitCtx, JoinUnitCtx
from gui.prb_control.formatters import messages
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import actions
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
from web_client_api import w2capi, w2c, W2CSchema, Field

class _StrongholdsJoinBattleSchema(W2CSchema):
    unit_id = Field(required=True, type=(int, long))
    periphery_id = Field(required=True, type=(int, long))


@w2capi(name='strongholds_battle', key='action')
class StrongholdsWebApi(object):

    @w2c(W2CSchema, 'open_list')
    @process
    def handleOpenList(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST))

    @w2c(W2CSchema, 'battle_chosen')
    @process
    def handleBattleChosen(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()

        def onTimeout():
            pushMessage(messages.getJoinFailureMessage(JOIN_FAILURE.TIME_OUT), type=SM_TYPE.Error)
            dispatcher.restorePrevious()

        yield dispatcher.create(CreateUnitCtx(PREBATTLE_TYPE.EXTERNAL, waitingID='prebattle/create', onTimeoutCallback=onTimeout))

    @w2c(_StrongholdsJoinBattleSchema, 'join_battle')
    @process
    def handleJoinBattle(self, cmd):

        @process
        def joinBattle(dispatcher, unitMgrId, onErrorCallback):
            yield dispatcher.join(JoinUnitCtx(unitMgrId, PREBATTLE_TYPE.EXTERNAL, onErrorCallback=onErrorCallback, waitingID='prebattle/join'))

        def doJoin(restoreOnError):
            dispatcher = g_prbLoader.getDispatcher()

            @process
            def onError(errorData):
                if restoreOnError:
                    dispatcher.restorePrevious()
                else:
                    yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST))
                try:
                    message = errorData['extra_data']['title']
                    pushMessage(message, type=SM_TYPE.Error)
                except (KeyError, TypeError):
                    LOG_CURRENT_EXCEPTION()

            joinBattle(dispatcher, cmd.unit_id, onError)

        connectionMgr = dependency.instance(IConnectionManager)
        if connectionMgr.peripheryID != cmd.periphery_id:
            success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
            if success:
                reloginCtrl = dependency.instance(IReloginController)
                reloginCtrl.doRelogin(cmd.periphery_id, extraChainSteps=(actions.OnLobbyInitedAction(onInited=partial(doJoin, False)),))
        else:
            doJoin(True)
