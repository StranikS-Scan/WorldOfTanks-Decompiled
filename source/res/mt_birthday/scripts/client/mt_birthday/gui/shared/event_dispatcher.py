# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/shared/event_dispatcher.py
import logging
import typing
import th_async
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showMissionsGrouped
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from gui.impl.lobby.common.sound_constants import BROWSER_VIEW_SOUND_SPACES
from mt_birthday.gui.impl.sounds import BIRTHDAY_SOUND_SPACE
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
from mt_birthday.gui.shared.events import BirthdayEvent
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)
BROWSER_VIEW_SOUND_SPACES.update({BIRTHDAY_SOUND_SPACE.name: BIRTHDAY_SOUND_SPACE})

def showMainView(tabId=None):
    from mt_birthday.gui.impl.lobby.birthday.birthday_main_view import BirthdayMainView
    __mtBirthday = dependency.instance(ITanksBirthdayController)
    if __mtBirthday.isEnabled():
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.mt_birthday.lobby.birthday.BirthdayMainView(), BirthdayMainView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId), scope=EVENT_BUS_SCOPE.LOBBY)


def closeBirthdayMainView():
    g_eventBus.handleEvent(BirthdayEvent(BirthdayEvent.DESTROY_BIRTHDAY_MAIN_VIEW))


def showGoldWagon():
    showMainView(TabId.GOLD_WAGON)


def showTicketExchange():
    showMainView(TabId.TICKET_EXCHANGE)


@th_async.th_async
def showPlayerSelectView():
    from mt_birthday.gui.impl.lobby.birthday.player_select_view import PlayerSelectViewWindow
    window = PlayerSelectViewWindow()
    window.load()
    result = yield th_async.th_await(window.wait())
    _logger.info('PlayerSelectView return result=%s', result)


def sendSimpleGifts(ids):
    from mt_birthday.birthday_constants import BIRTHDAY_STAMP_CODE

    def printer(*args, **kwargs):
        _logger.info('sendSimpleGifts %s %s', args, kwargs)

    tbc = dependency.instance(ITanksBirthdayController)
    tbc.giftSystem.sendGifts(BIRTHDAY_STAMP_CODE, ids, 1, printer)


def sendBloggerGift(pid):
    from mt_birthday.birthday_constants import BIRTHDAY_STAMP_CODE_SPECIAL

    def printer(*args, **kwargs):
        _logger.info('sendBloggerGift %s %s', args, kwargs)

    tbc = dependency.instance(ITanksBirthdayController)
    tbc.giftSystem.sendGifts(BIRTHDAY_STAMP_CODE_SPECIAL, [pid], 1, printer)


@dependency.replace_none_kwargs(controller=ITanksBirthdayController)
def showQuestsToEarnStamps(controller=None):
    if controller.hasActiveQuestGiverQuest():
        showMainView(tabId=TabId.QUESTS)
    else:
        showMissionsGrouped()
