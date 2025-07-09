# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/birthday_main_view.py
import typing
import Event
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.managers.optimization_manager import ExternalFullscreenGraphicsOptimizationComponent
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.shared.event_dispatcher import showHangar
from gui.server_events.events_helpers import isIngameBrowserEventEnable
from mt_birthday.birthday_account_settings import isIntroSeen, seenIntro
from mt_birthday.birthday_constants import BIRTHDAY_2025_GOLDEN_TICKET
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import BirthdayMainViewModel, TabId
from gui.impl.pub import ViewImpl
from helpers import dependency
from mt_birthday.gui.impl.lobby.birthday.about_view import createAboutView
from mt_birthday.gui.impl.lobby.birthday.all_rewards_view import AllRewardsView
from mt_birthday.gui.impl.lobby.birthday.tank_mail_view import TankMailView
from mt_birthday.gui.impl.lobby.birthday.lootbox_entry_point import LootBoxesEntryPointWidget
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.impl.sounds import BirthdaySoundEvents
from mt_birthday.gui.shared.event_dispatcher import showGoldWagonTankMail
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
if typing.TYPE_CHECKING:
    from typing import Sequence, Tuple, Callable, Optional

def _createMailView(*_):
    return TankMailView(R.views.mt_birthday.lobby.birthday.TankMailView())


def _createAllRewardsView(*_):
    return AllRewardsView(R.views.mt_birthday.lobby.birthday.AllRewardsView())


_STATIC_CHILD_VIEWS = {TabId.MAIL: (R.views.mt_birthday.lobby.birthday.TankMailView(), _createMailView),
 TabId.REWARDS: (R.views.mt_birthday.lobby.birthday.AllRewardsView(), _createAllRewardsView),
 TabId.ABOUT: (TabId.ABOUT.value, createAboutView)}
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
    __slots__ = ('__currentTabID', '__events', '__lootboxEntryPoint', '__graphicOptimization')

    def __init__(self, layoutID, tabId=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BirthdayMainViewModel()
        super(BirthdayMainView, self).__init__(settings)
        self.__currentTabID = tabId if tabId is not None else TabId.MAIL
        self.__events = BirthdayMainViewEvents()
        self.__lootboxEntryPoint = LootBoxesEntryPointWidget(self.viewModel.lootboxEntryPoint)
        self.__graphicOptimization = ExternalFullscreenGraphicsOptimizationComponent()
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
         (self.__mtBirthday.onEventSettingsUpdated, self.__onEventSettingsUpdated)) + self.__lootboxEntryPoint.getEvents()

    def _getCallbacks(self):
        return (('cache.entitlements', self.__onGoldenTicketsBalanceUpdate),)

    def _finalize(self):
        self.__events.clearEvents()
        self.__events = None
        super(BirthdayMainView, self)._finalize()
        self.__lootboxEntryPoint = None
        self.__graphicOptimization.fini()
        self.__setStateHangarSound(False)
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.MAIN_VIEW_EXIT)
        return

    def _onLoading(self, *args, **kwargs):
        super(BirthdayMainView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsIntroSeen(isIntroSeen())
        self.viewModel.setIsEnabledGoldWagonEntry(isIngameBrowserEventEnable())
        for _, (resID, viewCreator) in _STATIC_CHILD_VIEWS.iteritems():
            self.setChildView(resID, viewCreator(self.__events, *args, **kwargs))

        self.__switchTab(tabID=self.__currentTabID)
        self.__lootboxEntryPoint.onLoading()
        self.__setGoldenTicketsBalance()
        self.__graphicOptimization.init()
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.MAIN_VIEW_ENTER)

    def _onLoaded(self, *args, **kwargs):
        super(BirthdayMainView, self)._onLoaded(*args, **kwargs)
        if not self.viewModel.getIsIntroSeen():
            seenIntro()

    def __switchTab(self, tabID):
        if tabID in _DYNAMIC_CHILD_VIEW:
            resID, viewCreator = _DYNAMIC_CHILD_VIEW[tabID]
            self.setChildView(resID, viewCreator(self.__events))
        if tabID == TabId.ABOUT:
            self.__setStateHangarSound(True)
        else:
            self.__setStateHangarSound(False)
        self.__currentTabID = tabID
        self.viewModel.setCurrentTabId(self.__currentTabID)

    def __setStateHangarSound(self, state):
        if state:
            self.soundManager.setState(BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL, BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_ON)
        else:
            self.soundManager.setState(BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL, BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_OFF)

    def __onClose(self):
        self.destroyWindow()
        showHangar()

    def __onOpenGoldenCarriage(self):
        showGoldWagonTankMail()

    def __onEventSettingsUpdated(self):
        if not self.__mtBirthday.isEnabled():
            self.__onClose()

    def __setGoldenTicketsBalance(self):
        self.viewModel.setHasGoldenTickets(bool(self.__mtBirthday.getGoldenTicketsCount()))

    def __onGoldenTicketsBalanceUpdate(self, entitlements, *args, **kwargs):
        if entitlements.get(BIRTHDAY_2025_GOLDEN_TICKET, None) is not None:
            self.__setGoldenTicketsBalance()
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
