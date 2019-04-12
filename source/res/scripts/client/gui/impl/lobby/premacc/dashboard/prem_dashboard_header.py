# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_header.py
import BigWorld
from frameworks.wulf import ViewFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import shouldOpenNewStorage
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.clans.settings import getClanRoleName
from gui.goodies.goodie_items import MAX_ACTIVE_BOOSTERS_COUNT
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_model import PremDashboardHeaderModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_tooltips import PremDashboardHeaderTooltips
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_reserve_model import PremDashboardHeaderReserveModel
from gui.impl.lobby.tooltips.clans import ClanShortInfoTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.web import IWebController
from skeletons.gui.game_control import IBadgesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.goodies import IGoodiesCache

class PremDashboardHeader(ViewImpl):
    __slots__ = ()
    __webCtrl = dependency.descriptor(IWebController)
    __badgesController = dependency.descriptor(IBadgesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, *args, **kwargs):
        super(PremDashboardHeader, self).__init__(R.views.premDashboardHeader(), ViewFlags.VIEW, PremDashboardHeaderModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(PremDashboardHeader, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(PremDashboardHeader, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return ClanShortInfoTooltipContent() if contentID == R.views.clanShortInfoTooltipContent() else super(PremDashboardHeader, self).createToolTipContent(event=event, contentID=contentID)

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
            self.__buildPersonalReservesList(model.personalReserves)
            model.setHasClanReserves(False)
            self.__updateBadges(model=model)

    def _finalize(self):
        super(PremDashboardHeader, self)._finalize()
        self.viewModel.onShowBadges -= self.__onShowBadges
        self.viewModel.personalReserves.onUserItemClicked -= self.__onPersonalReserveClick
        self.viewModel.clanReserves.onUserItemClicked -= self.__onClanReserveClick
        self.__clearListeners()

    def __initListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged,
         'goodies': self.__onGoodiesUpdated})
        self.__badgesController.onUpdated += self.__updateBadges

    def __clearListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__badgesController.onUpdated -= self.__updateBadges

    def __onClanInfoChanged(self, _):
        self.__updateClanInfo(self.viewModel)

    def __onGoodiesUpdated(self, *_):
        self.__buildPersonalReservesList(self.viewModel.personalReserves)

    def __updateClanInfo(self, model):
        clanProfile = self.__webCtrl.getAccountProfile()
        isInClan = clanProfile.isInClan()
        model.setIsInClan(isInClan)
        if isInClan:
            clanInfoModel = model.clanInfo
            clanAbbrev = clanProfile.getClanAbbrev()
            model.userName.setClanAbbrev(clanAbbrev)
            clanInfoModel.setClanAbbrev(clanAbbrev)
            clanInfoModel.setRoleInClan(getClanRoleName(clanProfile.getRole()) or '')

    def __buildPersonalReservesList(self, listModel):
        listItems = listModel.getItems()
        if listItems:
            listItems.clear()
        activeBoosters = self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)
        activeBoostersList = sorted(activeBoosters.values(), key=lambda b: b.getUsageLeftTime(), reverse=True)
        activeBoostersCount = len(activeBoostersList)
        for idx in range(MAX_ACTIVE_BOOSTERS_COUNT):
            itemModel = PremDashboardHeaderReserveModel()
            if idx < activeBoostersCount:
                booster = activeBoostersList[idx]
                itemModel.setId(booster.boosterID)
                itemModel.setProgress(booster.getCooldownAsPercent())
                itemModel.setTimeleft(booster.getUsageLeftTime())
                itemModel.setIconId(booster.boosterGuiType)
            listModel.addViewModel(itemModel)

        listModel.invalidate()

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipType')
        if tooltipType == PremDashboardHeaderTooltips.TOOLTIP_PERSONAL_RESERVE:
            reserveId = event.getArgument('id')
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, specialArgs=(reserveId,))

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
        event_dispatcher.showBadges()

    @staticmethod
    def __onPersonalReserveClick(item):
        if item.getId() < 0:
            if shouldOpenNewStorage():
                event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.PERSONAL_RESERVES)
            else:
                g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __onClanReserveClick(item):
        pass
