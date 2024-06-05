# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/achievements_main_view.py
import weakref
from functools import partial
import typing
from collections import namedtuple
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements_main_view_model import AchievementsViews, AchievementsMainViewModel
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.pub import ViewImpl
from helpers import uniprof
if typing.TYPE_CHECKING:
    from typing import Dict
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', AchievementsViews), ('presenter', SubModelPresenter), ('canBeLoaded', typing.Optional[typing.Callable[[], bool]])])
AchievementsViewCtx = namedtuple('AchievementsViewCtx', ('menuName', 'userID', 'closeCallback'))

class AchievementMainView(ViewImpl):
    __slots__ = ('__ctx', '__contentPresentersMap', '__regionName')

    def __init__(self, ctx, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.achievements.AchievementsMainView())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = AchievementsMainViewModel()
        self.__ctx = ctx
        self.__contentPresentersMap = {}
        self.__regionName = None
        super(AchievementMainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentPresenter(self):
        return self.__contentPresentersMap[self.__ctx.menuName].presenter

    def createToolTipContent(self, event, contentID):
        return self.currentPresenter.createToolTipContent(event, contentID)

    def createToolTip(self, event):
        return self.currentPresenter.createToolTip(event) or super(AchievementMainView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(AchievementMainView, self)._onLoading(args, kwargs)
        self.__registerSubModels()
        self.__switchSubView(self.__ctx)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _getListeners(self):
        return ((events.Achievements20Event.CHANGE_GF_VIEW, self.__switchSubViewEventHandler, EVENT_BUS_SCOPE.LOBBY),)

    def _finalize(self):
        self.currentPresenter.finalize()
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
            self.__regionName = None
        for subModelInfo in self.__contentPresentersMap.itervalues():
            subModelInfo.presenter.clear()

        self.__contentPresentersMap.clear()
        self.__contentPresentersMap = None
        if self.__ctx and self.__ctx.closeCallback:
            self.__ctx.closeCallback()
        self.__ctx = None
        super(AchievementMainView, self)._finalize()
        return

    def __registerSubModels(self):
        self.__contentPresentersMap = _PresentersMap(self, self.__ctx.userID)

    def __switchSubViewEventHandler(self, event):
        if event.ctx.userID != self.__ctx.userID or self.__regionName == event.ctx.menuName:
            return
        self.__switchSubView(event.ctx)

    def __switchSubView(self, ctx):
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
        self.__regionName = ctx.menuName
        uniprof.enterToRegion(self.__regionName)
        subModelInfo = self.__contentPresentersMap[ctx.menuName]
        if subModelInfo.canBeLoaded is not None and not subModelInfo.canBeLoaded():
            return
        else:
            if self.currentPresenter.isLoaded:
                self.currentPresenter.finalize()
            with self.viewModel.transaction() as tx:
                subModelInfo.presenter.initialize()
                tx.setViewType(subModelInfo.ID)
                tx.setIsOtherPlayer(ctx.userID is not None)
            self.__ctx = ctx
            return

    def __onClose(self):
        if self.__ctx.userID is None:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            g_eventBus.handleEvent(events.Achievements20Event(events.Achievements20Event.CLOSE_SUMMARY_VIEW, {'databaseID': self.__ctx.userID}), scope=EVENT_BUS_SCOPE.LOBBY)
        return


class _PresentersMap(object):

    def __init__(self, mainView, userId):
        self.__presentersCache = {}
        self.__mainView = weakref.proxy(mainView)
        self.__userId = userId
        self.__loadersMap = {VIEW_ALIAS.PROFILE_TOTAL_PAGE: partial(self.__makeSubModel, AchievementsViews.SUMMARY, self.__loadSummary),
         VIEW_ALIAS.PROFILE_ACHIEVEMENTS_PAGE: partial(self.__makeSubModel, AchievementsViews.ACHIEVEMENTS, self.__loadAchievements)}

    def itervalues(self):
        return self.__presentersCache.itervalues()

    def clear(self):
        self.__loadersMap = {}
        self.__presentersCache = {}
        self.__mainView = None
        return

    def __getitem__(self, item):
        if item not in self.__presentersCache:
            self.__tryToLoadPresenter(item)
        return self.__presentersCache.get(item, None)

    def __tryToLoadPresenter(self, key):
        if key in self.__loadersMap:
            self.__presentersCache[key] = self.__loadersMap[key]()

    def __loadSummary(self):
        from gui.impl.lobby.achievements.summary.summary_view import SummaryView
        return SummaryView(self.__mainView.viewModel.summaryModel, self.__mainView, self.__userId)

    def __loadAchievements(self):
        from gui.impl.lobby.achievements.achievements.advanced_achievements_view import AdvancedAchievementsView
        return AdvancedAchievementsView(self.__mainView.viewModel.achievementsModel, self.__mainView, self.__userId)

    @staticmethod
    def __makeSubModel(viewAlias, loader, customPredicate=None):
        return _SubModelInfo(viewAlias, loader(), customPredicate)
