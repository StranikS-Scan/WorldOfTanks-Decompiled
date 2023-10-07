# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/auxiliary/close_event_confirmator.py
from BWUtil import AsyncReturn
from gui.shared import events
from wg_async import wg_async, await_callback
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.impl.gen import R
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from helpers import dependency
from halloween.gui.impl.lobby.hw_helpers.hangar_helpers import closeEvent
from gui import GUI_SETTINGS
from skeletons.gui.game_control import IHalloweenController

class CloseEventConfirmator(CloseConfirmatorsHelper):
    eventBattlesController = dependency.descriptor(IHalloweenController)
    ADD_HEADER_NAV_CONFIRMATOR = False

    def __init__(self):
        super(CloseEventConfirmator, self).__init__()
        self.__isStarted = False

    def start(self, *_):
        super(CloseEventConfirmator, self).start(self.__confirmator)
        self.__isStarted = True

    def stop(self):
        super(CloseEventConfirmator, self).stop()
        self.__isStarted = False

    @property
    def isStarted(self):
        return self.__isStarted

    def getRestrictedEvents(self):
        return [events.ViewEventType.LOAD_VIEW, events.ViewEventType.LOAD_GUI_IMPL_VIEW, events.BrowserEvent.BROWSER_CREATED]

    def getRestrictedSfViews(self):
        views = super(CloseEventConfirmator, self).getRestrictedSfViews()
        views.extend((VIEW_ALIAS.BATTLE_RESULTS,
         VIEW_ALIAS.LOBBY_STORAGE,
         VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
         VIEW_ALIAS.LOBBY_TECHTREE,
         VIEW_ALIAS.LOBBY_STRONGHOLD,
         VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW,
         VIEW_ALIAS.STYLE_PREVIEW,
         VIEW_ALIAS.VEH_POST_PROGRESSION,
         VIEW_ALIAS.WIKI_VIEW,
         VIEW_ALIAS.MANUAL_CHAPTER_VIEW,
         VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB,
         FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS))
        return views

    def getRestrictedGuiImplViews(self):
        views = super(CloseEventConfirmator, self).getRestrictedGuiImplViews()
        views.extend((R.views.lobby.account_dashboard.AccountDashboard(), R.views.lobby.offers.OfferGiftsWindow(), R.views.lobby.personal_reserves.ReservesActivationView()))
        return views

    def getRestrictedUrls(self):
        return [GUI_SETTINGS.promoscreens]

    @property
    def _isAddHeaderNavigationConfirmator(self):
        return False

    @wg_async
    def __confirmator(self):
        result = True
        if self.eventBattlesController.isEventPrbActive():
            result = yield await_callback(closeEvent)()
            if not result:
                self.eventBattlesController.selectEventBattle()
        raise AsyncReturn(result)
