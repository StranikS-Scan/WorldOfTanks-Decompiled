# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/QuestsControl.py
from debug_utils import LOG_DEBUG
from gui import game_control
from gui.shared import g_eventsCache, events
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.QuestsControlMeta import QuestsControlMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule
from gui.shared.gui_items import GUI_ITEM_TYPE
from items import getTypeOfCompactDescr

class QuestsControl(QuestsControlMeta, DAAPIModule):

    def __init__(self):
        super(QuestsControl, self).__init__()
        self.__isHighlighted = False

    def _populate(self):
        super(QuestsControl, self)._populate()
        g_eventsCache.onSyncCompleted += self.__onQuestsUpdated
        game_control.g_instance.igr.onIgrTypeChanged += self.__onQuestsUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onQuestsUpdated,
         'cache.eventsData': self.__onQuestsUpdated,
         'inventory.1': self.__onQuestsUpdated,
         'stats.unlocks': self.__onItemUnlocked})
        self.addListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onQuestsUpdated)
        self.__onQuestsUpdated()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onQuestsUpdated)
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onQuestsUpdated
        g_eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        super(QuestsControl, self)._dispose()

    def showQuestsWindow(self):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_EVENTS_WINDOW))

    def __onItemUnlocked(self, unlocks):
        for intCD in unlocks:
            if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                return self.__onQuestsUpdated()

    def __onQuestsUpdated(self, *args):
        svrEvents = g_eventsCache.getEvents()
        events_helpers.updateEventsSettings(svrEvents)
        newQuestsCount = len(events_helpers.getNewEvents(svrEvents))
        if newQuestsCount:
            if not self.__isHighlighted:
                self.as_highlightControlS()
        else:
            self.as_resetControlS()
        self.__isHighlighted = bool(newQuestsCount)
