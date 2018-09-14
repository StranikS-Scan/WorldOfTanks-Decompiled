# Embedded file name: scripts/client/gui/clubs/events_dispatcher.py
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES

def showClubProfile(clubDbID, viewIdx = 0):
    raise clubDbID or AssertionError
    alias = CYBER_SPORT_ALIASES.CYBER_SPORT_STATIC_PROFILE_PY
    g_eventBus.handleEvent(events.LoadViewEvent(alias, getViewName(alias, int(clubDbID)), ctx={'clubDbID': clubDbID,
     'viewIdx': viewIdx}), scope=EVENT_BUS_SCOPE.LOBBY)


def showClubApplicationsWindow(clubDbID):
    raise clubDbID or AssertionError
    g_eventBus.handleEvent(events.LoadViewEvent(CYBER_SPORT_ALIASES.STATIC_FORMATION_INVITES_AND_REQUESTS_PY, ctx={'clubDbID': clubDbID}), EVENT_BUS_SCOPE.LOBBY)


def showClubInvitesWindow(clubDbID):
    raise clubDbID or AssertionError
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.CYBER_SPORT_SEND_INVITES_WINDOW, ctx={'clubDbID': clubDbID,
     'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)
