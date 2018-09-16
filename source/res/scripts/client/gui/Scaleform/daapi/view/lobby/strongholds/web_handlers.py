# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/web_handlers.py
from functools import partial
from adisp import process
from constants import JOIN_FAILURE, PREBATTLE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.clans.web_handlers import handleGetMembersOnline, handleGetMembersStatus, handleGetFriendsStatus, handleOpenClanCard, handleOpenClanInvites, handleOpenClanSearch
from gui.Scaleform.daapi.view.lobby.profile.web_handlers import handleOpenProfile
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleNotificationCommand, handleSoundCommand, handlerRequestGraphicsSettings, handleRequestWgniToken, getOpenHangarTabHandler, getOpenProfileTabHandler, handleShowUserContextMenu, getCloseBrowserWindowHandler, getOpenBrowserHandler, handleRequestAccessToken
from gui.SystemMessages import pushMessage, SM_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.stronghold.unit.ctx import CreateUnitCtx, JoinUnitCtx
from gui.prb_control.formatters import messages
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import actions
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
from web_client_api.commands import createNotificationHandler, createSoundHandler, createOpenWindowHandler, createCloseWindowHandler, createOpenTabHandler, createStrongholdsBattleHandler, createRequestHandler, createContextMenuHandler, createClanManagementHandler

def createStrongholdsWebHandlers(includeCloseBrowser=False, onBrowserOpen=None, onBrowserClose=None):
    handlers = [createNotificationHandler(handleNotificationCommand),
     createSoundHandler(handleSoundCommand),
     createOpenWindowHandler(profileHandler=handleOpenProfile, clanCardHandler=handleOpenClanCard, clanInvitesHandler=handleOpenClanInvites, clanSearchHandler=handleOpenClanSearch, browserHandler=getOpenBrowserHandler(onBrowserOpen, partial(createStrongholdsWebHandlers, True))),
     createOpenTabHandler(hangarHandler=getOpenHangarTabHandler(), profileHandler=getOpenProfileTabHandler()),
     createStrongholdsBattleHandler(openListHandler=handleOpenList, battleChosenHandler=handleBattleChosen, joinBattleHandler=handleJoinBattle),
     createRequestHandler(token1Handler=handleRequestWgniToken, graphicsSettingsHandler=handlerRequestGraphicsSettings, accessTokenHandler=handleRequestAccessToken),
     createContextMenuHandler(handleShowUserContextMenu),
     createClanManagementHandler(membersOnlineHandler=handleGetMembersOnline, membersStatusHandler=handleGetMembersStatus, friendsStatusHandler=handleGetFriendsStatus)]
    if includeCloseBrowser:
        handlers.append(createCloseWindowHandler(getCloseBrowserWindowHandler(onBrowserClose)))
    return handlers


def handleOpenList(command, ctx):
    _doSelect(g_prbLoader.getDispatcher())


@process
def _doSelect(dispatcher):
    yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST))


def handleBattleChosen(command, ctx):
    _doBattleChosen(g_prbLoader.getDispatcher())


@process
def _doBattleChosen(dispatcher):

    def onTimeout():
        pushMessage(messages.getJoinFailureMessage(JOIN_FAILURE.TIME_OUT), type=SM_TYPE.Error)
        dispatcher.restorePrevious()

    yield dispatcher.create(CreateUnitCtx(PREBATTLE_TYPE.EXTERNAL, waitingID='prebattle/create', onTimeoutCallback=onTimeout))


@process
def handleJoinBattle(command, ctx):

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

        _doJoinBattle(dispatcher, command.unit_id, onError)

    connectionMgr = dependency.instance(IConnectionManager)
    if connectionMgr.peripheryID != command.periphery_id:
        success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            reloginCtrl = dependency.instance(IReloginController)
            reloginCtrl.doRelogin(command.periphery_id, extraChainSteps=(actions.OnLobbyInitedAction(onInited=partial(doJoin, False)),))
    else:
        doJoin(True)


@process
def _doJoinBattle(dispatcher, unitMgrId, onErrorCallback):
    yield dispatcher.join(JoinUnitCtx(unitMgrId, PREBATTLE_TYPE.EXTERNAL, onErrorCallback=onErrorCallback, waitingID='prebattle/join'))
