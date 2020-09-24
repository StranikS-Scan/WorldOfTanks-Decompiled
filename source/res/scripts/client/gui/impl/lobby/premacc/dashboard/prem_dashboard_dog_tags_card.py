# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_dog_tags_card.py
import BigWorld
from constants import DOG_TAGS_CONFIG
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_dog_tags_card_model import PremDashboardDogTagsCardModel
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import DogTagsEvent
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.event_dispatcher import showDogTags

class PremDashboardDogTagsCard(ViewImpl):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('_composer', '_dtHelper')

    def __init__(self, layoutID=R.views.lobby.premacc.dashboard.prem_dashboard_dog_tags_card.PremDashboardDogTagsCard()):
        settings = ViewSettings(layoutID)
        settings.model = PremDashboardDogTagsCardModel()
        self._dtHelper = BigWorld.player().dogTags
        self._composer = DogTagComposerLobby(self._dtHelper)
        super(PremDashboardDogTagsCard, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PremDashboardDogTagsCard, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PremDashboardDogTagsCard, self)._initialize(*args, **kwargs)
        self.viewModel.onGoToDogTagsView += self.__onOpenDogTagsView
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        self._dtHelper.onDogTagDataChanged += self.__onDogTagDataChanged
        g_eventBus.addListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__update()

    def _onLoading(self, *args, **kwargs):
        super(PremDashboardDogTagsCard, self)._onLoading(*args, **kwargs)
        self.__update()

    def _finalize(self):
        self.viewModel.onGoToDogTagsView -= self.__onOpenDogTagsView
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        self._dtHelper.onDogTagDataChanged -= self.__onDogTagDataChanged
        g_eventBus.removeListener(DogTagsEvent.COUNTERS_UPDATED, self.__onCountersUpdated, EVENT_BUS_SCOPE.LOBBY)
        super(PremDashboardDogTagsCard, self)._finalize()

    def __onOpenDogTagsView(self, _=None):
        showDogTags()
        self.__update()

    def __update(self):
        with self.viewModel.transaction() as tx:
            self._composer.fillDTCardModel(tx)

    def __timerUpdate(self):
        self.__update()

    def __onServerSettingsChanged(self, diff):
        if DOG_TAGS_CONFIG in diff:
            self.__update()

    def __updatePrem(self, *_):
        self.__update()

    def __onDogTagDataChanged(self, diff):
        self.__update()

    def __onCountersUpdated(self, event):
        self.__update()
