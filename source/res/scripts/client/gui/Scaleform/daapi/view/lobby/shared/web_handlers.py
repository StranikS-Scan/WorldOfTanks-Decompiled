# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from functools import partial
import SoundGroups
import nations
from adisp import process
from constants import TOKEN_TYPE
from debug_utils import LOG_DEBUG
from helpers import dependency
from items import vehicles
from gui.clans.settings import AccessTokenData
from helpers import time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.clans import IClanController
from skeletons.gui.game_control import IBrowserController
from gui.SystemMessages import SM_TYPE
from gui.SystemMessages import pushI18nMessage, pushMessage
from gui.shared.utils.functions import getViewName
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import events, g_eventBus
from gui.shared.utils import graphics
from gui.shared.utils.requesters import getTokenRequester
from gui.app_loader import g_appLoader
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import CustomUserCMHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from web_client_api import WebCommandException
from web_client_api.commands import instantiateObject
from web_client_api.commands.context_menu import UserContextMenuCommand
from web_client_api.commands.request import RequestAccessTokenCommand
from web_client_api.commands.window_navigator import OpenBrowserCommand

def handleNotificationCommand(command, ctx):
    """
    Shows notification according to command's parameters
    """
    type = SM_TYPE.lookup(command.type)
    if type is None:
        raise WebCommandException("Unknown notification's type: %s!" % command.type)
    if command.hasMessage():
        pushMessage(command.message, type=type, messageData=command.message_data)
    elif command.hasI18nKey():
        parameters = command.i18n_data
        params = {'type': type,
         'key': command.i18n_key,
         'messageData': command.message_data}
        for key, value in parameters.iteritems():
            params[key] = value

        pushI18nMessage(**params)
    elif command.hasKey():
        custom_parameters = command.custom_parameters
        params = {'type': type,
         'key': command.key,
         'messageData': command.message_data}
        for key, value in custom_parameters.iteritems():
            params[key] = value

        pushI18nMessage(**params)
    else:
        raise WebCommandException("'i18n_key' or 'message' parameter are missing!")
    return


def handleSoundCommand(command, ctx):
    """
    Plays sound effect by id
    """
    app = g_appLoader.getApp()
    if app and app.soundManager:
        app.soundManager.playEffectSound(command.sound_id)


def handleHangarSoundCommand(command, ctx):
    """
    Mutes/unmutes hangar sound
    """
    if command.mute:
        SoundGroups.g_instance.playSound2D('ue_master_mute')
    else:
        SoundGroups.g_instance.playSound2D('ue_master_unmute')


def handleHangarSoundCommandFini():
    """
    Reverts handler
    """
    SoundGroups.g_instance.playSound2D('ue_master_unmute')


def createOpenWindowCommandHandler(subCommands):

    def handleOpenWindowCommand(command, ctx):
        """
        Opens window by id
        """
        if command.window_id in subCommands:
            cls, handler = subCommands[command.window_id]
            if cls:
                subCommand = instantiateObject(cls, command.custom_parameters)
                handler(subCommand)
            else:
                handler()
        else:
            raise WebCommandException('Unknown window: %s!' % command.window_id)

    return handleOpenWindowCommand


def handleCloseWindowCommand(onBrowserClose, command, ctx, isWindow=True):
    """
    Closes window by id
    """
    if isWindow:
        closeWindowSubCommands = {'browser': partial(_closeBrowserWindow, onBrowserClose)}
    else:
        closeWindowSubCommands = {'browser': _closeBrowserView}
    if command.window_id in closeWindowSubCommands:
        handler = closeWindowSubCommands[command.window_id]
        handler(ctx)
    else:
        raise WebCommandException('Unknown window: %s!' % command.window_id)


