# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/animated_dog_tags_view.py
import logging
import typing
from functools import partial
import BigWorld
import WWISE
from constants import DOG_TAGS_CONFIG
from dog_tags_common.dog_tags_storage import UnlockedComponentsStorage, PlayerDogTagStorage
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.animated_dog_tags_view_model import AnimatedDogTagsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.achievements.profile_utils import createAdvancedAchievementsCatalogInitAchievementIDs
from gui.impl.lobby.dog_tags.animated_dog_tag_composer import AnimatedDogTagComposer
from gui.impl.lobby.dog_tags.catalog_animated_dog_tag_tooltip import CatalogAnimatedDogTagTooltip
from gui.impl.pub import ViewImpl
from gui.server_events import settings as userSettings
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView, showAdvancedAchievementsCatalogView, showAnimatedDogTags
from gui.impl.lobby.account_dashboard.sound_constants import ACC_DASHBOARD_SOUND_SPACE
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
from uilogging.dog_tags.logger import AnimatedDogTagsViewLogger
from uilogging.dog_tags.logging_constants import DogTagButtons, DogTagsViewKeys, DogTagKeys
from gui.Scaleform.Waiting import Waiting
if typing.TYPE_CHECKING:
    from account_helpers.dog_tags import DogTags as DogTagsAccountHelper
_logger = logging.getLogger(__name__)

