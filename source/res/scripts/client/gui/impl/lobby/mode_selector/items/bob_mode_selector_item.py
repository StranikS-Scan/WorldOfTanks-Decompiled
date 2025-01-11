# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/bob_mode_selector_item.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController, IMarathonEventsController
from gui.marathon.bob_event import BobEvent, BobEventAddUrl
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.prb_control.dispatcher import g_prbLoader
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import time_formatters

class BobModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('__currentSeason',)
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.BOB
    __bobCtrl = dependency.descriptor(IBobController)
    __marathonCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self, oldSelectorItem):
        super(BobModeSelectorItem, self).__init__(oldSelectorItem)
        self.__currentSeason = None
        return

    def _getIsDisabled(self):
        return not self.__bobCtrl.isEnabled() or self.__bobCtrl.isPaused()

    @property
    def isSelectable(self):
        return self.__bobCtrl.isRegistered()

    def handleClick(self):
        if not self.__bobCtrl.isRegistered():
            bobEvent = self.__marathonCtrl.getMarathon(BobEvent.BOB_EVENT_PREFIX)
            bobEvent.setAdditionalUrl(BobEventAddUrl.REGISTRATION)
            showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)
            self.__reloadMarathonPage()
        elif self.__isPlayerInBobMode():
            showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)
            self.__reloadMarathonPage()

    def _isInfoIconVisible(self):
        return True

    def __isPlayerInBobMode(self):
        dispatcher = g_prbLoader.getDispatcher()
        state = dispatcher.getFunctionalState()
        return state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)

    def handleInfoPageClick(self):
        bobEvent = self.__marathonCtrl.getMarathon(BobEvent.BOB_EVENT_PREFIX)
        bobEvent.setAdditionalUrl(BobEventAddUrl.INFO)
        showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(R.views.lobby.mode_selector.ModeSelectorView()))
        self.__reloadMarathonPage()

    def __reloadMarathonPage(self):
        g_eventBus.handleEvent(events.MissionsEvent(events.MissionsEvent.RELOAD_TAB_CONTEXT, ctx={}), EVENT_BUS_SCOPE.LOBBY)

    @property
    def calendarTooltipText(self):
        return backport.text(R.strings.bob.selector.tooltip.body(), day=self.__getCurrentSeasonDate())

    def __getCurrentSeasonDate(self):
        currentSeason = self.__bobCtrl.getCurrentSeason()
        return self.__getDate(currentSeason.getEndDate()) if currentSeason is not None else ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)

    def _onInitializing(self):
        super(BobModeSelectorItem, self)._onInitializing()
        self.__updateBobData()

    def __updateBobData(self):
        self.__currentSeason = self.__bobCtrl.getCurrentSeason()
        self.__fillViewModel()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getSeasonTimeLeft())
            self._addReward(ModeSelectorRewardID.PROGRESSION_STYLE)
            self._addReward(ModeSelectorRewardID.CREW)

    def __getSeasonTimeLeft(self):
        return time_formatters.getTillTimeByResource(max(0, self.__currentSeason.getEndDate() - time_utils.getServerUTCTime()), R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True) if self.__currentSeason is not None else ''