def handleOpenTabCommand(command, ctx):
    """
    Opens tab by id
    """
    if command.tab_id in OPEN_TAB_INFO:
        tabId, elementsList = OPEN_TAB_INFO[command.tab_id]
        ctx = None if not elementsList else elementsList.get(command.selected_id)
        g_eventBus.handleEvent(events.LoadViewEvent(tabId, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        raise WebCommandException('Unknown tab id: %s!' % command.tab_id)
    return


def handleRequestCommand(command, ctx):
    """
    Makes request according to request_id
    """
    if command.request_id in REQUEST_COMMANDS:

        def onCallback(data):
            data['request_id'] = command.request_id
            callback = ctx.get('callback')
            if callable(callback):
                callback(data)

        cls, handler = REQUEST_COMMANDS[command.request_id]
        if cls is not None:
            subCommand = instantiateObject(cls, command.custom_parameters)
            handler(subCommand, onCallback)
        else:
            handler(onCallback)
    else:
        raise WebCommandException('Unknown request id: %s!' % command.request_id)
    return


def handleContextMenuCommand(command, ctx):
    """
    Shows context menu by type
    """
    if command.menu_type in CONTEXT_MENU_TYPES:
        subCommand, handler = CONTEXT_MENU_TYPES[command.menu_type]
        subCommandInstance = instantiateObject(subCommand, command.custom_parameters)

        def onCallback(data):
            data['menu_type'] = command.menu_type
            data['spa_id'] = subCommandInstance.spa_id
            callback = ctx.get('callback')
            if callable(callback):
                callback(data)

        handler(subCommandInstance, ctx, onCallback)
    else:
        raise WebCommandException('Unknown context menu type: %s!' % command.menu_type)


def handleVehiclesCommand(command, ctx):
    """
    Returns vehicles info
    """
    if command.action in VEHICLES_ACTIONS:
        handler = VEHICLES_ACTIONS[command.action]
        handler(command, ctx.get('callback'))
    else:
        raise WebCommandException('Unknown vehicles action: %s!' % command.action)


def _openBrowser(onBrowserOpen, handlersCreator, command):
    """
    Opens browser window
    """
    _loadBrowser(onBrowserOpen, handlersCreator, command.url, command.title, command.width, command.height, command.is_modal, command.show_refresh, command.show_create_waiting)


@process
def _loadBrowser(onBrowserOpen, handlersCreator, url, title, width, height, isModal, showRefresh, showCreateWaiting):
    """
    Load browser and show window
    Takes onBrowserOpen callback with str param: aliasId. Called after browser was created.
    """
    browserCtrl = dependency.instance(IBrowserController)
    browserId = yield browserCtrl.load(url=url, title=title, browserSize=(width, height), isModal=isModal, showActionBtn=showRefresh, showCreateWaiting=showCreateWaiting, handlers=handlersCreator() if callable(handlersCreator) else None)
    browser = browserCtrl.getBrowser(browserId)
    if browser is not None:
        browser.ignoreKeyEvents = True
    if onBrowserOpen is not None:
        alias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL if isModal else VIEW_ALIAS.BROWSER_WINDOW, browserId)
        onBrowserOpen(alias)
    return


def createOpenBrowserSubCommands(onBrowserOpen, handlersCreator):
    return {'browser': (OpenBrowserCommand, partial(_openBrowser, onBrowserOpen, handlersCreator))}


def _closeBrowserWindow(onBrowserClose, ctx):
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


def _closeBrowserView(ctx):
    """
    Closes current browser view
    """
    app = g_appLoader.getApp()
    if app is not None and app.containerManager is not None:
        browserView = app.containerManager.getView(ViewTypes.LOBBY_SUB, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
        if browserView is not None:
            browserView.onCloseView()
            return
    raise WebCommandException('Unable to find BrowserView!')
    return


OPEN_TAB_INFO = {'hangar': (VIEW_ALIAS.LOBBY_HANGAR, None),
 'profile': (VIEW_ALIAS.LOBBY_PROFILE, {'hof': {'selectedAlias': VIEW_ALIAS.PROFILE_HOF},
              'technique': {'selectedAlias': VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE},
              'summary': {'selectedAlias': VIEW_ALIAS.PROFILE_SUMMARY_PAGE}})}

def _requestWgniToken(callback):
    tokenRqs = getTokenRequester(TOKEN_TYPE.WGNI)

    def onCallback(response):
        if response and response.isValid():
            callback({'spa_id': str(response.getDatabaseID()),
             'token': response.getToken()})
        else:
            coolDownExpiration = tokenRqs.getReqCoolDown() - tokenRqs.lastResponseDelta()
            callback({'error': 'Unable to obtain token.',
             'cooldown': coolDownExpiration if coolDownExpiration > 0 else tokenRqs.getReqCoolDown()})

    if not tokenRqs.isInProcess():
        tokenRqs.request(timeout=10.0)(onCallback)
    else:
        onCallback(response=None)
    return


def _requestGraphicsSettings(callback):
    settings = {'CUSTOM_AA_MODE': graphics.getCustomAAMode(),
     'MULTISAMPLING': graphics.getMultisamplingType()}
    settingNames = ('TEXTURE_QUALITY', 'LIGHTING_QUALITY', 'SHADOWS_QUALITY', 'SNIPER_MODE_GRASS_ENABLED', 'EFFECTS_QUALITY', 'SNIPER_MODE_EFFECTS_QUALITY', 'FLORA_QUALITY', 'POST_PROCESSING_QUALITY', 'VEHICLE_DUST_ENABLED', 'RENDER_PIPELINE')
    for settingName in settingNames:
        setting = graphics.getGraphicsSetting(settingName)
        if setting is not None:
            settings[settingName] = setting.value
        LOG_DEBUG('Settings "%s" not found!' % settingName)

    callback({'settings': settings})
    return


@process
@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def _requestAccessToken(command, callback, connectionMgr=None):
    ctrl = dependency.instance(IClanController)
    accessTokenData = yield ctrl.getAccessTokenData(force=command.force)
    if accessTokenData is not None:
        callback({'spa_id': str(connectionMgr.databaseID),
         'access_token': str(accessTokenData.accessToken),
         'expires_in': accessTokenData.expiresAt - time_utils.getCurrentTimestamp(),
         'periphery_id': str(connectionMgr.peripheryID)})
    else:
        callback({'error': 'Unable to obtain access token.'})
    return


REQUEST_COMMANDS = {'token1': (None, _requestWgniToken),
 'graphics_settings': (None, _requestGraphicsSettings),
 'access_token': (RequestAccessTokenCommand, _requestAccessToken)}

def _showUserContextMenu(command, ctx, callback):
    context = {'dbID': command.spa_id,
     'userName': command.user_name,
     'customItems': command.custom_items,
     'excludedItems': command.excluded_items}
    browserView = ctx.get('browser_view')
    app = g_appLoader.getApp()
    try:
        browserView.as_showContextMenuS(CONTEXT_MENU_HANDLER_TYPE.CUSTOM_USER, context)
        cmHandler = app.contextMenuManager.getCurrentHandler()
    except AttributeError as ex:
        raise WebCommandException('Failed to show context menu: %s' % ex)

    if cmHandler is not None and isinstance(cmHandler, CustomUserCMHandler):
        webBrowser = dependency.instance(IBrowserController).getBrowser(ctx.get('browser_id'))
        webBrowser.allowMouseWheel = False

        def onSelectedCallback(optionId):
            callback({'menu_type': 'user_menu',
             'selected_item': optionId})
            webBrowser.allowMouseWheel = True

        cmHandler.onSelected += onSelectedCallback
    else:
        callback({'menu_type': 'user_menu',
         'selected_item': None})
    return


CONTEXT_MENU_TYPES = {'user_menu': (UserContextMenuCommand, _showUserContextMenu)}

def _getVehicleInfo(command, callback):
    try:
        vehicle = vehicles.getVehicleType(command.vehicle_id)
    except:
        res = {'error': 'vehicle_id is invalid.'}
    else:
        res = {'vehicle': {'vehicle_id': vehicle.compactDescr,
                     'tag': vehicle.name,
                     'name': vehicle.userString,
                     'short_name': vehicle.shortUserString,
                     'nation': nations.NAMES[vehicle.id[0]],
                     'type': vehicles.getVehicleClassFromVehicleType(vehicle),
                     'tier': vehicle.level,
                     'is_premium': bool('premium' in vehicle.tags)}}

    callback(res)


VEHICLES_ACTIONS = {'vehicle_info': _getVehicleInfo}
