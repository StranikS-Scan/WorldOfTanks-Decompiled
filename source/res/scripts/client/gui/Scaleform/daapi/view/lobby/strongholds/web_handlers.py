# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/web_handlers.py
from functools import partial
from adisp import process
from constants import JOIN_FAILURE, PREBATTLE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.clans.web_handlers import handleClanManagementCommand, OPEN_WINDOW_CLAN_SUB_COMMANDS
from gui.Scaleform.daapi.view.lobby.profile.web_handlers import OPEN_WINDOW_PROFILE_SUB_COMMANS
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleNotificationCommand, handleSoundCommand, handleOpenTabCommand, handleRequestCommand, handleContextMenuCommand, createOpenWindowCommandHandler, handleCloseWindowCommand
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createOpenBrowserSubCommands
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
from web_client_api import WebCommandException
from web_client_api.commands import createNotificationHandler, createSoundHandler, createOpenWindowHandler, createCloseWindowHandler, createOpenTabHandler, createStrongholdsBattleHandler, createRequestHandler, createContextMenuHandler, createClanManagementHandler, instantiateObject
from web_client_api.commands.strongholds import StrongholdsJoinBattleCommand

def createStrongholdsWebHandlers(includeCloseBrowser=False, onBrowserOpen=None, onBrowserClose=None):
    """
    Creates list of stronghold specific web handlers
    :param includeCloseBrowser: - whether 'close_browser' handler to be included
    :return: - list oh handlers
    """
    openWindowSubCommands = {}
    openWindowSubCommands.update(OPEN_WINDOW_CLAN_SUB_COMMANDS)
    openWindowSubCommands.update(OPEN_WINDOW_PROFILE_SUB_COMMANS)
    openWindowSubCommands.update(createOpenBrowserSubCommands(onBrowserOpen, partial(createStrongholdsWebHandlers, True)))
    handlers = [createNotificationHandler(handleNotificationCommand),
     createSoundHandler(handleSoundCommand),
     createOpenWindowHandler(createOpenWindowCommandHandler(openWindowSubCommands)),
     createOpenTabHandler(handleOpenTabCommand),
     createStrongholdsBattleHandler(handleStrongholdsBattleCommand),
     createRequestHandler(handleRequestCommand),
     createContextMenuHandler(handleContextMenuCommand),
     createClanManagementHandler(handleClanManagementCommand)]
    if includeCloseBrowser:
        handlers.append(createCloseWindowHandler(partial(handleCloseWindowCommand, onBrowserClose)))
    return handlers


def handleStrongholdsBattleCommand(command, ctx):
    """
    Executes battle specific actions
    """
    if command.action in STRONGHOLD_BATTLE_ACTIONS:
        subCommand, handler = STRONGHOLD_BATTLE_ACTIONS[command.action]
        if subCommand:
            subCommandInstance = instantiateObject(subCommand, command.custom_parameters)
            handler(subCommandInstance)
        else:
            handler()
    else:
        raise WebCommandException('Unknown strongholds battle action: %s!' % command.action)


def _openList():
    """
    Opens list of battles
    """
    _doSelect(g_prbLoader.getDispatcher())


@process
def _doSelect(dispatcher):
    yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST))


def _battleChosen():
    """
    Notifies client that battle was chosen on web and client should wait for join
    """
    _doBattleChosen(g_prbLoader.getDispatcher())


@process
def _doBattleChosen(dispatcher):

    def onTimeout():
        pushMessage(messages.getJoinFailureMessage(JOIN_FAILURE.TIME_OUT), type=SM_TYPE.Error)
        dispatcher.restorePrevious()

    yield dispatcher.create(CreateUnitCtx(PREBATTLE_TYPE.EXTERNAL, waitingID='prebattle/create', onTimeoutCallback=onTimeout))


@process
def _joinBattle(command):

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


STRONGHOLD_BATTLE_ACTIONS = {'open_list': (None, _openList),
 'battle_chosen': (None, _battleChosen),
 'join_battle': (StrongholdsJoinBattleCommand, _joinBattle)}
