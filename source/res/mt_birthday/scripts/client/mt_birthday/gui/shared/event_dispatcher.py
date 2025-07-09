# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/shared/event_dispatcher.py
import logging
import typing
import wg_async
from constants import IS_CLIENT
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if IS_CLIENT:
    from gui.shared.event_dispatcher import showBrowserOverlayView
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)

def showMainView(tabId=None):
    from mt_birthday.gui.impl.lobby.birthday.birthday_main_view import BirthdayMainView
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    __mtBirthday = dependency.instance(ITanksBirthdayController)
    if __mtBirthday.isEnabled():
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.mt_birthday.lobby.birthday.BirthdayMainView(), BirthdayMainView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId), scope=EVENT_BUS_SCOPE.LOBBY)


def showGoldWagon():
    from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
    lobbyContext = dependency.instance(ILobbyContext)
    mtBirthday = dependency.instance(ITanksBirthdayController)
    isEnabledGoldWagon = lobbyContext.getServerSettings().ingameBrowserEventConfig.isEnabled
    if mtBirthday.isEnabled() and isEnabledGoldWagon:
        url = lobbyContext.getServerSettings().ingameBrowserEventConfig.url
        suffix = 'overlay=1'
        url = '?'.join([url, suffix])
        showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)


def showGoldWagonTankMail():
    lobbyContext = dependency.instance(ILobbyContext)
    url = lobbyContext.getServerSettings().ingameBrowserEventConfig.url
    showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)


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
