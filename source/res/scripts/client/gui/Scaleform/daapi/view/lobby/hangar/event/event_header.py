# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_header.py
import logging
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from constants import QUEUE_TYPE
from gui.Scaleform.framework.entities.View import ViewKeyDynamic
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventHeaderMeta import EventHeaderMeta
from gui.prb_control.entities.event.squad.entity import EventBattleSquadEntity
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.events_dispatcher import showEventTab
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.events import ViewEventType
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IEventTokenController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class _OffHeaderLifecycleHandler(IViewLifecycleHandler):
    __DYNAMIC = (VIEW_ALIAS.EVENT_BATTLE_RESULTS,
     VIEW_ALIAS.EVENT_BATTLE_QUEUE,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.EVENT_STYLES_PREVIEW,
     VIEW_ALIAS.EVENT_STYLES_SHOP_PREVIEW,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS,
     VIEW_ALIAS.EVENT_CONFIRMATION,
     VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW,
     VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONGRATULATION)

    def __init__(self, header):
        super(_OffHeaderLifecycleHandler, self).__init__([ ViewKeyDynamic(alias) for alias in self.__DYNAMIC ])
        self.__loadedSubViews = set()
        self.__header = header

    def onViewCreated(self, view):
        if view.key not in self.__loadedSubViews:
            self.__loadedSubViews.add(view.key)
            self.__notifyHeader()

    def onViewDestroyed(self, view):
        if view.key in self.__loadedSubViews:
            self.__loadedSubViews.remove(view.key)
            self.__notifyHeader()

    def __notifyHeader(self):
        self.__header.setViewsWithoutHeader(len(self.__loadedSubViews) > 0)


class _OnHeaderLifecycleHandler(IViewLifecycleHandler):
    __DYNAMIC = (VIEW_ALIAS.EVENT_QUESTS,
     VIEW_ALIAS.EVENT_SHOP,
     VIEW_ALIAS.EVENT_NOTES,
     VIEW_ALIAS.EVENT_ABOUT,
     VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.EVENT_DIFFICULTY,
     VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS,
     VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONFIRMATION,
     VIEW_ALIAS.EVENT_PLAYER_PACK_CONFIRMATION,
     VIEW_ALIAS.EVENT_ITEM_PACK_CONFIRMATION)

    def __init__(self, header):
        super(_OnHeaderLifecycleHandler, self).__init__([ ViewKeyDynamic(alias) for alias in self.__DYNAMIC ])
        self.__loadedSubViews = set()
        self.__header = header

    def onViewCreated(self, view):
        if view.key not in self.__loadedSubViews:
            self.__loadedSubViews.add(view.key)
            self.__notifyHeader()

    def onViewDestroyed(self, view):
        if view.key in self.__loadedSubViews:
            self.__loadedSubViews.remove(view.key)
            self.__notifyHeader()

    def __notifyHeader(self):
        self.__header.setViewsWithEventHeader(len(self.__loadedSubViews) > 0)


