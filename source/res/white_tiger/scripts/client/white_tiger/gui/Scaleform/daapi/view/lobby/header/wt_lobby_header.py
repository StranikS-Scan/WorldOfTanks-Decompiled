# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/header/wt_lobby_header.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from messenger.formatters import TimeFormatter
from gui.shared.formatters import text_styles
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger_common.wt_constants import WHITE_TIGER_GAME_PARAMS_KEY
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui import GUI_SETTINGS
from gui.shared import events
from th_async import th_async, AsyncReturn, await_callback
from adisp import adisp_process
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

@adisp_process
def closeEvent(callback=None):
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        if callback is not None:
            callback(False)
        return
    else:
        result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if callback is not None:
            callback(result)
        return


class _WTCloseConfirmatorsHelper(CloseConfirmatorsHelper):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        super(_WTCloseConfirmatorsHelper, self).__init__()
        self.__isStarted = False

    def start(self, *_):
        super(_WTCloseConfirmatorsHelper, self).start(self.__confirmator)
        self.__isStarted = True

    def stop(self):
        super(_WTCloseConfirmatorsHelper, self).stop()
        self.__isStarted = False

    @property
    def isStarted(self):
        return self.__isStarted

    def getRestrictedEvents(self):
        return [events.ViewEventType.LOAD_VIEW, events.ViewEventType.LOAD_GUI_IMPL_VIEW, events.BrowserEvent.BROWSER_CREATED]

    def getRestrictedSfViews(self):
        views = super(_WTCloseConfirmatorsHelper, self).getRestrictedSfViews()
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
         VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB))
        return views

    def getRestrictedGuiImplViews(self):
        views = super(_WTCloseConfirmatorsHelper, self).getRestrictedGuiImplViews()
        views.extend((R.views.lobby.account_dashboard.AccountDashboard(),
         R.views.lobby.offers.OfferGiftsWindow(),
         R.views.lobby.personal_reserves.ReservesActivationView(),
         R.views.lobby.techtree.VehicleTechTree()))
        return views

    def getRestrictedUrls(self):
        return [GUI_SETTINGS.promoscreens]

    @property
    def _isAddHeaderNavigationConfirmator(self):
        return False

    @th_async
    def __confirmator(self):
        result = True
        if self.__wtController.isWtMode():
            result = yield await_callback(closeEvent)()
            if not result:
                self.__wtController.doSelectEventPrb()
        raise AsyncReturn(result)


class WTLobbyHeader(LobbyHeader):
    _wtController = dependency.descriptor(IWhiteTigerController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(WTLobbyHeader, self).__init__()
        self.__closeConfirmatorHelper = _WTCloseConfirmatorsHelper()

    def onPrbEntitySwitched(self):
        self._populateButtons()
        super(WTLobbyHeader, self).onPrbEntitySwitched()

    def _addListeners(self):
        super(WTLobbyHeader, self)._addListeners()
        self._wtController.onLobbyHeaderUpdate += self.__onLobbyHeaderUpdate
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged

    def _removeListeners(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self._wtController.onLobbyHeaderUpdate -= self.__onLobbyHeaderUpdate
        super(WTLobbyHeader, self)._removeListeners()

    def __onLobbyHeaderUpdate(self):
        self._updatePrebattleControls()

    def _updatePrebattleControls(self, *_):
        super(WTLobbyHeader, self)._updatePrebattleControls(*_)
        if self._wtController.isWtMode():
            if not self.__closeConfirmatorHelper.isStarted:
                self.__closeConfirmatorHelper.start()
            if self._wtController.isBanned:
                timeStr = text_styles.yellowText(TimeFormatter.getLongDatetimeFormat(self._wtController.banExpiryTime))
                r = R.strings.white_tiger.hangar.startBtn
                body = backport.text(r.banned.body(), time=timeStr)
                self.as_disableFightButtonS(True)
                self.as_setFightBtnTooltipS(makeTooltip(backport.text(r.banned.header()), body), False)
        elif self.__closeConfirmatorHelper.isStarted:
            self.__closeConfirmatorHelper.stop()

    def __onSettingsChanged(self, diff):
        if WHITE_TIGER_GAME_PARAMS_KEY not in diff:
            return
        self._updatePrebattleControls()
