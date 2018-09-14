# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/web_handlers.py
import time
from adisp import process
from constants import PREBATTLE_TYPE, TOKEN_TYPE, JOIN_FAILURE
from helpers import dependency
from ConnectionManager import connectionManager
from debug_utils import LOG_CURRENT_EXCEPTION
from functools import partial
from web_client_api import WebCommandException
from web_client_api.commands.window_navigator import OpenClanCardCommand, OpenProfileCommand, OpenBrowserCommand, CloseWindowCommand
from web_client_api.commands.strongholds import StrongholdsJoinBattleCommand
from web_client_api.commands import createNotificationHandler, createSoundHandler, createOpenWindowHandler, createCloseWindowHandler, createOpenTabHandler, createStrongholdsBattleHandler, createRequestHandler, instantiateObject
from gui import DialogsInterface
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.stronghold.unit.ctx import CreateUnitCtx, JoinUnitCtx
from gui.SystemMessages import SM_TYPE
from gui.SystemMessages import pushI18nMessage, pushMessage
from gui.shared import actions
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showClanProfileWindow, showProfileWindow, requestProfile, events, g_eventBus
from gui.shared.utils.requesters import getTokenRequester
from gui.shared.utils.functions import getViewName
from gui.app_loader import g_appLoader
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from skeletons.gui.game_control import IBrowserController, IReloginController

def createStrongholdsWebHandlers(includeCloseBrowser=False, onBrowserOpen=None, onBrowserClose=None):
    """
    Creates list of stronghold specific web handlers
    :param includeCloseBrowser: - whether 'close_browser' handler to be included
    :return: - list oh handlers
    """
    handlers = [createNotificationHandler(handleNotificationCommand),
     createSoundHandler(handleSoundCommand),
     createOpenWindowHandler(partial(handleOpenWindowCommand, onBrowserOpen)),
     createCloseWindowHandler(partial(handleCloseWindowCommand, onBrowserClose)),
     createOpenTabHandler(handleOpenTabCommand),
     createStrongholdsBattleHandler(handleStrongholdsBattleCommand),
     createRequestHandler(handleRequestCommand)]
    if includeCloseBrowser:
        handlers.append(createCloseWindowHandler(handleCloseWindowCommand))
    return handlers


def handleNotificationCommand(command, ctx):
    """
    Shows notification according to command's parameters
    """
    type = SM_TYPE.lookup(command.type)
    if type is None:
        raise WebCommandException("Unknown notification's type: %s!" % command.type)
    if command.hasKey():
        custom_parameters = command.custom_parameters
        params = {'type': type,
         'key': command.key}
        for key, value in custom_parameters.iteritems():
            params[key] = value

        pushI18nMessage(**params)
    elif command.hasMessage():
        pushMessage(command.message, type=type)
    else:
        raise WebCommandException("'key' or 'message' parameter are missing!")
    return


def handleSoundCommand(command, ctx):
    """
    Plays sound effect by id
    """
    app = g_appLoader.getApp()
    if app and app.soundManager:
        app.soundManager.playEffectSound(command.sound_id)


def handleOpenWindowCommand(onBrowserOpen, command, ctx):
    """
    Opens window by id
    """
    _OpenWindowSubCommands = {'clan_card_window': (OpenClanCardCommand, _openClanCard),
     'profile_window': (OpenProfileCommand, _openProfile),
     'browser': (OpenBrowserCommand, partial(_openBrowser, onBrowserOpen))}
    if command.window_id in _OpenWindowSubCommands:
        cls, handler = _OpenWindowSubCommands[command.window_id]
        subCommand = instantiateObject(cls, command.custom_parameters)
        handler(subCommand)
    else:
        raise WebCommandException('Unknown window: %s!' % command.window_id)


def handleCloseWindowCommand(onBrowserClose, command, ctx):
    """
    Closes window by id
    """
    _CloseWindowSubCommands = {'browser': (CloseWindowCommand, partial(_closeBrowser, onBrowserClose))}
    if command.window_id in _CloseWindowSubCommands:
        cls, handler = _CloseWindowSubCommands[command.window_id]
        command.custom_parameters = {'window_id': command.window_id}
        subCommand = instantiateObject(cls, command.custom_parameters)
        handler(subCommand, ctx)
    else:
        raise WebCommandException('Unknown window: %s!' % command.window_id)


