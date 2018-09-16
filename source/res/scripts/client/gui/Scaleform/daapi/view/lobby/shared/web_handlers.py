# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from functools import partial
import SoundGroups
import nations
from adisp import process
from constants import TOKEN_TYPE
from debug_utils import LOG_DEBUG
from helpers import dependency, time_utils
from items import vehicles
from gui.wgcg.states import AccessTokenData
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.web import IWebController
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

def handleNotificationCommand(command, ctx):
    smType = SM_TYPE.lookup(command.type)
    if smType is None:
        raise WebCommandException("Unknown notification's type: %s!" % command.type)
    if command.hasMessage():
        pushMessage(command.message, type=smType, messageData=command.message_data)
    elif command.hasI18nKey():
        parameters = command.i18n_data
        params = {'type': smType,
         'key': command.i18n_key,
         'messageData': command.message_data}
        for key, value in parameters.iteritems():
            params[key] = value

        pushI18nMessage(**params)
    elif command.hasKey():
        custom_parameters = command.custom_parameters
        params = {'type': smType,
         'key': command.key,
         'messageData': command.message_data}
        for key, value in custom_parameters.iteritems():
            params[key] = value

        pushI18nMessage(**params)
    return


def handleSoundCommand(command, ctx):
    app = g_appLoader.getApp()
    if app and app.soundManager:
        app.soundManager.playEffectSound(command.sound_id)


def handleHangarSoundCommand(command, ctx):
    if command.mute:
        SoundGroups.g_instance.playSound2D('ue_master_mute')
    else:
        SoundGroups.g_instance.playSound2D('ue_master_unmute')


def handleHangarSoundCommandFini():
    SoundGroups.g_instance.playSound2D('ue_master_unmute')


def _openTab(tabId, elementsList, command, ctx):
    selectedCtx = None if not elementsList else elementsList.get(command.selected_id)
    g_eventBus.handleEvent(events.LoadViewEvent(tabId, ctx=selectedCtx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def getOpenHangarTabHandler():
    return partial(_openTab, VIEW_ALIAS.LOBBY_HANGAR, None)


def getOpenProfileTabHandler():
    return partial(_openTab, VIEW_ALIAS.LOBBY_PROFILE, {'hof': {'selectedAlias': VIEW_ALIAS.PROFILE_HOF},
     'technique': {'selectedAlias': VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE},
     'summary': {'selectedAlias': VIEW_ALIAS.PROFILE_SUMMARY_PAGE}})


def _openBrowser(onBrowserOpen, handlersCreator, command, ctx):
    _loadBrowser(onBrowserOpen, handlersCreator, command.url, command.title, command.width, command.height, command.is_modal, command.show_refresh, command.show_create_waiting)


@process
def _loadBrowser(onBrowserOpen, handlersCreator, url, title, width, height, isModal, showRefresh, showCreateWaiting):
    browserCtrl = dependency.instance(IBrowserController)
    browserId = yield browserCtrl.load(url=url, title=title, browserSize=(width, height), isModal=isModal, showActionBtn=showRefresh, showCreateWaiting=showCreateWaiting, handlers=handlersCreator() if callable(handlersCreator) else None)
    browser = browserCtrl.getBrowser(browserId)
    if browser is not None:
        browser.ignoreKeyEvents = True
    if onBrowserOpen is not None:
        alias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL if isModal else VIEW_ALIAS.BROWSER_WINDOW, browserId)
        onBrowserOpen(alias)
    return


def getOpenBrowserHandler(onBrowserOpen, handlersCreator):
    return partial(_openBrowser, onBrowserOpen, handlersCreator)


def _handlerCloseBrowserWindow(onBrowserClose, command, ctx):
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


def getCloseBrowserWindowHandler(onBrowserClose=None):
    return partial(_handlerCloseBrowserWindow, onBrowserClose)


def handleCloseBrowserView(command, ctx):
    app = g_appLoader.getApp()
    if app is not None and app.containerManager is not None:
        browserView = app.containerManager.getView(ViewTypes.LOBBY_SUB, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
        if browserView is not None:
            browserView.onCloseView()
            return
    raise WebCommandException('Unable to find BrowserView!')
    return


def handleRequestWgniToken(command, ctx):
    tokenRqs = getTokenRequester(TOKEN_TYPE.WGNI)
    callback = ctx.get('callback')

    def onCallback(response):
        if response and response.isValid():
            callback({'request_id': 'token1',
             'spa_id': str(response.getDatabaseID()),
             'token': response.getToken()})
        else:
            coolDownExpiration = tokenRqs.getReqCoolDown() - tokenRqs.lastResponseDelta()
            callback({'request_id': 'token1',
             'error': 'Unable to obtain token.',
             'cooldown': coolDownExpiration if coolDownExpiration > 0 else tokenRqs.getReqCoolDown()})

    if not tokenRqs.isInProcess():
        tokenRqs.request(timeout=10.0)(onCallback)
    else:
        onCallback(response=None)
    return


def handlerRequestGraphicsSettings(command, ctx):
    settings = {}
    settingNames = ('TEXTURE_QUALITY', 'LIGHTING_QUALITY', 'SHADOWS_QUALITY', 'SNIPER_MODE_GRASS_ENABLED', 'EFFECTS_QUALITY', 'SNIPER_MODE_EFFECTS_QUALITY', 'FLORA_QUALITY', 'POST_PROCESSING_QUALITY', 'VEHICLE_DUST_ENABLED', 'CUSTOM_AA_MODE', 'MSAA_QUALITY', 'RENDER_PIPELINE')
    for settingName in settingNames:
        setting = graphics.getGraphicsSetting(settingName)
        if setting is not None:
            settings[settingName] = setting.value
        LOG_DEBUG('Settings "%s" not found!' % settingName)

    ctx['callback']({'request_id': 'graphics_settings',
     'settings': settings})
    return


@process
@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def handleRequestAccessToken(command, ctx, connectionMgr=None):
    ctrl = dependency.instance(IWebController)
    accessTokenData = yield ctrl.getAccessTokenData(force=command.force)
    if accessTokenData is not None:
        ctx['callback']({'spa_id': str(connectionMgr.databaseID),
         'access_token': str(accessTokenData.accessToken),
         'expires_in': accessTokenData.expiresAt - time_utils.getCurrentTimestamp(),
         'periphery_id': str(connectionMgr.peripheryID)})
    else:
        ctx['callback']({'error': 'Unable to obtain access token.'})
    return


def handleShowUserContextMenu(command, ctx):
    context = {'dbID': command.spa_id,
     'userName': command.user_name,
     'customItems': command.custom_items,
     'excludedItems': command.excluded_items}
    callback = ctx.get('callback')
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
             'selected_item': optionId,
             'spa_id': command.spa_id})
            webBrowser.allowMouseWheel = True

        cmHandler.onSelected += onSelectedCallback
    else:
        callback({'menu_type': 'user_menu',
         'selected_item': None,
         'spa_id': command.spa_id})
    return


def handleGetVehicleInfo(command, ctx):
    try:
        vehicle = vehicles.getVehicleType(command.vehicle_id)
    except Exception:
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

    ctx['callback'](res)
