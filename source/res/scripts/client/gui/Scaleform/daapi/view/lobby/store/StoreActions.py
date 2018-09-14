# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreActions.py
from async import async, await
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.store.actions_formatters import ActionsBuilder
from gui.Scaleform.daapi.view.meta.StoreActionsViewMeta import StoreActionsViewMeta
from gui.server_events.events_dispatcher import showMission
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class StoreActions(StoreActionsViewMeta):
    eventsCache = dependency.descriptor(IEventsCache)

    def actionSelect(self, triggerChainID):
        """
        run tutorial sales chain for selected action
        :param triggerChainID: str
        """
        event_dispatcher.runSalesChain(triggerChainID)

    def onActionSeen(self, actionId):
        self._actionsBuilder.markVisited(actionId)

    def onBattleTaskSelect(self, actionId):
        if actionId:
            id = actionId.split('/')[0]
            action = self.eventsCache.getActions().get(id)
            if action:
                for quest in action.linkedQuests:
                    showMission(quest)
                    break

    def _populate(self):
        super(StoreActions, self)._populate()
        self._actionsBuilder = ActionsBuilder()
        self.eventsCache.onSyncCompleted += self.__onEventUpdate
        self.__update()

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self.__onEventUpdate
        super(StoreActions, self)._dispose()

    @classmethod
    def _getActions(cls):

        def _filterFunc(x):
            return not x.isOutOfDate()

        actions = cls.eventsCache.getActions(filterFunc=_filterFunc).values()
        actionsEntities = cls.eventsCache.getActionEntities()
        announcedActions = cls.eventsCache.getAnnouncedActions()
        return (actions, actionsEntities, announcedActions)

    @async
    def __update(self):
        Waiting.show('updateShop')
        yield await(self.eventsCache.prefetcher.demand())
        Waiting.hide('updateShop')
        self.as_setDataS(self._actionsBuilder.format(*self._getActions()))

    def __onEventUpdate(self, *_):
        self.__update()
