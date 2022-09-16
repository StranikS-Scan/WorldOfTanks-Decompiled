# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/bonus_xp_feature.py
import typing
from constants import PremiumConfigs, PREMIUM_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showDailyExpPageView
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_dashboard.bonus_xp_model import BonusXpModel

class BonusXPFeature(FeatureItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)

    def initialize(self, *args, **kwargs):
        super(BonusXPFeature, self).initialize(*args, **kwargs)
        self.__startListening()

    def finalize(self):
        self.__stopListening()
        super(BonusXPFeature, self).finalize()

    def _fillModel(self, model):
        self.__updateModel(model=model)

    def __startListening(self):
        self.__gameSession.onPremiumNotify += self.__onUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        g_clientUpdateManager.addCallbacks({'applyAdditionalXPCount': self.__onUpdate})
        self._viewModel.bonusXp.onClick += self.__onClick

    def __stopListening(self):
        self._viewModel.bonusXp.onClick -= self.__onClick
        self.__gameSession.onPremiumNotify -= self.__onUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onUpdate(self, *_):
        self.__updateModel()

    def _onServerSettingsChange(self, diff):
        if PremiumConfigs.DAILY_BONUS in diff:
            self.__updateModel()

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        submodel = model.bonusXp
        config = self.__lobbyContext.getServerSettings().getAdditionalBonusConfig()
        submodel.setIsEnabled(config.get('enabled', False))
        submodel.setMultiplier(int(config.get('bonusFactor')))
        submodel.setUsesLeft(self.__itemsCache.items.stats.applyAdditionalXPCount)
        submodel.setTotalUses(config.get('applyCount') if self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS) else 0)

    @staticmethod
    def __onClick():
        showDailyExpPageView()