def handleOpenTabCommand(command, ctx):
    """
    Opens tab by id
    """
    if command.tab_id in _OpenTabInfo:
        tabId = _OpenTabInfo[command.tab_id]
        g_eventBus.handleEvent(events.LoadViewEvent(tabId), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        raise WebCommandException('Unknown tab id: %s!' % command.tab_id)


def handleStrongholdsBattleCommand(command, ctx):
    """
    Executes battle specific actions
    """
    if command.action in _StrongholdsBattleActions:
        subCommand, handler = _StrongholdsBattleActions[command.action]
        if subCommand:
            subCommandInstance = instantiateObject(subCommand, command.custom_parameters)
            handler(subCommandInstance)
        else:
            handler()
    else:
        raise WebCommandException('Unknown strongholds battle action: %s!' % command.action)


def handleRequestCommand(command, ctx):
    """
    Makes request according to request_id
    """
    if command.request_id in _RequestCommands:

        def onCallback(data):
            data['request_id'] = command.request_id
            callback = ctx.get('callback')
            if callable(callback):
                callback(data)

        _RequestCommands[command.request_id](onCallback)
    else:
        raise WebCommandException('Unknown request id: %s!' % command.request_id)


def _openClanCard(command):
    """
    Opens clan card window
    """
    showClanProfileWindow(command.clan_dbid, command.clan_abbrev)


def _openProfile(command):
    """
    Opens profile window
    """

    def onDossierReceived(databaseID, userName):
        showProfileWindow(databaseID, userName)

    requestProfile(command.database_id, command.user_name, successCallback=onDossierReceived)


def _openBrowser(onBrowserOpen, command):
    """
    Opens browser window
    """
    _loadBrowser(onBrowserOpen, command.url, command.title, command.width, command.height, command.is_modal, command.show_refresh, command.show_create_waiting)


@process
def _loadBrowser(onBrowserOpen, url, title, width, height, isModal, showRefresh, showCreateWaiting):
    """
    Load browser and show window
    Takes onBrowserOpen callback with str param: aliasId. Called after browser was created.
    """
    browserCtrl = dependency.instance(IBrowserController)
    browserId = yield browserCtrl.load(url=url, title=title, browserSize=(width, height), isModal=isModal, showActionBtn=showRefresh, showCreateWaiting=showCreateWaiting, handlers=createStrongholdsWebHandlers(True))
    browser = browserCtrl.getBrowser(browserId)
    if browser is not None:
        browser.ignoreKeyEvents = True
    if onBrowserOpen is not None:
        alias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL if isModal else VIEW_ALIAS.BROWSER_WINDOW, browserId)
        onBrowserOpen(alias)
    return


def _closeBrowser(onBrowserClose, command, ctx):
    """
    Closes current browser window
    """
    if 'browser_id' in ctx:
        windowAlias = getViewName(ctx['browser_alias'], ctx['browser_id'])
        app = g_appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserWindow = app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.UNIQUE_NAME: windowAlias})
            if browserWindow is not None:
                browserWindow.destroy()
            else:
                raise WebCommandException("Browser window can't be found!")
    if onBrowserClose is not None:
        onBrowserClose()
    return


_OpenTabInfo = {'hangar': VIEW_ALIAS.LOBBY_HANGAR}

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

    if connectionManager.peripheryID != command.periphery_id:
        success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            reloginCtrl = dependency.instance(IReloginController)
            reloginCtrl.doRelogin(command.periphery_id, extraChainSteps=(actions.OnLobbyInitedAction(onInited=partial(doJoin, False)),))
    else:
        doJoin(True)


@process
def _doJoinBattle(dispatcher, unitMgrId, onErrorCallback):
    yield dispatcher.join(JoinUnitCtx(unitMgrId, PREBATTLE_TYPE.EXTERNAL, onErrorCallback=onErrorCallback, waitingID='prebattle/join'))


_StrongholdsBattleActions = {'open_list': (None, _openList),
 'battle_chosen': (None, _battleChosen),
 'join_battle': (StrongholdsJoinBattleCommand, _joinBattle)}

def _requestWgniToken(callback):
    tokenRqs = getTokenRequester(TOKEN_TYPE.WGNI)

    def onCallback(response):
        if response and response.isValid():
            callback({'token': response.getToken()})
        else:
            coolDownExpiration = tokenRqs.getReqCoolDown() - tokenRqs.lastResponseDelta()
            callback({'error': 'Unable to obtain token.',
             'cooldown': coolDownExpiration if coolDownExpiration > 0 else tokenRqs.getReqCoolDown()})

    if not tokenRqs.isInProcess():
        tokenRqs.request(timeout=10.0)(onCallback)
    else:
        onCallback(response=None)
    return


_RequestCommands = {'token1': _requestWgniToken}
