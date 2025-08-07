# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/shared/event_dispatcher.py
import logging
import typing
import wg_async
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from frameworks.wulf import ViewFlags
from gui.impl.lobby.common.sound_constants import BROWSER_VIEW_SOUND_SPACES
from mt_birthday.gui.impl.sounds import BIRTHDAY_SOUND_SPACE
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)
TARGET_MAIN_VIEW = 'mainView'
BROWSER_VIEW_SOUND_SPACES.update({BIRTHDAY_SOUND_SPACE.name: BIRTHDAY_SOUND_SPACE})

def showMainView(tabId=None):
    from mt_birthday.gui.impl.lobby.birthday.birthday_main_view import BirthdayMainView
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    __mtBirthday = dependency.instance(ITanksBirthdayController)
    if __mtBirthday.isEnabled():
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.mt_birthday.lobby.birthday.BirthdayMainView(), BirthdayMainView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId), scope=EVENT_BUS_SCOPE.LOBBY)


def _webHandlers():
    from web.web_client_api.shop import ShopWebApi
    from web.web_client_api.platform import PlatformWebApi
    from web.web_client_api.reactive_comm import ReactiveCommunicationWebApi
    from web.web_client_api import webApiCollection, ui, request, sound as sound_web_api
    from mt_birthday.web.web_client_api.gold_wagon.gold_wagon import GoldWagonWebApi
    return webApiCollection(request.RequestWebApi, ui.OpenWindowWebApi, ui.CloseWindowWebApi, ui.OpenTabWebApi, ui.UtilWebApi, ui.NotificationWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi, sound_web_api.SoundStateWebApi, ShopWebApi, PlatformWebApi, ReactiveCommunicationWebApi, GoldWagonWebApi)


def openGoldWagon(target=None):
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    lobbyContext = dependency.instance(ILobbyContext)
    mtBirthday = dependency.instance(ITanksBirthdayController)
    isEnabledGoldWagon = lobbyContext.getServerSettings().ingameBrowserEventConfig.isEnabled
    if mtBirthday.isEnabled() and isEnabledGoldWagon:
        url = lobbyContext.getServerSettings().ingameBrowserEventConfig.url
        suffix = 'overlay=1'
        url = '?'.join([url, suffix])

        def closeCallbackWrapper(*args, **kwargs):
            if kwargs.pop('forceClosed', False):
                if target == TARGET_MAIN_VIEW:
                    showMainView()
                    return
                g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

        layoutID = R.views.lobby.common.BrowserView()
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(layoutID))
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(loadParams=GuiImplViewLoadParams(layoutID, BrowserView, ScopeTemplates.DEFAULT_SCOPE), settings=makeSettings(url=url, webHandlers=_webHandlers(), viewFlags=ViewFlags.LOBBY_SUB_VIEW, returnClb=closeCallbackWrapper, restoreBackground=True, isClosable=True, soundSpaceID=BIRTHDAY_SOUND_SPACE.name)))


def showGoldWagon():
    openGoldWagon()


def showGoldWagonTankMail():
    openGoldWagon(TARGET_MAIN_VIEW)


@wg_async.wg_async
def showPlayerSelectView():
    from mt_birthday.gui.impl.lobby.birthday.player_select_view import PlayerSelectViewWindow
    window = PlayerSelectViewWindow()
    window.load()
    result = yield wg_async.wg_await(window.wait())
    _logger.info('PlayerSelectView return result=%s', result)


def sendSimpleGifts(ids):
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    from mt_birthday.birthday_constants import BIRTHDAY_2025_STAMP_CODE

    def printer(*args, **kwargs):
        print args, kwargs

    tbc = dependency.instance(ITanksBirthdayController)
    tbc.giftSystem.sendGifts(BIRTHDAY_2025_STAMP_CODE, ids, 1, printer)


def sendBloggerGift(pid):
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    from mt_birthday.birthday_constants import BIRTHDAY_2025_STAMP_CODE_SPECIAL

    def printer(*args, **kwargs):
        print args, kwargs

    tbc = dependency.instance(ITanksBirthdayController)
    tbc.giftSystem.sendGifts(BIRTHDAY_2025_STAMP_CODE_SPECIAL, [pid], 1, printer)


def showCollageView():
    from mt_birthday.gui.impl.lobby.birthday.collage_view import CollageView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(loadParams=GuiImplViewLoadParams(R.views.mt_birthday.lobby.birthday.CollageView(), CollageView, ScopeTemplates.DEFAULT_SCOPE)))
