# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/catalog_view.py
from functools import partial
import typing
from PlayerEvents import g_playerEvents
from advanced_achievements_client.constants import TROPHIES_ACHIEVEMENT_ID
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.catalog_view_model import CatalogViewModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.breadcrumb_model import BreadcrumbModel
from gui.impl.lobby.achievements.profile_utils import fillDetailsModel, fillBreadcrumbModel, fillAchievementCardModel, getTrophiesData, createBackportTooltipDecorator, createTooltipContentDecorator
from gui.shared.event_dispatcher import showAdvancedAchievementsCatalogView, showAdvancedAchievementsView, showStylePreview, showResearchView, showAnimatedDogTags, showDashboardView
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IAchievementsController
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.app_loader import IAppLoader
from uilogging.advanced_achievement.logger import AdvancedAchievementLogger
from uilogging.advanced_achievement.logging_constants import AdvancedAchievementViewKey, AdvancedAchievementButtons
from gui.Scaleform.daapi.view.lobby.profile.sound_constants import ACHIEVEMENTS_SOUND_SPACE
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.details_model import DetailsModel

class CatalogView(ViewImpl):
    __slots__ = ('__tooltipData', '__closeCallback', '__breadcrumbAchievementIDs', '__achievementCategory', '__uiLogging', '__uiParentScreen', '__mainViewCallback')
    __achievementsController = dependency.descriptor(IAchievementsController)
    __customizationService = dependency.descriptor(ICustomizationService)
    __appLoader = dependency.descriptor(IAppLoader)
    _COMMON_SOUND_SPACE = ACHIEVEMENTS_SOUND_SPACE

    def __init__(self, initAchievementIDs, achievementCategory, closeCallback, uiParentScreen, mainViewCallback=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.achievements.CatalogView())
        settings.flags = ViewFlags.VIEW
        settings.model = CatalogViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipData = {}
        self.__achievementCategory = achievementCategory
        self.__closeCallback = closeCallback
        self.__breadcrumbAchievementIDs = initAchievementIDs
        self.__uiParentScreen = uiParentScreen
        self.__uiLogging = AdvancedAchievementLogger(AdvancedAchievementViewKey.CATALOG)
        self.__mainViewCallback = mainViewCallback
        super(CatalogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CatalogView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onBreadcrumbClick, self.__onBreadcrumbClick),
         (self.viewModel.onCatalogClick, self.__onCatalogClick),
         (self.viewModel.onStylePreview, self.__onStylePreview),
         (self.viewModel.onPurchaseVehicleClick, self.__onPurchaseVehicleClick),
         (self.viewModel.onCardClick, self.__onCardClick),
         (self.viewModel.onHintClose, self.__onHintClose),
         (self.viewModel.onCardHover, self.__onCardHover),
         (self.viewModel.onDogTagPreview, self.__onDogTagPreview),
         (g_playerEvents.onDisconnected, self.destroyWindow))

    @createTooltipContentDecorator(AdvancedAchievementViewKey.CATALOG)
    def createToolTipContent(self, event, contentID):
        return None

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CatalogView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        self.__updatePage()
        self.viewModel.setIsNeededShowHint(self.__achievementsController.getShowHint())
        super(CatalogView, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        Waiting.hide('loadPage')
        self.__uiLogging.onViewOpen(AdvancedAchievementViewKey.CATALOG, parentScreen=self.__uiParentScreen)
        super(CatalogView, self)._onLoaded(*args, **kwargs)

    def _finalize(self):
        self.__breadcrumbAchievementIDs = None
        super(CatalogView, self)._finalize()
        return

    def __updatePage(self):
        self.__tooltipData.clear()
        with self.viewModel.transaction() as model:
            self.__updateAchievementScore(model)
            self.__updateBreadcrumbs(model)
            self.__updateAchievements(model)

    def __updateAchievementScore(self, model):
        model.setAchievementScore(self.__achievementsController.getCurrentScore())
        model.setMaxAchievementsScore(self.__achievementsController.getTotalScore())

    def __updateBreadcrumbs(self, model):
        breadcrumbs = model.getBreadcrumbs()
        breadcrumbs.clear()
        for achievementID in self.__breadcrumbAchievementIDs:
            if achievementID == TROPHIES_ACHIEVEMENT_ID:
                trophiesData = getTrophiesData()
                breadcrumbModel = BreadcrumbModel()
                breadcrumbModel.setAchievementId(TROPHIES_ACHIEVEMENT_ID)
                breadcrumbModel.setKey(trophiesData['key'])
                breadcrumbs.addViewModel(breadcrumbModel)
            breadcrumbs.addViewModel(fillBreadcrumbModel(self.__achievementsController.getAchievementByID(achievementID, self.__achievementCategory)))

        breadcrumbs.invalidate()

    def __updateAchievements(self, model):
        descriptionAchievementID = self.__breadcrumbAchievementIDs[-1]
        if descriptionAchievementID == TROPHIES_ACHIEVEMENT_ID:
            self.__updateTrophiesDescription(model)
            self.__updateAchievementsList(model, self.__achievementsController.getTrophiesAchievements())
        else:
            descriptionAchievement = self.__achievementsController.getAchievementByID(descriptionAchievementID, self.__achievementCategory)
            self.__updateDescription(model, descriptionAchievement)
            self.__updateAchievementsList(model, descriptionAchievement.getChildsIterator())

    def __updateDescription(self, model, descriptionAchievement):
        fillDetailsModel(descriptionAchievement, self.__tooltipData, model.details)

    def __updateTrophiesDescription(self, model):
        detailsModel = model.details
        trophiesData = getTrophiesData()
        detailsModel.setType(trophiesData['type'])
        detailsModel.setBackground(trophiesData['background'])
        detailsModel.setKey(trophiesData['key'])
        detailsModel.setIconPosition(trophiesData['iconPosition'])
        detailsModel.setIsTrophy(trophiesData['isTrophy'])

    def __updateAchievementsList(self, model, achievements):
        with model.getAchievementsList().transaction() as achievementsList:
            achievementsList.clear()
            for achievement in achievements:
                bubbleCount = self.__getAchievementBubbles(achievement)
                achievementsList.addViewModel(fillAchievementCardModel(achievement, self.__tooltipData, bubbleCount))

    def __getAchievementBubbles(self, achievement):
        descriptionAchievementID = self.__breadcrumbAchievementIDs[-1]
        if descriptionAchievementID == TROPHIES_ACHIEVEMENT_ID:
            if achievement.getID() not in self.__achievementsController.getSeenTrophiesAdvancedAchievements(achievement.getCategory()):
                return 1
            return 0
        return self.__achievementsController.getUnseenAdvancedAchievementsCount(achievement.getCategory(), achievement.getID())

    def __navigateToBreadcrumb(self, achievementID):
        while self.__breadcrumbAchievementIDs[-1] != achievementID:
            self.__breadcrumbAchievementIDs.pop()

    def __addBreadcrumb(self, achievementID):
        self.__breadcrumbAchievementIDs.append(achievementID)

    def __onClose(self):
        self.__closeCallback()
        self.destroyWindow()

    def __onBreadcrumbClick(self, args):
        self.__navigateToBreadcrumb(int(args['achievementId']))
        self.__updatePage()

    def __onCatalogClick(self):
        self.__uiLogging.logClick(AdvancedAchievementButtons.CATALOG)
        showAdvancedAchievementsView(closeCallback=self.__mainViewCallback)
        self.destroyWindow()

    def __onStylePreview(self, args):
        style = self.__customizationService.getItemByID(GUI_ITEM_TYPE.STYLE, int(args['id']))
        styledVehicleCD = getVehicleCDForStyle(style)
        showStylePreview(styledVehicleCD, style, backCallback=_getPreviewCallback(self.__appLoader, self.__breadcrumbAchievementIDs, self.__achievementCategory, self.__closeCallback, AdvancedAchievementViewKey.CATALOG), backBtnDescrLabel=backport.text(R.strings.achievements_page.stylePreview.backBtnDescr()))
        self.destroyWindow()

    def __onPurchaseVehicleClick(self, args):
        containerManager = self.__appLoader.getApp().containerManager
        researchView = containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_RESEARCH))
        if researchView is not None:
            researchView.destroy()
        showResearchView(int(args['intCD']))
        self.destroyWindow()
        return

    def __onCardClick(self, args):
        self.__uiLogging.logCardClick(int(args['achievementId']), args['category'])
        self.__addBreadcrumb(int(args['achievementId']))
        self.__updatePage()

    def __onHintClose(self):
        self.__achievementsController.setShowHint(False)
        self.viewModel.setIsNeededShowHint(False)

    def __onCardHover(self, args):
        achievementId = int(args['achievementId'])
        category = args['achievementCategory']
        if self.__breadcrumbAchievementIDs[-1] == TROPHIES_ACHIEVEMENT_ID:
            if achievementId not in self.__achievementsController.getSeenTrophiesAdvancedAchievements(category):
                self.__achievementsController.seeUnseenTrophiesAdvancedAchievement(category, achievementId)
                with self.viewModel.transaction() as model:
                    self.__updateAchievements(model)
        elif achievementId in self.__achievementsController.getUnseenAdvancedAchievements(category):
            self.__achievementsController.seeUnseenAdvancedAchievement(category, achievementId)
            with self.viewModel.transaction() as model:
                self.__updateAchievements(model)

    def __onDogTagPreview(self, args):
        containerManager = self.__appLoader.getApp().containerManager
        profileView = containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_PROFILE))
        Waiting.show('loadPage')
        self.__uiLogging.logClick(AdvancedAchievementButtons.DOG_TAG_PREVIEW)
        showAnimatedDogTags(args['backgroundId'], args['engravingId'], closeCallback=showDashboardView)
        if profileView is not None:
            profileView.destroy()
        self.destroyWindow()
        return


class CatalogViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, initAchievementIDs, achievementCategory, closeCallback, uiParentScreen, parent=None, *args, **kwargs):
        super(CatalogViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=CatalogView(initAchievementIDs=initAchievementIDs, achievementCategory=achievementCategory, closeCallback=closeCallback, uiParentScreen=uiParentScreen, *args, **kwargs), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


def _getPreviewCallback(appLoader, initAchievementIDs, achievementCategory, closeCallback, parentScreen):

    def backToCatalog(appLoader, initAchievementIDs, achievementCategory, closeCallback, parentScreen):
        containerManager = appLoader.getApp().containerManager
        stylePreview = containerManager.getViewByKey(ViewKey(VIEW_ALIAS.STYLE_PREVIEW))
        if stylePreview is not None:
            stylePreview.destroy()
        showAdvancedAchievementsCatalogView(initAchievementIDs, achievementCategory, closeCallback, parentScreen)
        return

    return partial(backToCatalog, appLoader, initAchievementIDs, achievementCategory, closeCallback, parentScreen)
