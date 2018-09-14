# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/QuestsControl.py
from collections import namedtuple
from account_helpers.AccountSettings import AccountSettings, IGR_PROMO
from gui.LobbyContext import g_lobbyContext
from gui.shared.formatters import text_styles
from helpers import i18n
from gui import game_control
from gui.server_events.events_dispatcher import showEventsWindow
from gui.shared import events, EVENT_BUS_SCOPE
from gui.server_events import g_eventsCache, settings as quest_settings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.meta.QuestsControlMeta import QuestsControlMeta
_QuestButtonInfo = namedtuple('QuestButtonInfo', 'text tooltip alert highlight')

def _createBtnInfo(text='', tooltip='', alert=False, highlight=True):
    return _QuestButtonInfo(text, tooltip, alert, highlight)


class QuestsControl(QuestsControlMeta):

    def __init__(self):
        super(QuestsControl, self).__init__()
        self.__isHighlighted = False

    def _populate(self):
        super(QuestsControl, self)._populate()
        g_eventsCache.onProgressUpdated += self.__onQuestsUpdated
        game_control.g_instance.igr.onIgrTypeChanged += self.__onQuestsUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onQuestsUpdated,
         'cache.eventsData': self.__onQuestsUpdated})
        self.__onQuestsUpdated()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onQuestsUpdated
        g_eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(QuestsControl, self)._dispose()

    def showQuestsWindow(self):
        showEventsWindow()

    def __onQuestsUpdated(self, *args):
        svrEvents = g_eventsCache.getEvents()
        quest_settings.updateCommonEventsSettings(svrEvents)
        self.as_setDataS({'titleText': QUESTS.QUESTSCONTROL_TITLE,
         'tooltip': TOOLTIPS.PRIVATEQUESTS_QUESTCONTROL})
        premiumIgrVehiclesQuests = g_eventsCache.getQuests(lambda q: q.getStartTimeLeft() <= 0 < q.getFinishTimeLeft() and q.hasPremIGRVehBonus())
        if len(premiumIgrVehiclesQuests):
            storedValue = AccountSettings.getFilter(IGR_PROMO)
            if not storedValue['wasShown']:
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW), EVENT_BUS_SCOPE.LOBBY)
