# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/dog_tags_feature.py
import BigWorld
from account_helpers.AccountSettings import AccountSettings, DOG_TAGS
from constants import DOG_TAGS_CONFIG
from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tags_model import DogTagsModel
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.dog_tags.animated_dog_tag_composer import AnimatedDogTagComposer
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showDogTags, showAnimatedDogTags
from gui.shared.events import DogTagsEvent
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext

class DogTagsFeature(FeatureItem):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __slots__ = ('_customizableComposer', '_animatedComposer', '_dtHelper')

    def __init__(self, viewModel):
        super(DogTagsFeature, self).__init__(viewModel)
        self._dtHelper = BigWorld.player().dogTags
        self._customizableComposer = DogTagComposerLobby(self._dtHelper)
        self._animatedComposer = AnimatedDogTagComposer(self._dtHelper)

    def initialize(self, *args, **kwargs):
        super(DogTagsFeature, self).initialize(*args, **kwargs)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        self._dtHelper.onDogTagDataChanged += self.__onDogTagDataChanged
        g_eventBus.addListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__limitedUIController.startObserve(LuiRules.DOG_TAG_HINT, self.__onLuiRuleDogTagCompleted)
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self._viewModel.dogTags.customizableDogTag.onClick += self.__onCustomizableDogTagClick
        self._viewModel.dogTags.animatedDogTag.onClick += self.__onAnimatedDogTagClick

    def finalize(self):
        self._viewModel.dogTags.customizableDogTag.onClick -= self.__onCustomizableDogTagClick
        self._viewModel.dogTags.animatedDogTag.onClick -= self.__onAnimatedDogTagClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        self._dtHelper.onDogTagDataChanged -= self.__onDogTagDataChanged
        g_eventBus.removeListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__limitedUIController.stopObserve(LuiRules.DOG_TAG_HINT, self.__onLuiRuleDogTagCompleted)
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        super(DogTagsFeature, self).finalize()

    def _fillModel(self, model):
        self.__updateModel(model=model)

    def __onServerSettingsChanged(self, diff):
        if DOG_TAGS_CONFIG in diff:
            self.__updateModel()

    def __updatePrem(self, *_):
        self.__updateModel()

    def __onDogTagDataChanged(self, diff):
        self.__updateModel()

    def __onCountersUpdated(self, event):
        self.__updateModel()

    def __onLuiRuleDogTagCompleted(self, *_):
        self.__updateModel()

    def __onAccountSettingsChanging(self, key, _):
        if key == DOG_TAGS:
            self.__updateModel()

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        submodel = model.dogTags
        submodel.setIsEnabled(self.__lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled())
        self._customizableComposer.fillEntryPoint(submodel.customizableDogTag)
        self._animatedComposer.fillEntryPoint(submodel.animatedDogTag)

    @staticmethod
    def __onCustomizableDogTagClick():
        showDogTags()

    @staticmethod
    def __onAnimatedDogTagClick():
        showAnimatedDogTags()
