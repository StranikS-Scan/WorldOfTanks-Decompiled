# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/se20_banner.py
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SECRET_EVENT_2020_SEEN, SECRET_EVENT_BERLIN_2020_SEEN
from adisp import process
from constants import EPIC_PERF_GROUP
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.SE20BannerMeta import SE20BannerMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class SE20Banner(SE20BannerMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _SHOW_DELAY = 2

    def __init__(self):
        super(SE20Banner, self).__init__()
        self.__showEventBannerCallbackID = None
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onClick(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)

    def _populate(self):
        super(SE20Banner, self)._populate()
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(LobbySimpleEvent.WAITING_HIDDEN, self.__onWaitingHidden, EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.getEnergy().onEnergyChanged += self.__updateEvent
        self.eventsCache.onSyncCompleted += self.__updateEvent
        self.__updateEvent()

    def _dispose(self):
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LobbySimpleEvent.WAITING_HIDDEN, self.__onWaitingHidden, EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.getEnergy().onEnergyChanged -= self.__updateEvent
        self.eventsCache.onSyncCompleted -= self.__updateEvent
        self.__cancelShowEventTimer()
        super(SE20Banner, self)._dispose()

    def __updateEvent(self):
        if self.eventsCache.isEventEnabled():
            isAssault = self.gameEventController.isBerlinStarted()
            showNovelty = not isAssault and not AccountSettings.getCounters(SECRET_EVENT_2020_SEEN) or isAssault and not AccountSettings.getCounters(SECRET_EVENT_BERLIN_2020_SEEN)
            certificates = sum((item.getEnergiesCount() for item in self.gameEventController.getCommanders().itervalues()))
            self.as_setDataS({'tooltip': '',
             'isSpecial': False,
             'specialArgs': [],
             'specialAlias': TOOLTIPS_CONSTANTS.EVENT_BANNER_INFO,
             'fuel': certificates,
             'isAssault': isAssault,
             'showNew': showNovelty})
            if not Waiting.isVisible():
                self.__showEventBanner()
        else:
            self.__cancelShowEventTimer()

    def __cancelShowEventTimer(self):
        if self.__showEventBannerCallbackID is not None:
            BigWorld.cancelCallback(self.__showEventBannerCallbackID)
            self.__showEventBannerCallbackID = None
        return

    def __showEventBanner(self):
        if self.gameEventController.wasBannerAnimationShown:
            isAnimated = self.epicController.getPerformanceGroup() != EPIC_PERF_GROUP.HIGH_RISK
            self.as_showS(False, isAnimated)
        elif self.__showEventBannerCallbackID is None:
            self.__showEventBannerCallbackID = BigWorld.callback(self._SHOW_DELAY, self.__doShowEventBanner)
        return

    def __doShowEventBanner(self):
        self.__showEventBannerCallbackID = None
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LobbySimpleEvent.WAITING_HIDDEN, self.__onWaitingHidden, EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.setBannerAnimationAsShown()
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.PLAY_SE20_BANNER_SOUND), scope=EVENT_BUS_SCOPE.LOBBY)
        isAnimated = self.epicController.getPerformanceGroup() != EPIC_PERF_GROUP.HIGH_RISK
        self.as_showS(True, isAnimated)
        return

    def __onWaitingShown(self, _):
        self.__cancelShowEventTimer()

    def __onWaitingHidden(self, _):
        if self.eventsCache.isEventEnabled():
            self.__showEventBanner()

    @process
    def __doSelectAction(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
