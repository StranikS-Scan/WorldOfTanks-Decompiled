# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_header.py
import typing
import BigWorld
from frameworks.wulf import ViewFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import shouldOpenNewStorage
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.clans.clan_helpers import getStrongholdClanCardUrl
from gui.clans.settings import getClanRoleName
from gui.goodies.goodie_items import MAX_ACTIVE_BOOSTERS_COUNT
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_model import PremDashboardHeaderModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_tooltips import PremDashboardHeaderTooltips
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_reserve_model import PremDashboardHeaderReserveModel
from gui.impl.lobby.tooltips.clans import ClanShortInfoTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStrongholds
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.web import IWebController
from skeletons.gui.game_control import IBadgesController, IBoostersController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.goodies import IGoodiesCache
if typing.TYPE_CHECKING:
    from gui.clans.clan_account_profile import ClanAccountProfile

class PremDashboardHeader(ViewImpl):
    __slots__ = ()
    __webCtrl = dependency.descriptor(IWebController)
    __badgesController = dependency.descriptor(IBadgesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __boosters = dependency.descriptor(IBoostersController)
    __MAX_VIEWABLE_CLAN_RESERVES_COUNT = 2
    __TOOLTIPS_MAPPING = {PremDashboardHeaderTooltips.TOOLTIP_PERSONAL_RESERVE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
     PremDashboardHeaderTooltips.TOOLTIP_CLAN_RESERVE: TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO}

    def __init__(self, *args, **kwargs):
        super(PremDashboardHeader, self).__init__(R.views.lobby.premacc.dashboard.prem_dashboard_header.PremDashboardHeader(), ViewFlags.VIEW, PremDashboardHeaderModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(PremDashboardHeader, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(PremDashboardHeader, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return ClanShortInfoTooltipContent() if contentID == R.views.lobby.tooltips.clans.ClanShortInfoTooltipContent() else super(PremDashboardHeader, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, *args, **kwargs):
        super(PremDashboardHeader, self)._initialize(*args, **kwargs)
        self.__initListeners()
        self.viewModel.onShowBadges += self.__onShowBadges
        self.viewModel.personalReserves.onUserItemClicked += self.__onPersonalReserveClick
        self.viewModel.clanReserves.onUserItemClicked += self.__onClanReserveClick
        with self.viewModel.transaction() as model:
            userNameModel = model.userName
            userNameModel.setUserName(BigWorld.player().name)
            userNameModel.setIsTeamKiller(self.__itemsCache.items.stats.isTeamKiller)
            self.__updateClanInfo(model)
            self.__buildPersonalReservesList(model=model)
            self.__updateBadges(model=model)

    def _finalize(self):
        super(PremDashboardHeader, self)._finalize()
        self.viewModel.onShowBadges -= self.__onShowBadges
        self.viewModel.personalReserves.onUserItemClicked -= self.__onPersonalReserveClick
        self.viewModel.clanReserves.onUserItemClicked -= self.__onClanReserveClick
        self.__clearListeners()

    def __initListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged,
         'goodies': self.__onGoodiesUpdated,
         'cache.activeOrders': self.__onClanInfoChanged})
        self.__badgesController.onUpdated += self.__updateBadges
        self.__boosters.onBoosterChangeNotify += self.__onBoosterChangeNotify
        self.__boosters.onReserveTimerTick += self.__buildClanReservesList

    def __clearListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__badgesController.onUpdated -= self.__updateBadges
        self.__boosters.onBoosterChangeNotify -= self.__onBoosterChangeNotify
        self.__boosters.onReserveTimerTick -= self.__buildClanReservesList

    def __onClanInfoChanged(self, _):
        self.__updateClanInfo(self.viewModel)

    def __onGoodiesUpdated(self, *_):
        self.__buildPersonalReservesList()
        self.__buildClanReservesList()

    def __onBoosterChangeNotify(self, *_):
        self.__buildPersonalReservesList()

    def __updateClanInfo(self, model):
        clanProfile = self.__getAccountProfile()
        isInClan = clanProfile.isInClan()
        model.setIsInClan(isInClan)
        if isInClan:
            clanInfoModel = model.clanInfo
            clanAbbrev = clanProfile.getClanAbbrev()
            model.userName.setClanAbbrev(clanAbbrev)
            clanInfoModel.setClanAbbrev(clanAbbrev)
            clanInfoModel.setRoleInClan(getClanRoleName(clanProfile.getRole()) or '')
            self.__buildClanReservesList(model=model)

    @replaceNoneKwargsModel
    def __buildPersonalReservesList(self, _=None, model=None):
        listModel = model.personalReserves
        listModel.clearItems()
        activeBoosters = self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)
        activeBoostersList = sorted(activeBoosters.values(), key=lambda b: b.getUsageLeftTime(), reverse=True)
        for idx in range(MAX_ACTIVE_BOOSTERS_COUNT):
            itemModel = self.__makeReserveModel(activeBoostersList, idx)
            listModel.addViewModel(itemModel)

        listModel.invalidate()

    @replaceNoneKwargsModel
    def __buildClanReservesList(self, _=None, model=None):
        clanProfile = self.__getAccountProfile()
        mayActivate = clanProfile.getMyClanPermissions().canActivateReserves()
        activeReserves = sorted(self.__goodiesCache.getClanReserves().values(), key=lambda r: r.finishTime)
        showSection = mayActivate or activeReserves
        model.setHasClanReserves(bool(showSection))
        if showSection:
            listModel = model.clanReserves
            listItems = listModel.getItems()
            if listItems:
                listItems.clear()
            if mayActivate:
                slotsCount = self.__MAX_VIEWABLE_CLAN_RESERVES_COUNT
            else:
                slotsCount = min(len(activeReserves), self.__MAX_VIEWABLE_CLAN_RESERVES_COUNT)
            for idx in range(slotsCount):
                itemModel = self.__makeReserveModel(activeReserves, idx)
                listModel.addViewModel(itemModel)

            listModel.invalidate()

    def __getAccountProfile(self):
        return self.__webCtrl.getAccountProfile()

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipType')
        tooltipAlias = self.__TOOLTIPS_MAPPING.get(tooltipType)
        if tooltipAlias:
            reserveId = event.getArgument('id')
            return backport.createTooltipData(isSpecial=True, specialAlias=tooltipAlias, specialArgs=(reserveId,))

    @replaceNoneKwargsModel
    def __updateBadges(self, model=None):
        self.__setBadge(model.setPrefixBadgeId, self.__badgesController.getPrefix())
        self.__setBadge(model.setSuffixBadgeId, self.__badgesController.getSuffix())

    @staticmethod
    def __setBadge(setter, badge):
        setter(str(badge.badgeID) if badge is not None and badge.isSelected else '')
        return

    @staticmethod
    def __onShowBadges():
        event_dispatcher.showBadges(backViewName=backport.text(R.strings.badge.badgesPage.header.backBtn.descrLabel()))

    @staticmethod
    def __onPersonalReserveClick(item):
        if shouldOpenNewStorage():
            event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.PERSONAL_RESERVES)
        else:
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __onClanReserveClick(item):
        showStrongholds(getStrongholdClanCardUrl())

    @staticmethod
    def __makeReserveModel(reserves, idx):
        itemModel = PremDashboardHeaderReserveModel()
        if idx < len(reserves):
            booster = reserves[idx]
            itemModel.setId(booster.boosterID)
            itemModel.setProgress(booster.getCooldownAsPercent())
            itemModel.setTimeleft(booster.getUsageLeftTime())
            itemModel.setIconId(booster.boosterGuiType)
        return itemModel
