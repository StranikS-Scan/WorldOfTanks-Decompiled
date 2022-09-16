# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/subscriptions_feature.py
from constants import PLAYER_SUBSCRIPTIONS_CONFIG
from gui.impl.gen.view_models.views.lobby.account_dashboard.subscriptions_entry_point_model import SubscriptionsEntryPointModel
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showSubscriptionsPage
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class SubscriptionsFeature(FeatureItem):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def initialize(self, *args, **kwargs):
        super(SubscriptionsFeature, self).initialize(*args, **kwargs)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self._viewModel.subscriptions.onClick += self.__onClick

    def finalize(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self._viewModel.subscriptions.onClick -= self.__onClick
        super(SubscriptionsFeature, self).finalize()

    def _fillModel(self, model):
        self.__update(model=model)

    @replaceNoneKwargsModel
    def __update(self, model=None):
        submodel = model.subscriptions
        submodel.setIsEnabled(self.__lobbyContext.getServerSettings().isPlayerSubscriptionsEnabled())
        model.setIsPlayerSubscriptionsEntrypointHidden(self.__lobbyContext.getServerSettings().isPlayerSubscriptionsEntrypointHidden())

    def __onServerSettingsChanged(self, diff):
        if PLAYER_SUBSCRIPTIONS_CONFIG in diff:
            self.__update()

    @staticmethod
    def __onClick():
        showSubscriptionsPage()
