# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/presenter.py
import logging
import typing
from gui.battle_results.br_helper import BattleResultData
from gui.battle_results.presenter.achievements import getAchievementTooltipArgs
from gui.battle_results.presenter.common import getPremiumBenefits, setUserStatus, setAccountType, setArenaType
from gui.battle_results.presenter.detail_stats import updateDetailedStatsXP
from gui.battle_results.presenter.events import setEventsData
from gui.battle_results.presenter.tooltips.currency_tooltips import setFinancialData
from gui.battle_results.presenter import personal
from gui.battle_results.presenter.tooltips.efficiency_tooltips import setPersonalEfficiencyTooltipData, getTeamEfficiencyTooltipData, TeamEfficiencyTooltipData, getTotalEfficiencyTooltipData
from gui.battle_results.presenter.getter import createFieldsGetter
from gui.battle_results.presenter.team_stats import setTeamStatsData
from gui.impl.gen.view_models.views.lobby.postbattle.postbattle_screen_model import PostbattleScreenModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.tooltip_efficiency_model import TooltipEfficiencyModel
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.financial_tooltip_model import FinancialTooltipModel
_logger = logging.getLogger(__name__)

class DataPresenter(object):
    __slots__ = ('__battleResults', '__fieldsGetter', '__cachedSettings')
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(DataPresenter, self).__init__()
        self.__battleResults = {}
        self.__cachedSettings = {}
        self.__fieldsGetter = None
        return

    @property
    def __getter(self):
        if self.__fieldsGetter is None:
            self.__fieldsGetter = createFieldsGetter()
        return self.__fieldsGetter

    def fini(self):
        self.__cachedSettings = None
        return

    def clear(self):
        self.__battleResults = {}
        if self.__fieldsGetter is not None:
            self.__fieldsGetter.clear()
            self.__fieldsGetter = None
        return

    def addBattleResult(self, reusableInfo, result):
        arenaID = reusableInfo.arenaUniqueID
        if self.__getBattleResult(arenaID):
            _logger.warning('Arena info with UniqueID = %i is already added', arenaID)
        else:
            self.__battleResults[arenaID] = BattleResultData(reusableInfo, result)
            self.__saveSettings(arenaID)

    def updateBattleResult(self, reusableInfo, result):
        arenaID = reusableInfo.arenaUniqueID
        self.__battleResults[arenaID] = BattleResultData(reusableInfo, result)

    def setDataToModel(self, model, arenaUniqueID, tooltipData):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        personal.setPersonalData(model.common, self.__cachedSettings.get(arenaUniqueID), *battleResult)
        setTeamStatsData(model.team, self.__getter, *battleResult)
        setUserStatus(model.userStatus, *battleResult)
        setEventsData(model.events, tooltipData=tooltipData, *battleResult)
        setAccountType(model, *battleResult)
        setArenaType(model, *battleResult)
        personal.setWidgetsData(model.widgets, *battleResult)
        return

    def setEfficiencyTooltipData(self, model, arenaUniqueID, efficiencyType):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        setPersonalEfficiencyTooltipData(model, efficiencyType, battleResult)
        return

    def getEfficiencyTooltipData(self, arenaUniqueID, parameterName, enemyVehicleID=0):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        return getTeamEfficiencyTooltipData(parameterName, enemyVehicleID, battleResult)

    def getTotalEfficiencyTooltipData(self, arenaUniqueID, parameterName):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        return getTotalEfficiencyTooltipData(parameterName, battleResult)

    def getAchievementTooltipData(self, arenaUniqueID, achievementID, achievementName, isPersonal):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        return getAchievementTooltipArgs(achievementID, achievementName, isPersonal, battleResult)

    def setFinancialTooltipData(self, model, arenaUniqueID, currencyType):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        reusable, _ = battleResult
        setFinancialData(model, self.__getter, reusable, currencyType)
        return

    def updatePremiumBonus(self, model, arenaUniqueID):
        reusable, _ = self.__getBattleResult(arenaUniqueID)
        personal.updatePremiumData(model.common.rewards, reusable, self.__cachedSettings.get(arenaUniqueID))
        updateDetailedStatsXP(model.details, reusable, self.__getter)

    def getPremiumBenefits(self):
        return getPremiumBenefits(self.__getter)

    def updatePremiumState(self, model, arenaUniqueID):
        reusable, _ = self.__getBattleResult(arenaUniqueID)
        personal.updatePremiumState(model.common.rewards, reusable, self.__cachedSettings.get(arenaUniqueID))

    def updateTime(self, model, arenaUniqueID):
        if arenaUniqueID not in self.__battleResults:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        reusable, _ = self.__getBattleResult(arenaUniqueID)
        personal.updateCurrentTime(model.common, reusable)

    def getArenaGuiType(self, arenaUniqueID):
        battleResult = self.__getBattleResult(arenaUniqueID)
        if battleResult is None:
            raise SoftException('Arena info with UniqueID = {} not found'.format(arenaUniqueID))
        return battleResult.reusable.common.arenaGuiType

    def __getBattleResult(self, arenaUniqueID):
        return self.__battleResults.get(arenaUniqueID)

    def __saveSettings(self, arenaUniqueID):
        if arenaUniqueID not in self.__cachedSettings:
            additionalBonusConfig = self.__lobbyContext.getServerSettings().getAdditionalBonusConfig()
            self.__cachedSettings[arenaUniqueID] = {'additionalBonusMultiplier': additionalBonusConfig.get('bonusFactor', 0)}