class EventHeader(EventHeaderMeta, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    eventTokenController = dependency.descriptor(IEventTokenController)
    _SHOP_TAB_INDEX = 2

    def __init__(self):
        super(EventHeader, self).__init__()
        self.__isNavigationEnabled = True
        self.__badViewLifecycleWatcher = ViewLifecycleWatcher()
        self.__goodViewLifecycleWatcher = ViewLifecycleWatcher()
        self.__subViewsWithoutHeader = False
        self.__subViewsWithEventHeader = False

    def setViewsWithoutHeader(self, state):
        self.__subViewsWithoutHeader = state
        self.__updateVisible()

    def setViewsWithEventHeader(self, state):
        self.__subViewsWithEventHeader = state
        self.__updateVisible()

    def menuItemClick(self, alias):
        if alias == self._openedViewAlias:
            _logger.warning('Alias already loaded: %s', alias)
        else:
            showEventTab(alias)

    def onTabChanged(self, event):
        alias = event.ctx['alias']
        self.as_setScreenS(alias)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx=event.ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def onUnitPlayerBecomeCreator(self, pInfo):
        self.__updateHeader()

    def onPrbEntitySwitched(self):
        self.as_setScreenS(VIEW_ALIAS.LOBBY_HANGAR)
        self.__updateVisible()
        self.__updateHeader()

    def onEnqueued(self, queueType, *args):
        self.__updateVisible()

    def onDequeued(self, queueType, *args):
        self.__updateVisible()

    def _populate(self):
        super(EventHeader, self)._populate()
        self.__updateHeader()
        self.as_setScreenS(VIEW_ALIAS.LOBBY_HANGAR)
        self.__updateVisible()
        self.__updateCoins()
        self.__updateNotesTabCounter()
        self.__updateSelectedDifficultyLevel()
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.eventTokenController.onNotesUpdated += self.__updateNotesTabCounter
        self.gameEventController.onSelectedDifficultyLevelChanged += self.__updateSelectedDifficultyLevel
        self.eventTokenController.onEventMoneyUpdated += self.__updateCoins
        g_eventBus.addListener(events.EventHeaderEvent.TAB_CHANGED, self.onTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__updateTabs, EVENT_BUS_SCOPE.LOBBY)
        self.__badViewLifecycleWatcher.start(self.app.containerManager, [_OffHeaderLifecycleHandler(self)])
        self.__goodViewLifecycleWatcher.start(self.app.containerManager, [_OnHeaderLifecycleHandler(self)])
        self._openedViewAlias = None
        return

    def _dispose(self):
        self.stopGlobalListening()
        self.__badViewLifecycleWatcher.stop()
        self.__goodViewLifecycleWatcher.stop()
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.eventTokenController.onNotesUpdated -= self.__updateNotesTabCounter
        self.gameEventController.onSelectedDifficultyLevelChanged -= self.__updateSelectedDifficultyLevel
        self.eventTokenController.onEventMoneyUpdated -= self.__updateCoins
        g_eventBus.removeListener(events.EventHeaderEvent.TAB_CHANGED, self.onTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__updateTabs, EVENT_BUS_SCOPE.LOBBY)
        super(EventHeader, self)._dispose()

    def __updateHeader(self):
        menuData = [{'label': backport.text(R.strings.event.hangar.header.base()),
          'value': VIEW_ALIAS.LOBBY_HANGAR,
          'tooltip': 'tooltip'},
         {'label': backport.text(R.strings.event.hangar.header.missions()),
          'value': VIEW_ALIAS.EVENT_QUESTS,
          'tooltip': 'tooltip'},
         {'label': backport.text(R.strings.event.hangar.header.notes()),
          'value': VIEW_ALIAS.EVENT_NOTES,
          'tooltip': 'tooltip'},
         {'label': backport.text(R.strings.event.hangar.header.about()),
          'value': VIEW_ALIAS.EVENT_ABOUT,
          'tooltip': 'tooltip'},
         {'label': backport.text(R.strings.event.hangar.header.difficulty()),
          'value': VIEW_ALIAS.EVENT_DIFFICULTY,
          'tooltip': self._getDifficultyLevelTooltipData(),
          'enabled': self._enableDifficultyBtn()}]
        shopEnabled = self.gameEventController.getShop().isEnabled()
        if shopEnabled:
            menuData.insert(self._SHOP_TAB_INDEX, {'label': backport.text(R.strings.event.hangar.header.shop()),
             'value': VIEW_ALIAS.EVENT_SHOP,
             'tooltip': 'tooltip'})
        self.as_setHangarMenuDataS(menuData)

    def _enableDifficultyBtn(self):
        if not isinstance(self.prbEntity, EventBattleSquadEntity):
            return True
        _, unit = self.prbEntity.getUnit()
        pInfo = self.prbEntity.getPlayerInfo()
        if not unit or not pInfo:
            return True
        return False if unit.isPrebattlesSquad() and unit.getCommanderDBID() != pInfo.dbID else True

    def _getDifficultyLevelTooltipData(self):
        difficultyTooltip = R.strings.event.tooltip.menu.difficulty
        if self._enableDifficultyBtn():
            tooltip = makeTooltip(_ms(backport.text(difficultyTooltip.header())), _ms(backport.text(difficultyTooltip.description())))
        else:
            tooltip = makeTooltip(_ms(backport.text(difficultyTooltip.header_locked())), _ms(backport.text(R.strings.event.tooltip.menu.difficulty.description_locked())))
        return tooltip

    def __updateVisible(self):
        if self.prbDispatcher:
            entity = self.prbDispatcher.getEntity()
            isEventHangar = entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES
            if isEventHangar and not self.__subViewsWithoutHeader and self.__subViewsWithEventHeader:
                self.as_setVisibleS(True)
                self.__updateLobbyHeaderState(HeaderMenuVisibilityState.NOTHING)
            elif self.__subViewsWithoutHeader:
                self.as_setVisibleS(False)
                self.__updateLobbyHeaderState(HeaderMenuVisibilityState.NOTHING)
            else:
                self.as_setVisibleS(False)
                self.__updateLobbyHeaderState(HeaderMenuVisibilityState.ALL)
        return

    def __updateCoins(self):
        shopEnabled = self.gameEventController.getShop().isEnabled()
        self.as_setCoinsS(self.gameEventController.getShop().getCoins() if shopEnabled else 0)

    def __updateTabs(self, event):
        alias = event.alias
        if alias in (VIEW_ALIAS.LOBBY_HANGAR,
         VIEW_ALIAS.EVENT_QUESTS,
         VIEW_ALIAS.EVENT_NOTES,
         VIEW_ALIAS.EVENT_ABOUT,
         VIEW_ALIAS.EVENT_SHOP,
         VIEW_ALIAS.EVENT_DIFFICULTY):
            self._openedViewAlias = alias
        if alias == VIEW_ALIAS.LOBBY_HANGAR and self.prbDispatcher:
            entity = self.prbDispatcher.getEntity()
            isEventHangar = entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES
            if isEventHangar:
                self.as_setScreenS(VIEW_ALIAS.LOBBY_HANGAR)
        return

    def __onCacheResync(self, reason, diff):
        self.__updateHeader()

    def __updateNotesTabCounter(self):
        unreadNotesCnt = self.eventTokenController.getNewNotesCount()
        if unreadNotesCnt > 0:
            self.as_setButtonCounterS(VIEW_ALIAS.EVENT_NOTES, str(unreadNotesCnt))
        else:
            self.as_removeButtonCounterS(VIEW_ALIAS.EVENT_NOTES)

    def __updateLobbyHeaderState(self, state):
        self.fireEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), EVENT_BUS_SCOPE.LOBBY)

    def __updateSelectedDifficultyLevel(self):
        self.as_setDifficultyS(self.gameEventController.getSelectedDifficultyLevel())

    def onUnitPlayerInfoChanged(self, pInfo):
        if isinstance(self.prbEntity, EventBattleSquadEntity) and pInfo.isCommander():
            self.prbEntity.gameEventController.setSquadDifficultyLevel(pInfo.difficultyLevel)
            if not self.prbEntity.isCommander():
                self.prbEntity.gameEventController.setSelectedDifficultyLevel(pInfo.difficultyLevel)