class AnimatedDogTagsView(ViewImpl):
    __slots__ = ('_dogTagsHelper', '_composer', '__initBackgroundId', '__initEngravingId', '__closeCallback', '__uiLogger')
    _webCtrl = dependency.descriptor(IWebController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _COMMON_SOUND_SPACE = ACC_DASHBOARD_SOUND_SPACE

    def __init__(self, layoutID=R.views.lobby.dog_tags.AnimatedDogTagsView(), initBackgroundId=0, initEngravingId=0, closeCallback=None, makeTopView=True, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW if makeTopView else ViewFlags.LOBBY_SUB_VIEW
        settings.model = AnimatedDogTagsViewModel()
        self.__initBackgroundId = initBackgroundId
        self.__initEngravingId = initEngravingId
        self.__closeCallback = closeCallback
        self._dogTagsHelper = BigWorld.player().dogTags
        self._composer = AnimatedDogTagComposer(self._dogTagsHelper)
        self.__uiLogger = AnimatedDogTagsViewLogger(DogTagsViewKeys.DOG_TAG)
        super(AnimatedDogTagsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AnimatedDogTagsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onEquip, self.__onEquip),
         (self.viewModel.onGoToAchievement, self.__onGoToAchievement),
         (self.viewModel.onInfoButtonClick, self.__onInfoButtonClicked),
         (self.viewModel.onPlayVideo, self.__onPlayVideo),
         (self.viewModel.onOnboardingCloseClick, self.__onOnboardingCloseClick),
         (self.viewModel.onHideNewBubble, self.__onHideNewBubble),
         (self.viewModel.onClose, self.__onClose),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self._dogTagsHelper.onDogTagDataChanged, self.__onDogTagDataChanged))

    def _onLoading(self):
        super(AnimatedDogTagsView, self)._onLoading()
        self.__update()

    def _onLoaded(self, *args, **kwargs):
        Waiting.hide('loadPage')
        self.__uiLogger.onViewOpen(DogTagsViewKeys.ANIMATED_DOG_TAG, DogTagsViewKeys.ACCOUNT_DASHBOARD)
        if not userSettings.getDogTagsSettings().animatedDogTagsVisited:
            with userSettings.dogTagsSettings() as dt:
                dt.setAnimatedDogTagsVisited(True)
        super(AnimatedDogTagsView, self)._onLoaded(*args, **kwargs)

    def _finalize(self):
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ach_dog_tag_exit()))
        super(AnimatedDogTagsView, self)._finalize()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.dog_tags.CatalogAnimatedDogTagTooltip():
            params = {'engravingId': event.getArgument('engravingId'),
             'backgroundId': event.getArgument('backgroundId')}
            return CatalogAnimatedDogTagTooltip(params=params, uiParent=DogTagsViewKeys.ANIMATED_DOG_TAG)
        else:
            return None

    def __onClose(self):
        self.destroyWindow()
        if callable(self.__closeCallback):
            self.__closeCallback()

    def __update(self):
        with self.viewModel.transaction() as tx:
            self._composer.fillAnimatedDogTags(tx, self.__initBackgroundId, self.__initEngravingId)
            tx.setOnboardingEnabled(userSettings.getDogTagsSettings().onboardingEnabled)

    def __onInfoButtonClicked(self):
        url = GUI_SETTINGS.dogTagsInfoPage
        _logger.info('Opening info page: %s', url)
        self.__uiLogger.logClick(DogTagButtons.INFO, DogTagsViewKeys.ANIMATED_DOG_TAG)
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)

    @args2params(int, int)
    def __onEquip(self, background, engraving):
        _logger.debug('DogTags::onEquip(%s, %s)', background, engraving)
        self._dogTagsHelper.updatePlayerDT(background, engraving)
        with userSettings.dogTagsSettings() as dt:
            dt.setSelectedAnimated([background, engraving])

    @args2params(int, str, int, int)
    def __onGoToAchievement(self, achievementId, category, background, engraving):
        Waiting.show('loadPage')
        initAchievementsIds = createAdvancedAchievementsCatalogInitAchievementIDs(achievementId, category)
        showAdvancedAchievementsCatalogView(initAchievementsIds, category, closeCallback=_getCatalogCallback(background, engraving, self.__closeCallback), parentScreen=DogTagsViewKeys.ANIMATED_DOG_TAG)
        self.__uiLogger.logClickAchievement(DogTagKeys.ACHIEVEMENT_CARD, achievementId, category)
        self.destroyWindow()

    @args2params(str)
    def __onPlayVideo(self, urlKey):
        url = ''
        if urlKey == 'onboardingVideo1':
            url = GUI_SETTINGS.dogTagsOnboardingVideo1
        elif urlKey == 'onboardingVideo2':
            url = GUI_SETTINGS.dogTagsOnboardingVideo2
        _logger.info('Starting video: %s', url)
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT)

    def __onOnboardingCloseClick(self):
        with userSettings.dogTagsSettings() as dt:
            dt.setOnboardingEnabled(False)
            with self.viewModel.transaction() as tx:
                tx.setOnboardingEnabled(dt.onboardingEnabled)

    @args2params(int, int)
    def __onHideNewBubble(self, background, engraving):
        with userSettings.dogTagsSettings() as dt:
            dt.markComponentAsSeen(background)
            dt.markComponentAsSeen(engraving)
        g_eventBus.handleEvent(events.DogTagsEvent(events.DogTagsEvent.COUNTERS_UPDATED), EVENT_BUS_SCOPE.LOBBY)
        self.__update()

    def __onDogTagDataChanged(self, diff):
        _logger.debug('DogTags::__onDogTagDataChanged: %s', diff)
        if (PlayerDogTagStorage.key, '_r') in diff or UnlockedComponentsStorage.key in diff:
            self.__update()

    def __onServerSettingsChange(self, diff):
        if DOG_TAGS_CONFIG in diff:
            if not self.lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled():
                self.destroyWindow()


def _getCatalogCallback(backgroundId, engravingId, closeCallback):

    def backToAnimatedDT(backgroundId, engravingId, closeCallback):
        uiLoader = dependency.instance(IGuiLoader)
        achievementsMainView = uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.achievements.AchievementsMainView())
        if achievementsMainView is None:
            Waiting.show('loadPage')
            showAnimatedDogTags(backgroundId, engravingId, closeCallback)
        return

    return partial(backToAnimatedDT, backgroundId, engravingId, closeCallback)
