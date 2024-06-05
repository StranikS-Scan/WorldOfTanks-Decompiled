# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/achievements/advanced_achievements_view.py
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements.advanced_achievements_view_model import AdvancedAchievementsViewModel
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements.upcoming_model import UpcomingModel
from helpers import dependency
from frameworks.wulf import WindowLayer, WindowStatus
from gui.shared.event_dispatcher import showAdvancedAchievementsCatalogView, showTrophiesView, showAdvancedAchievementsView
from gui.impl.lobby.achievements.profile_utils import fillAdvancedAchievementModel, createAdvancedAchievementsCatalogInitAchievementIDs, getTrophiesData, fillSubcategoryAdvancedAchievementModel, getVehicleByName
from advanced_achievements_client.constants import AchievementType
from advanced_achievements_client.getters import ROOT_ACHIEVEMENT_IDS, getAchievementByID, getNearest, getLastReceivedAchievements
from uilogging.advanced_achievement.logger import AdvancedAchievementLogger
from uilogging.advanced_achievement.logging_constants import AdvancedAchievementViewKey, AdvancedAchievementButtons, AdvancedAchievementKeys, AdvancedAchievementSubcategory
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IAchievementsController
from skeletons.gui.impl import IGuiLoader

class AdvancedAchievementsView(SubModelPresenter):
    __slots__ = ('__userId', '__achievementList', '__isAnimationInProgress', '__isWindowOverlapped', '__uiLogger')
    __itemsCache = dependency.descriptor(IItemsCache)
    __advAchmntCtrl = dependency.descriptor(IAchievementsController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __RESTRICTED_LAYERS = {WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.TOP_WINDOW,
     WindowLayer.WINDOW,
     WindowLayer.TOP_SUB_VIEW}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, achievementsModel, parentView, userId):
        self.__userId = userId
        self.__achievementList = None
        self.__isAnimationInProgress = False
        self.__isWindowOverlapped = False
        self.__uiLogger = AdvancedAchievementLogger(AdvancedAchievementViewKey.PLAYER_COLLECTION)
        super(AdvancedAchievementsView, self).__init__(achievementsModel, parentView)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def __isOtherPlayer(self):
        return self.__userId is not None

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def initialize(self, *args, **kwargs):
        super(AdvancedAchievementsView, self).initialize(*args, **kwargs)
        if not self.__isOtherPlayer:
            self.__advAchmntCtrl.setMainAdvancedAchievementsPageVisited(True)
        self.__updatePage()
        self.__uiLogger.onViewOpen(AdvancedAchievementViewKey.PLAYER_COLLECTION, AdvancedAchievementViewKey.HANGAR, isOtherPlayer=self.__isOtherPlayer)

    def _getEvents(self):
        return ((self.viewModel.onOpenDetails, self.__onOpenDetails),
         (self.viewModel.onCupClick, self.__onCupClick),
         (self.viewModel.onOpenTrophies, self.__onOpenTrophies),
         (self.viewModel.onAnimationInProgress, self.__onAnimationInProgress),
         (self.viewModel.onAllAnimationEnd, self.__onAllAnimationEnd),
         (self.viewModel.onAchievementHover, self.__onAchievementHover),
         (self.__advAchmntCtrl.onNewAchievementsEarned, self.__onNewAchievementsEarned),
         (self.__guiLoader.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged))

    def finalize(self):
        self.__achievementList = None
        super(AdvancedAchievementsView, self).finalize()
        return

    def __onWindowStatusChanged(self, _, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            windows = self.__guiLoader.windowsManager.findWindows(lambda w: w.layer in self.__RESTRICTED_LAYERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)
            if windows:
                self.__isWindowOverlapped = True
            elif self.__isWindowOverlapped:
                self.__isWindowOverlapped = False
                self.__update()
            self.__onSkipAnimation(self.__isWindowOverlapped)

    def __onNewAchievementsEarned(self, _):
        self.__update()

    def __update(self):
        if not self.__isAnimationInProgress and not self.__isOtherPlayer and not self.__isWindowOverlapped:
            self.__updatePage()

    def __updatePage(self):
        dossierDescr = self.__itemsCache.items.getAccountDossier(self.__userId).getDossierDescr()
        achievementProgress = self.__advAchmntCtrl.getProgress(self.__userId)
        currentAchievementScore = self.__advAchmntCtrl.getCurrentScore(self.__userId)
        subcategoryData = self.__advAchmntCtrl.getPrevCategoryData()
        prevCategoryData = []
        self.__updateUpcomingAchievements(dossierDescr)
        with self.viewModel.transaction() as model:
            if self.__isOtherPlayer:
                model.setPrevAchievementsScore(currentAchievementScore)
                model.setPrevCategoryProgress(achievementProgress.getAsPercent())
            else:
                model.setPrevAchievementsScore(self.__advAchmntCtrl.getPrevAchievementsScore())
                model.setPrevCategoryProgress(self.__advAchmntCtrl.getPrevPlayerCollectionProgress())
            self.__updateTrophies(model)
            model.setIsOtherPlayer(self.__isOtherPlayer)
            model.setAchievementsScore(currentAchievementScore)
            model.setMaxAchievementsScore(self.__advAchmntCtrl.getTotalScore())
            model.setCategoryBackgroundName('players_collection')
            model.setCategoryName('players_collection')
            model.setCategoryProgress(achievementProgress.getAsPercent())
            subCategories = model.getSubcategories()
            subCategories.clear()
            for idx, (achievementCategory, id) in enumerate(ROOT_ACHIEVEMENT_IDS):
                subcategory = getAchievementByID(id, achievementCategory, dossierDescr)
                bubbles = self.__advAchmntCtrl.getUnseenAdvancedAchievementsCount(achievementCategory, id, self.__userId)
                prevScore = subcategory.getScore().current if self.__isOtherPlayer else subcategoryData[idx][0]
                prevValue = subcategory.getProgress().getAsPercent() if self.__isOtherPlayer else subcategoryData[idx][1]
                subCategories.addViewModel(fillSubcategoryAdvancedAchievementModel(subcategory, bubbles, prevScore, prevValue))
                prevCategoryData.append((subcategory.getScore().current, int(subcategory.getProgress().getAsPercent())))

            subCategories.invalidate()
        if not self.__isOtherPlayer:
            self.__setPrevAchievementScore()
            self.__setPrevSubcategoryData(prevCategoryData)
            self.__setPrevTrophy()
            self.__setPrevCategoryProgress(achievementProgress.getAsPercent())

    def __updateTrophies(self, model):
        trophyModel = model.trophy
        data = getTrophiesData()
        trophyModel.setType(data['type'])
        trophyModel.setKey(data['key'])
        trophyModel.setBubbles(self.__advAchmntCtrl.getUnseenTrophiesAdvancedAchievementsCount(self.__userId))
        trophyModel.setBackground(data['background'])
        trophyModel.setIconPosition(data['iconPosition'])
        trophyModel.setIsTrophy(data['isTrophy'])
        trophyModel.setCurrentValue(len(self.__advAchmntCtrl.getTrophiesAchievements(self.__userId)))
        trophyModel.setPrevValue(self.__advAchmntCtrl.getPrevTrophy())

    def __updateUpcomingAchievements(self, dossierDescr):
        if self.__isOtherPlayer:
            self.__achievementList = getLastReceivedAchievements(dossierDescr)
        else:
            self.__achievementList = getNearest()
        if self.__achievementList:
            with self.viewModel.transaction() as model:
                nearestAchievements = model.getUpcomingAchievements()
                nearestAchievements.clear()
                for achievement in self.__achievementList:
                    nearestAchievements.addViewModel(self.__fillUpcomingAchievement(achievement))

                nearestAchievements.invalidate()

    def __fillUpcomingAchievement(self, achievement):
        upcomingModel = UpcomingModel()
        with upcomingModel.transaction() as model:
            fillAdvancedAchievementModel(achievement, model, self.__isOtherPlayer)
            if achievement.getType() == AchievementType.REGULAR:
                conditionID = achievement.getConditionID()
                isResearchable = bool(achievement.getOpenByUnlock())
                if conditionID is not None and isResearchable:
                    item = self.__itemsCache.items.getItemByCD(conditionID)
                    model.setIsResearchable(isResearchable)
                    model.setSpecificItemName(item.shortUserName)
                    model.setSpecificItemLevel(item.level)
        if achievement.getVehicle():
            model.setSpecificItemLevel(getVehicleByName(achievement.getVehicle()))
        return upcomingModel

    def __setPrevAchievementScore(self):
        self.__advAchmntCtrl.setPrevAchievementsScore(self.__advAchmntCtrl.getCurrentScore())

    def __setPrevTrophy(self):
        self.__advAchmntCtrl.setPrevTrophy(self.__advAchmntCtrl.getPrevTrophy())

    def __setPrevSubcategoryData(self, prevSubcategories):
        self.__advAchmntCtrl.setPrevCategoryData(prevSubcategories)

    def __setPrevCategoryProgress(self, value):
        self.__advAchmntCtrl.setPrevPlayerCollectionProgress(value)

    def __onAnimationInProgress(self, args):
        self.__isAnimationInProgress = args['isAnimationInProgress']

    def __onAllAnimationEnd(self):
        self.__update()

    def __onCupClick(self):
        self.__uiLogger.logClick(AdvancedAchievementButtons.GOBLET)

    def __onAchievementHover(self, args):
        achievementID = int(args['achievementId'])
        category = args['achievementCategory']
        if achievementID in self.__advAchmntCtrl.getUnseenAdvancedAchievements(category):
            self.__advAchmntCtrl.seeUnseenAdvancedAchievement(category, achievementID)
            self.__update()

    def __onSkipAnimation(self, isSkip):
        self.viewModel.setIsSkipAnimation(isSkip)

    def __onOpenDetails(self, args):
        achievementID = int(args['achievementId'])
        category = args['achievementCategory']
        initIDs = createAdvancedAchievementsCatalogInitAchievementIDs(achievementID, category)
        self.__uiLogger.logCategoryClick(achievementID, category)
        showAdvancedAchievementsCatalogView(initIDs, category, closeCallback=showAdvancedAchievementsView, parentScreen=AdvancedAchievementViewKey.PLAYER_COLLECTION)

    def __onOpenTrophies(self):
        if len(self.__advAchmntCtrl.getTrophiesAchievements(self.__userId)) < 1:
            return
        showTrophiesView(closeCallback=showAdvancedAchievementsView, parentScreen=AdvancedAchievementViewKey.PLAYER_COLLECTION)
        self.__uiLogger.logClick(AdvancedAchievementKeys.SUBCATEGORY, parentScreen=AdvancedAchievementViewKey.PLAYER_COLLECTION, info=AdvancedAchievementSubcategory.TROPHY)
