# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_premium_plus.py
from __future__ import absolute_import
import typing
from constants import PremiumConfigs
from fun_random.gui.battle_results.packers.fun_packers import FunRandomPremiumPlus
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gui_decorators import args2params
from gui.impl.gen.view_models.views.lobby.battle_results.premium_plus_model import PremiumPlusModel
from gui.shared import events
from helpers import dependency, server_settings
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunPremiumPlusSubPresenter(BattleResultsSubPresenter):
    __gameSession = dependency.descriptor(IGameSessionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    @classmethod
    def getViewModelType(cls):
        return PremiumPlusModel

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FunRandomPremiumPlus.packModel(model, battleResults)

    def _getEvents(self):
        return super(FunPremiumPlusSubPresenter, self)._getEvents() + ((self.getViewModel().onPremiumXpBonusApplied, self.__onXpBonusApplied),
         (self.getViewModel().onNextBonusTimeUpdate, self.__onNextBonusTimeUpdate),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__wotPlusController.onDataChanged, self.__onWotPlusChanged),
         (self.__gameSession.onPremiumTypeChanged, self.__onPremiumStatusChanged))

    def _getListeners(self):
        return super(FunPremiumPlusSubPresenter, self)._getListeners() + ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusApplyStatusChanged),)

    def _getCallbacks(self):
        return super(FunPremiumPlusSubPresenter, self)._getCallbacks() + (('stats.applyAdditionalXPCount', self.__onXpBonusChanged), ('stats.applyAdditionalWoTPlusXPCount', self.__onXpBonusChanged))

    @args2params(bool)
    def __onNextBonusTimeUpdate(self, isUpdate):
        if isUpdate:
            self.__onXpBonusChanged()

    def __onPremiumStatusChanged(self, _=None):
        with self.getViewModel().transaction() as model:
            FunRandomPremiumPlus.updateModel(model, self.getBattleResults())

    @server_settings.serverSettingsChangeListener(PremiumConfigs.DAILY_BONUS)
    def __onServerSettingsChanged(self, _):
        with self.getViewModel().transaction() as model:
            FunRandomPremiumPlus.updateModel(model, self.getBattleResults())

    def __onXpBonusApplied(self):
        self._battleResults.applyAdditionalBonus(self.parentView.arenaUniqueID)

    def __onXpBonusApplyStatusChanged(self, event):
        with self.getViewModel().transaction() as model:
            ctx = event.ctx if event is not None else None
            FunRandomPremiumPlus.updateModel(model, self.getBattleResults(), ctx, isFullUpdate=False)
        return

    def __onXpBonusChanged(self, _=None):
        with self.getViewModel().transaction() as model:
            FunRandomPremiumPlus.updateModel(model, self.getBattleResults(), isFullUpdate=False)

    def __onWotPlusChanged(self, data):
        if 'isEnabled' in data:
            self.__onXpBonusChanged()
