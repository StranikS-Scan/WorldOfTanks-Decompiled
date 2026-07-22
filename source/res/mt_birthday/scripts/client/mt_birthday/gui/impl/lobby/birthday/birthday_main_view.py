# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/birthday_main_view.py
import typing
import Event
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.framework.managers.optimization_manager import ExternalFullscreenGraphicsOptimizationComponent
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.shared.event_dispatcher import showHangar
from mt_birthday.birthday_constants import BIRTHDAY_GOLDEN_TICKET
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import BirthdayMainViewModel, TabId
from gui.impl.pub import ViewImpl
from helpers import dependency
from mt_birthday.gui.impl.lobby.birthday.all_rewards_view import AllRewardsView
from mt_birthday.gui.impl.lobby.birthday.quests_giver_view import QuestsGiverView
from mt_birthday.gui.impl.lobby.birthday.tank_mail_view import TankMailView
from mt_birthday.gui.impl.lobby.birthday.lootbox_entry_point import LootBoxesEntryPointWidget
from mt_birthday.gui.impl.lobby.birthday.web_browser_view import WebBrowserView, StaticWebBrowserView
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.shared.event_dispatcher import showGoldWagon
from mt_birthday.gui.shared.events import BirthdayEvent
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.impl.sounds import BIRTHDAY_SOUND_SPACE
from mt_birthday.birthday_account_settings import setSettings
from mt_birthday.uilogging.ticket_exchange.loggers import TicketExchangeLogger
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import Sequence, Tuple, Callable, Optional
_logger = logging.getLogger(__name__)

def _createMailView(*_):
    return TankMailView(R.views.mt_birthday.lobby.birthday.TankMailView())


def _createQuestsGiverView(*_):
    return QuestsGiverView(R.views.mt_birthday.lobby.birthday.QuestsGiverView())


def _createAllRewardsView(*_):
    return AllRewardsView(R.views.mt_birthday.lobby.birthday.AllRewardsView())


def _createAboutView(events, *_):
    return StaticWebBrowserView(events, TabId.ABOUT, GUI_SETTINGS.lookup('birthdayInfoPageURL'))


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def _createTicketExchangeView(events, birthdayController=None, *_):
    return WebBrowserView(events, TabId.TICKET_EXCHANGE, birthdayController.getTicketExchangeURL(), skipEscape=False)


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def _createGoldWagonView(events, birthdayController=None, *_):
    return WebBrowserView(events, TabId.GOLD_WAGON, birthdayController.getGoldWagonURL())


_STATIC_CHILD_VIEWS = {TabId.MAIL: (R.views.mt_birthday.lobby.birthday.TankMailView(), _createMailView),
 TabId.QUESTS: (R.views.mt_birthday.lobby.birthday.QuestsGiverView(), _createQuestsGiverView),
 TabId.GOLD_WAGON: (TabId.GOLD_WAGON.value, _createGoldWagonView),
 TabId.TICKET_EXCHANGE: (TabId.TICKET_EXCHANGE.value, _createTicketExchangeView),
 TabId.ABOUT: (TabId.ABOUT.value, _createAboutView)}
_DYNAMIC_CHILD_VIEW = {}

class BirthdayMainViewEvents(object):

    def __init__(self):
        em = Event.EventManager()
        self.onTabChange = Event.Event(em)
        self.__eventManager = em

    def clearEvents(self):
        self.__eventManager.clear()


