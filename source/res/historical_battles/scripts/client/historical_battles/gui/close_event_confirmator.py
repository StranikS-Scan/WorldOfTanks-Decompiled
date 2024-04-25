# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/close_event_confirmator.py
from BWUtil import AsyncReturn
from wg_async import wg_async, await_callback
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.impl.gen import R
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.events import ViewEventType
from helpers import dependency
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
from historical_battles.gui.shared.event_dispatcher import showHBHangar
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui import SystemMessages
from gui.prb_control.dispatcher import g_prbLoader

class CloseEventConfirmator(CloseConfirmatorsHelper):
    ADD_HEADER_NAV_CONFIRMATOR = False
    _gameEventController = dependency.descriptor(IGameEventController)

    def start(self, *_):
        super(CloseEventConfirmator, self).start(self.__confirmator)

    def getRestrictedEvents(self):
        return [ViewEventType.LOAD_VIEW, ViewEventType.LOAD_GUI_IMPL_VIEW]

    def getRestrictedSfViews(self):
        views = super(CloseEventConfirmator, self).getRestrictedSfViews()
        views.extend((VIEW_ALIAS.BATTLE_RESULTS,
         VIEW_ALIAS.LOBBY_CUSTOMIZATION,
         VIEW_ALIAS.LOBBY_STORAGE,
         VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
         VIEW_ALIAS.LOBBY_TECHTREE,
         VIEW_ALIAS.LOBBY_STRONGHOLD,
         VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW,
         VIEW_ALIAS.STYLE_PREVIEW,
         VIEW_ALIAS.HERO_VEHICLE_PREVIEW,
         VIEW_ALIAS.VEH_POST_PROGRESSION,
         VIEW_ALIAS.AMMUNITION_SETUP_VIEW,
         FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS))
        return views

    def getRestrictedGuiImplViews(self):
        views = super(CloseEventConfirmator, self).getRestrictedGuiImplViews()
        views.extend((R.views.lobby.account_dashboard.AccountDashboard(),
         R.views.lobby.offers.OfferGiftsWindow(),
         R.views.lobby.personal_reserves.ReservesActivationView(),
         R.views.lobby.crystalsPromo.CrystalsPromoView(),
         R.views.lobby.crew.BarracksView()))
        return views

    @wg_async
    def __confirmator(self):
        result = True
        if self._gameEventController.isHistoricalBattlesMode() and self._gameEventController.isEnabled():
            prbDispatcher = g_prbLoader.getDispatcher()
            if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
                SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
                raise AsyncReturn(result)
            result = yield await_callback(closeEvent)()
            if not result and not isViewLoaded(R.views.historical_battles.lobby.HangarView()):
                showHBHangar()
        raise AsyncReturn(result)
        return
