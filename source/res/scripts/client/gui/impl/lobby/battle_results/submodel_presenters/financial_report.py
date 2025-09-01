# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/financial_report.py
from math import ceil
from functools import partial
import typing
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import PremiumConfigs, PREMIUM_TYPE
from helpers import dependency, server_settings, time_utils
from gui.battle_results.pbs_helpers.additional_bonuses import getAccountStatusToBRPS, getAdditionalXpBonusStatus, isAddXpBonusStatusAcceptable, isAdditionalXpBonusAvailable, getLeftAdditionalBonus, getAdditionalXPFactor10FromResult, getAdditionalXpBonusDiff
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.presenters.packers.economics.financial_report_packers import CrystalsDetailsPacker, XpDetailsPacker, FreeXpDetailsPacker, CreditsStatisticsPacker, GoldStatisticsPacker
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.financial_report_model import FinancialReportModel
from gui.impl.gen.view_models.views.lobby.battle_results.additional_bonus_model import AdditionalBonusModel, PremiumXpBonusRestriction, BonusStates
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
from gui.shared import events
from gui.impl.lobby.premacc import premacc_helpers
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl, getWotPlusShopUrl
from gui.shared.event_dispatcher import showShop, showDailyExpPageView
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class ManageableBonusSubPresenter(BattleResultsSubPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusController = dependency.descriptor(IWotPlusController)
    __gameSession = dependency.descriptor(IGameSessionController)

    @classmethod
    def getViewModelType(cls):
        return AdditionalBonusModel

    @property
    def arenaUniqueID(self):
        return self.parentView.arenaUniqueID

    def packBattleResults(self, battleResults):
        reusable = battleResults.reusable
        piggyBankConfig = self.__lobbyContext.getServerSettings().getPiggyBankConfig()
        piggyBankMaxAmount = piggyBankConfig.get('creditsThreshold', 0)
        period = piggyBankConfig.get('cycleLength', time_utils.ONE_DAY)
        periodInDays = ceil(period / time_utils.ONE_DAY)
        dailyXp = self.__itemsCache.items.stats.dailyAppliedAdditionalXP
        self.getViewModel().setDailyAppliedAdditionalXP(dailyXp)
        self.getViewModel().setCreditsThreshold(piggyBankMaxAmount)
        self.getViewModel().setDurationInDays(periodInDays)
        self.getViewModel().setHasWotPlus(reusable.personal.isWotPlus)
        self.getViewModel().setHasAnyPremium(reusable.personal.hasAnyPremium)
        hasPremiumPlus = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        self.getViewModel().setHasPremium(hasPremiumPlus)
        hasBasicPremium = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.BASIC)
        self.getViewModel().setHasBasicPremium(hasBasicPremium)
        wasPremiumPlusInBattle = reusable.personal.isPremiumPlus
        self.getViewModel().setWasPremium(wasPremiumPlusInBattle)
        isXpBonusAvailable = isAdditionalXpBonusAvailable(self.arenaUniqueID, reusable, hasPremiumPlus, isAddXpBonusStatusAcceptable)
        self.getViewModel().setIsXpBonusEnabled(isXpBonusAvailable)
        hasWotPlus = self.__wotPlusController.isEnabled()
        _, leftCount, _ = getLeftAdditionalBonus(hasWotPlus, hasPremiumPlus)
        self.getViewModel().setLeftBonusCount(leftCount)
        isPersonalTeamWin = reusable.isPersonalTeamWin()
        if isPersonalTeamWin:
            multiplier = getAdditionalXPFactor10FromResult(battleResults.results[_RECORD.PERSONAL], reusable)
        else:
            bonusFactor = self.__lobbyContext.getServerSettings().getAdditionalBonusConfig().get('bonusFactor', 1)
            multiplier = premacc_helpers.validateAdditionalBonusMultiplier(bonusFactor)
        self.getViewModel().setBonusMultiplier(multiplier)
        self.getViewModel().setXpDiff(getAdditionalXpBonusDiff(self.arenaUniqueID))
        _, vehicle = first(reusable.personal.getVehicleItemsIterator())
        vehicleCD = vehicle.intCD
        addXpBonusStatus = getAdditionalXpBonusStatus(self.arenaUniqueID, isPersonalTeamWin, vehicleCD, isXpBonusAvailable)
        self.getViewModel().setRestriction(addXpBonusStatus)
        state = getAccountStatusToBRPS(hadPremiumPlus=reusable.isPostBattlePremiumPlus, isBonusAppliedAlready=self._battleResults.isAddXPBonusApplied(self.arenaUniqueID), hasXpInBonusCaps=reusable.common.checkBonusCaps(ARENA_BONUS_TYPE_CAPS.XP), hasXpBonusInBonusCaps=reusable.common.checkBonusCaps(ARENA_BONUS_TYPE_CAPS.ADDITIONAL_XP_POSTBATTLE), negativeImpact=reusable.personal.getXPDiff() < 0 or reusable.personal.getCreditsDiff() < 0)
        self.getViewModel().setState(BonusStates(state))
        self.getViewModel().setLocalStorage(self.parentView.getLocalStorage())

    def _getEvents(self):
        return ((self.getViewModel().onPremiumXpBonusApplied, self.__onXpBonusApplied),
         (self.getViewModel().onLocalStorageUpdated, self.__onLocalStorageUpdated),
         (self.getViewModel().onShowDetails, self.__onShowDetails),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__wotPlusController.onDataChanged, self.__onWotPlusChanged),
         (self.__gameSession.onPremiumTypeChanged, self.__onPremiumStatusChanged))

    def _getListeners(self):
        return ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusStatusChanged),)

    def _getCallbacks(self):
        return (('stats.applyAdditionalXPCount', self.__onXpBonusStatusChanged), ('stats.applyAdditionalWoTPlusXPCount', self.__onXpBonusStatusChanged))

    def __onXpBonusApplied(self):
        self._battleResults.applyAdditionalBonus(self.arenaUniqueID)

    @server_settings.serverSettingsChangeListener(PremiumConfigs.DAILY_BONUS)
    def __onServerSettingsChanged(self, _):
        with self.getViewModel().transaction():
            self.packBattleResults(self.getBattleResults())

    def __onWotPlusChanged(self, data):
        if 'isEnabled' not in data:
            return
        with self.getViewModel().transaction():
            self.packBattleResults(self.getBattleResults())

    def __onPremiumStatusChanged(self, _=None):
        with self.getViewModel().transaction():
            self.packBattleResults(self.getBattleResults())

    def __onXpBonusStatusChanged(self, _=None):
        if not self._battleResults.isAddXPBonusApplied(self.arenaUniqueID):
            self.getViewModel().setRestriction(PremiumXpBonusRestriction.NOTAPPLYINGERROR)
        else:
            with self.getViewModel().transaction():
                self.packBattleResults(self.getBattleResults())

    def __onLocalStorageUpdated(self, event):
        ctx = event.get('localStorage', '')
        self.parentView.saveLocalStorage(ctx)

    def __onShowDetails(self, _=None):
        bonusState = self.getViewModel().getState()
        if bonusState == BonusStates.PLUSEARNINGS:
            url = getWotPlusShopUrl()
            BigWorld.callback(0.0, partial(showShop, url))
        elif bonusState in (BonusStates.PREMIUMEARNINGS, BonusStates.PREMIUMADVERTISING, BonusStates.PREMIUMINFO):
            url = getBuyPremiumUrl()
            BigWorld.callback(0.0, partial(showShop, url))
        elif bonusState == BonusStates.PLUSINFO:
            showDailyExpPageView()


class FinancialReportSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return FinancialReportModel

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        CrystalsDetailsPacker.packModel(viewModel.crystals, CurrencyRecordsItemModel.CRYSTAL, battleResults)
        XpDetailsPacker.packModel(viewModel.xp, CurrencyRecordsItemModel.XP_COST, battleResults)
        FreeXpDetailsPacker.packModel(viewModel.freeXp, CurrencyRecordsItemModel.FREE_XP, battleResults)
        CreditsStatisticsPacker.packModel(viewModel.credits, CurrencyRecordsItemModel.CREDITS, battleResults)
        GoldStatisticsPacker.packModel(viewModel.gold, CurrencyRecordsItemModel.GOLD, battleResults)

    def _getListeners(self):
        return ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusStatusChanged),)

    def _getCallbacks(self):
        return (('stats.applyAdditionalXPCount', self.__onXpBonusStatusChanged), ('stats.applyAdditionalWoTPlusXPCount', self.__onXpBonusStatusChanged))

    def __onXpBonusStatusChanged(self, _=None):
        with self.getViewModel().transaction():
            self.packBattleResults(self.getBattleResults())
