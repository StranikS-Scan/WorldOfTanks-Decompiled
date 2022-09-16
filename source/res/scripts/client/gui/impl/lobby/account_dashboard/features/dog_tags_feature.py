# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/dog_tags_feature.py
import BigWorld
from constants import DOG_TAGS_CONFIG
from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tags_model import DogTagsModel
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showDogTags
from gui.shared.events import DogTagsEvent
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext

class DogTagsFeature(FeatureItem):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('_composer', '_dtHelper')

    def __init__(self, viewModel):
        super(DogTagsFeature, self).__init__(viewModel)
        self._dtHelper = BigWorld.player().dogTags
        self._composer = DogTagComposerLobby(self._dtHelper)

    def initialize(self, *args, **kwargs):
        super(DogTagsFeature, self).initialize(*args, **kwargs)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        self._dtHelper.onDogTagDataChanged += self.__onDogTagDataChanged
        g_eventBus.addListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
        self._viewModel.dogTags.onClick += self.__onClick

    def finalize(self):
        self._viewModel.dogTags.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        self._dtHelper.onDogTagDataChanged -= self.__onDogTagDataChanged
        g_eventBus.removeListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
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

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        submodel = model.dogTags
        self._composer.fillDTFeatureModel(submodel)

    @staticmethod
    def __onClick():
        showDogTags()
