# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/earning_pop_up_view.py
from collections import deque
from functools import partial
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EarningPopUpViewMeta import EarningPopUpViewMeta
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.impl.gen import R
from gui.impl.lobby.achievements.profile_utils import fillAdvancedAchievementModel, createAdvancedAchievementsCatalogInitAchievementIDs
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements_earning_view_model import AchievementsEarningViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showAdvancedAchievementsCatalogView, showAdvancedAchievementsView, showTrophiesView
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IAchievementsController
from tutorial.control.context import GLOBAL_FLAG
from uilogging.advanced_achievement.logger import AdvancedAchievementEarningLogger
from uilogging.advanced_achievement.logging_constants import AdvancedAchievementViewKey, AdvancedAchievementKeys

class EarningPopUpView(EarningPopUpViewMeta):

    def __init__(self):
        super(EarningPopUpView, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self):
        self.__view = _EarningPopUpView()
        return self.__view


class _NonOverlappingViewsLifecycleHandler(IViewLifecycleHandler):
    __NON_OVERLAPPING_VIEWS = (VIEW_ALIAS.BATTLE_QUEUE,)

    def __init__(self, stopAnimationCallback):
        super(_NonOverlappingViewsLifecycleHandler, self).__init__([ ViewKey(alias) for alias in self.__NON_OVERLAPPING_VIEWS ])
        self.__stopAnimationCallback = stopAnimationCallback

    def onViewCreated(self, view):
        self.__stopAnimationCallback()


class _EarningPopUpView(ViewImpl):
    __appLoader = dependency.descriptor(IAppLoader)
    __achievementsController = dependency.descriptor(IAchievementsController)
    __slots__ = ('__achievementQueue', '__uiLogging', '__viewLifecycleWatcher')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.achievements.EarningPopUpView())
        settings.flags = ViewFlags.VIEW
        settings.args = args
        settings.kwargs = kwargs
        settings.model = AchievementsEarningViewModel()
        self.__achievementQueue = deque()
        self.__uiLogging = AdvancedAchievementEarningLogger()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        super(_EarningPopUpView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getListeners(self):
        return ((events.Achievements20Event.ACHIEVEMENT_EARNED, self.__achEarnedEventHandler, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.viewModel.onShown, self.__onShown), (self.viewModel.onGoToAchievement, self.__onGoToAchievement))

    def _initialize(self, *args, **kwargs):
        super(_EarningPopUpView, self)._initialize(*args, **kwargs)
        handler = _NonOverlappingViewsLifecycleHandler(stopAnimationCallback=self.__onStopAnimation)
        self.__viewLifecycleWatcher.start(self.__appLoader.getApp().containerManager, [handler])

    def _finalize(self):
        self.__viewLifecycleWatcher.stop()
        super(_EarningPopUpView, self)._finalize()

    def __achEarnedEventHandler(self, event):
        data = event.ctx.get('data')
        if self.viewModel.getIsAnimationPlaying():
            self.__achievementQueue.append(data)
        else:
            self.__startAnimation(data)

    def __onStopAnimation(self):
        self.__achievementQueue.clear()
        if self.viewModel.getIsAnimationPlaying():
            self.__onShown()

    def __startAnimation(self, data):
        achievements = sorted(data, key=lambda achievement: (not achievement.isDeprecated, achievement.getScore()), reverse=True)
        self.__uiLogging.onViewOpen(AdvancedAchievementViewKey.EARNING)
        with self.viewModel.transaction() as model:
            achievementsModel = model.getAchievements()
            achievementsModel.clear()
            for achievement in achievements:
                achievementsModel.addViewModel(fillAdvancedAchievementModel(achievement))

            achievementsModel.invalidate()
            model.setIsAnimationPlaying(True)

    def __onShown(self):
        self.viewModel.setIsAnimationPlaying(False)
        if self.__achievementQueue:
            self.__startAnimation(self.__achievementQueue.popleft())
        else:
            g_eventBus.handleEvent(events.Achievements20Event(events.Achievements20Event.ACHIEVEMENT_EARNED_SHOWNED), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onGoToAchievement(self, args):
        isTrophy = args.get('isTrophy')
        isMultiple = args.get('isMultiple')
        achievementId = int(args.get('achievementId'))
        category = args.get('category')
        goToAchievements = partial(showAdvancedAchievementsView, closeCallback=self.__achievementCloseCallback)
        self.__uiLogging.logNotificationClick(AdvancedAchievementKeys.EARNING_NOTIFICATION, isMultiple)
        if isTrophy:
            showTrophiesView(goToAchievements, AdvancedAchievementViewKey.EARNING, mainViewCallback=self.__achievementCloseCallback)
        elif isMultiple:
            goToAchievements()
        else:
            initAchievementsIds = createAdvancedAchievementsCatalogInitAchievementIDs(achievementId, category)
            self.__achievementsController.seeUnseenAdvancedAchievement(category, achievementId)
            showAdvancedAchievementsCatalogView(initAchievementsIds, category, self.__achievementCloseCallback, AdvancedAchievementViewKey.EARNING, mainViewCallback=self.__achievementCloseCallback)

    def __achievementCloseCallback(self):
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.VISITED_ACHIEVEMENTS_FROM_NOTIFICATION, True)