class BirthdayMainView(ViewImpl):
    __mtBirthday = dependency.descriptor(ITanksBirthdayController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _COMMON_SOUND_SPACE = BIRTHDAY_SOUND_SPACE
    __slots__ = ('__currentTabID', '__events', '__lootboxEntryPoint', '__graphicOptimization', '__ticketExchangeLogger')

    def __init__(self, layoutID, tabId=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BirthdayMainViewModel()
        super(BirthdayMainView, self).__init__(settings)
        self.__currentTabID = tabId if tabId is not None else TabId.MAIL
        self.__events = BirthdayMainViewEvents()
        self.__lootboxEntryPoint = LootBoxesEntryPointWidget(self.viewModel.lootboxEntryPoint)
        self.__graphicOptimization = ExternalFullscreenGraphicsOptimizationComponent()
        self.__ticketExchangeLogger = TicketExchangeLogger()
        self.__logTicketExchangeEnter()
        return

    @property
    def viewModel(self):
        return super(BirthdayMainView, self).getViewModel()

    @property
    def currentTabView(self):
        return _STATIC_CHILD_VIEWS.get(self.__currentTabID, _DYNAMIC_CHILD_VIEW.get(self.__currentTabID))[0]

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.PostStampTooltip():
            return PostStampTooltip()
        subViewTooltip = self.getChildView(self.currentTabView).createToolTipContent(event, contentID)
        return subViewTooltip if subViewTooltip else super(BirthdayMainView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BirthdayMainView, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.getChildView(self.currentTabView).getTooltipData(event)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onTabChange, self.__onTabChange),
         (self.viewModel.onOpenGoldenCarriage, self.__onOpenGoldenCarriage),
         (self.viewModel.onTipsCompleted, self.__onTipsCompleted),
         (self.__mtBirthday.onEventSettingsUpdated, self.__onEventSettingsUpdated),
         (self.__settingsCore.onSettingsChanged, self.__updateTips)) + self.__lootboxEntryPoint.getEvents()

    def _getListeners(self):
        return ((BirthdayEvent.DESTROY_BIRTHDAY_MAIN_VIEW, self.__onClose),)

    def _getCallbacks(self):
        return (('cache.entitlements', self.__onGoldenTicketsBalanceUpdate),)

    def _finalize(self):
        self.__logTicketExchangeExit()
        self.__events.clearEvents()
        self.__events = None
        super(BirthdayMainView, self)._finalize()
        self.__lootboxEntryPoint = None
        self.__graphicOptimization.fini()
        return

    def _onLoading(self, *args, **kwargs):
        super(BirthdayMainView, self)._onLoading(*args, **kwargs)
        self.__updateBrowserViews()
        for _, (resID, viewCreator) in _STATIC_CHILD_VIEWS.iteritems():
            self.setChildView(resID, viewCreator(self.__events, *args, **kwargs))

        self.__switchTab(tabID=self.__currentTabID)
        self.__lootboxEntryPoint.onLoading()
        self.__setGoldenTicketsBalance()
        self.__graphicOptimization.init()

    def __updateBrowserViews(self):
        isGoldWagonEnabled = bool(self.__mtBirthday.getGoldWagonURL())
        isTicketExchangeEnabled = bool(self.__mtBirthday.getTicketExchangeURL())
        self.viewModel.setIsEnabledGoldWagonEntry(isGoldWagonEnabled)
        self.viewModel.setIsEnabledTicketExchangeEntry(isTicketExchangeEnabled)
        if not isGoldWagonEnabled and self.__currentTabID == TabId.GOLD_WAGON or not isTicketExchangeEnabled and self.__currentTabID == TabId.TICKET_EXCHANGE:
            self.__switchTab(TabId.MAIL)

    def __switchTab(self, tabID):
        if tabID in _DYNAMIC_CHILD_VIEW:
            resID, viewCreator = _DYNAMIC_CHILD_VIEW[tabID]
            self.setChildView(resID, viewCreator(self.__events))
        self.__logTicketExchangeExit()
        self.__currentTabID = tabID
        self.__logTicketExchangeEnter()
        self.viewModel.setCurrentTabId(self.__currentTabID)
        self.__updateTips()

    def __updateTips(self, *args):
        self.viewModel.setIsGeneralTipEnabled(not self.__mtBirthday.isGeneralTipCompleted())
        self.viewModel.setIsTipEnabled(not self.__mtBirthday.isTabTipsCompleted(self.__currentTabID))

    def __logTicketExchangeEnter(self):
        if self.__currentTabID == TabId.TICKET_EXCHANGE:
            self.__ticketExchangeLogger.logEnter()

    def __logTicketExchangeExit(self):
        if self.__currentTabID == TabId.TICKET_EXCHANGE:
            self.__ticketExchangeLogger.logExit()

    def __onClose(self, *args, **kwargs):
        self.destroyWindow()
        showHangar()

    def __onOpenGoldenCarriage(self):
        showGoldWagon()

    def __onEventSettingsUpdated(self):
        if not self.__mtBirthday.isEnabled():
            return self.__onClose()
        self.__updateBrowserViews()

    def __setGoldenTicketsBalance(self):
        self.viewModel.setHasGoldenTickets(bool(self.__mtBirthday.getGoldenTicketsCount()))

    def __onGoldenTicketsBalanceUpdate(self, entitlements, *args, **kwargs):
        if entitlements.get(BIRTHDAY_GOLDEN_TICKET, None) is not None:
            self.__setGoldenTicketsBalance()
        return

    def __onTipsCompleted(self, args):
        tabId = args.get('tabId', None)
        accountSettingsPath = self.__mtBirthday.getAccountSettingsTipPathByTabId(tabId)
        if accountSettingsPath:
            setSettings(accountSettingsPath, True)
        else:
            _logger.error('Current tab=%s has no tips to complete', tabId)
        return

    @args2params(int)
    def __onTabChange(self, tabId):
        tId = TabId(tabId)
        if tId == self.__currentTabID:
            return
        else:
            self.__events.onTabChange(self.__currentTabID, tId)
            self.__switchTab(tId)
            if self.__currentTabID in _DYNAMIC_CHILD_VIEW:
                resID, _ = _DYNAMIC_CHILD_VIEW[self.__currentTabID]
                self.setChildView(resID, None)
            return
