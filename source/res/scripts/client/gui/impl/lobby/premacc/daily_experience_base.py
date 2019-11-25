# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/daily_experience_base.py
import logging
import typing
from constants import PREMIUM_TYPE, PremiumConfigs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.premacc.daily_experience_base_model import DailyExperienceBaseModel
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
logger = logging.getLogger(__name__)

class DailyExperienceBaseView(ViewImpl, SoundViewMixin):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ()

    @property
    def viewModel(self):
        return super(DailyExperienceBaseView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(DailyExperienceBaseView, self)._initialize(*args, **kwargs)
        self._addSoundEvent()
        self._addListeners()
        self._updateData()

    def _finalize(self):
        self._removeListeners()
        self._removeSoundEvent()
        super(DailyExperienceBaseView, self)._finalize()

    def _addListeners(self):
        self.__gameSession.onPremiumNotify += self.__updateIsTankPremiumActive
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        g_clientUpdateManager.addCallbacks({'applyAdditionalXPCount': self.__updateLeftBonusCount})

    def _removeListeners(self):
        self.__gameSession.onPremiumNotify -= self.__updateIsTankPremiumActive
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _getConfig(self):
        return self.__lobbyContext.getServerSettings().getAdditionalBonusConfig()

    def _updateData(self):
        logger.info('Update data connected with daily bonuses')
        config = self._getConfig()
        with self.getViewModel().transaction() as model:
            model.setMultiplier(int(config.get('bonusFactor')))
            model.setTotalBonusCount(config.get('applyCount'))
            model.setIsTankPremiumActive(self.__isTankPremiumActive())
            self.__updateLeftBonusCount(model=model)

    def _onServerSettingsChange(self, diff):
        diffConfig = diff.get(PremiumConfigs.DAILY_BONUS)
        if diffConfig is None:
            return
        else:
            self._updateData()
            return

    @replaceNoneKwargsModel
    def __updateLeftBonusCount(self, battlesLeft=None, model=None):
        leftBonusCount = battlesLeft or self.__itemsCache.items.stats.applyAdditionalXPCount
        model.setLeftBonusCount(leftBonusCount)

    def __updateIsTankPremiumActive(self, *args, **kwargs):
        isPremium = self.__isTankPremiumActive()
        self.viewModel.setIsTankPremiumActive(isPremium)

    def __isTankPremiumActive(self):
        return self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
