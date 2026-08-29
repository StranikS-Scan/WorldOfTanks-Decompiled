# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_how_to_earn_points_view.py
from __future__ import absolute_import
import logging
from future.moves import itertools
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_how_to_earn_points_view_model import BattlePassHowToEarnPointsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_cell_model import GameModeCellModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_model import ArenaBonusType, GameModeModel, PointsCardType
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel
from gui.impl.lobby.user_missions.hub.hub_view import DailyTabs
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.event_dispatcher import showHangar, showShop
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusProShopUrl
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.battle_pass.battle_pass_wot_plus import getWotPlusPerBattlePoints, getWotPlusBattlePassTier, isWotPlusBattlePassAvailableForAnyTier, getMergedWotPlusPointsList, extractMinValueFromRange
REVERSE_GAME_MODE_ORDER = (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO,
 ARENA_BONUS_TYPE.COMP7_LIGHT,
 ARENA_BONUS_TYPE.COMP7,
 ARENA_BONUS_TYPE.EPIC_BATTLE,
 ARENA_BONUS_TYPE.REGULAR)
REVERSE_GAME_MODE_ORDER_MAP = {bonusType:idx for idx, bonusType in enumerate(REVERSE_GAME_MODE_ORDER)}
_rBattlePass = R.strings.battle_pass
_logger = logging.getLogger(__name__)

class BattlePassHowToEarnPointsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, chapterID=0):
        settings = ViewSettings(R.views.mono.battle_pass.how_to_earn_points())
        settings.model = BattlePassHowToEarnPointsViewModel()
        self.__chapterID = chapterID
        super(BattlePassHowToEarnPointsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassHowToEarnPointsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassHowToEarnPointsView, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        self.__createGeneralModel()

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        super(BattlePassHowToEarnPointsView, self)._finalize()

    def _getEvents(self):
        return ((self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChange), (self.viewModel.onGoToMissions, self.__goToMissions), (self.viewModel.onWotPlusClick, self.__goToWotPlus))

    def __getGameMode(self, arenaType):
        return self.__createBattleRoyalGameModel() if arenaType == ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO else self.__createGameModel(arenaType)

    def __createGeneralModel(self):
        with self.viewModel.transaction() as model:
            gameModes = model.getGameModes()
            gameModes.clear()
            for arenaType in sorted(self.__battlePass.getVisibleGameModes(), key=REVERSE_GAME_MODE_ORDER_MAP.get, reverse=True):
                if any((bonusType.value == arenaType for bonusType in ArenaBonusType.__members__.values())):
                    gameModes.addViewModel(self.__getGameMode(arenaType))
                _logger.error('ArenaBonusType %s is not supported in BattlePassHowToEarnPointsView', arenaType)

            gameModes.invalidate()
            model.setChapterID(self.__chapterID)
            model.setIsWotPlusShown(isWotPlusBattlePassAvailableForAnyTier())

    def __createGameModel(self, gameType):
        viewModel = GameModeModel()
        viewModel.setArenaBonusType(ArenaBonusType(gameType))
        self.__createConditionsTable(gameType, viewModel)
        self.__createVehiclesTable(gameType, viewModel)
        self.__createCardsModel(gameType, viewModel)
        return viewModel

    def __createBattleRoyalGameModel(self):
        viewModel = GameModeModel()
        viewModel.setArenaBonusType(ArenaBonusType.BATTLE_ROYALE_SOLO)
        self.__createBattleRoyalConditionsTable(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, viewModel)
        return viewModel

    def __createBattleRoyalConditionsTable(self, gameType, viewModel):
        self.__createBattleRoyalTableHeader(gameType, viewModel)
        previousLevelSolo = 1
        previousLevelSquad = 1
        availableBPTier = getWotPlusBattlePassTier()
        wpWinMergedPointsSolo = getMergedWotPlusPointsList(availableBPTier, ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO)
        wpWinMergedPointsSquad = getMergedWotPlusPointsList(availableBPTier, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)
        for pointsSolo, pointsSquad in itertools.zip_longest(self.__battlePass.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO), self.__battlePass.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD), fillvalue=0):
            previousLevelSolo, soloTableRow = self.__createBattleRoyaleConditionRow(pointsSolo, previousLevelSolo, wpWinMergedPointsSolo)
            viewModel.battleRoyaleCondtions.getSolo().addViewModel(soloTableRow)
            previousLevelSquad, squadTableRow = self.__createBattleRoyaleConditionRow(pointsSquad, previousLevelSquad, wpWinMergedPointsSquad)
            viewModel.battleRoyaleCondtions.getSquad().addViewModel(squadTableRow)

    def __createBattleRoyaleConditionRow(self, points, previousLevel, wpWinMergedPoints):
        pointsCell = GameModeCellModel()
        labelCell = GameModeCellModel()
        if points > 0:
            pointsCell.setExternalPoints(extractMinValueFromRange(previousLevel - 1, points.label, wpWinMergedPoints))
            pointsCell.setPoints(points.points)
            labelCell.setText(backport.text(_rBattlePass.howToEarnPoints.rating(), place=points.label))
            previousLevel = points.label + 1
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(labelCell)
        tableRow.getCell().addViewModel(pointsCell)
        return (previousLevel, tableRow)

    def __createConditionsTable(self, gameType, viewModel):
        self.__createTableHeader(gameType, viewModel)
        availableBPTier = getWotPlusBattlePassTier()
        for points in self.__battlePass.getPerBattlePoints(gameMode=gameType):
            cellLabel = GameModeCellModel()
            cellLabel.setText(backport.text(_rBattlePass.howToEarnPoints.rating(), place=points.label))
            wpWinPoints, wpLossPoints = getWotPlusPerBattlePoints(points.label, availableBPTier, bonusType=gameType)
            cellWinPoints = GameModeCellModel()
            cellWinPoints.setPoints(points.winPoint)
            cellWinPoints.setExternalPoints(wpWinPoints)
            cellLosePoints = GameModeCellModel()
            cellLosePoints.setPoints(points.losePoint)
            cellLosePoints.setExternalPoints(wpLossPoints)
            tableRow = GameModeRowsModel()
            tableRow.getCell().addViewModel(cellLabel)
            tableRow.getCell().addViewModel(cellWinPoints)
            tableRow.getCell().addViewModel(cellLosePoints)
            viewModel.getConditions().addViewModel(tableRow)

    @staticmethod
    def __createBattleRoyalTableHeader(gameType, viewModel):
        cellLabel = GameModeCellModel()
        cellLabel.setText(backport.text(_rBattlePass.howToEarnPoints.condition.num(gameType, _rBattlePass.howToEarnPoints.condition.default)()))
        cellPoints = GameModeCellModel()
        cellPoints.setText(backport.text(_rBattlePass.howToEarnPoints.points()))
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabel)
        tableRow.getCell().addViewModel(cellPoints)
        viewModel.battleRoyaleCondtions.getSolo().addViewModel(tableRow)
        viewModel.battleRoyaleCondtions.getSquad().addViewModel(tableRow)

    @staticmethod
    def __createTableHeader(gameType, viewModel):
        cellLabel = GameModeCellModel()
        cellLabel.setText(backport.text(_rBattlePass.howToEarnPoints.condition.num(gameType, _rBattlePass.howToEarnPoints.condition.default)()))
        cellWinPoints = GameModeCellModel()
        cellWinPoints.setText(backport.text(_rBattlePass.howToEarnPoints.win.num(gameType)()))
        cellLosePoints = GameModeCellModel()
        cellLosePoints.setText(backport.text(_rBattlePass.howToEarnPoints.lose.num(gameType)()))
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabel)
        tableRow.getCell().addViewModel(cellWinPoints)
        tableRow.getCell().addViewModel(cellLosePoints)
        viewModel.getConditions().addViewModel(tableRow)

    def __createCardsModel(self, gameType, viewModel):
        cards = viewModel.getCards()
        cards.clear()
        if gameType == ARENA_BONUS_TYPE.REGULAR:
            cards.addNumber(PointsCardType.LIMIT.value)
            cards.addNumber(PointsCardType.DAILY.value)
        elif gameType == ARENA_BONUS_TYPE.EPIC_BATTLE:
            cards.addNumber(PointsCardType.LIMIT.value)
        elif gameType in (ARENA_BONUS_TYPE.COMP7, ARENA_BONUS_TYPE.COMP7_LIGHT):
            cards.addNumber(PointsCardType.DAILY.value)

    @staticmethod
    def __createVehiclesHeader(gameType, viewModel):
        cellLabel = GameModeCellModel()
        cellLabel.setText(backport.text(_rBattlePass.howToEarnPoints.vehicle()))
        cellResult = GameModeCellModel()
        cellResult.setText(backport.text(_rBattlePass.howToEarnPoints.condition.num(gameType, _rBattlePass.howToEarnPoints.condition.default)()))
        cellExtraPoints = GameModeCellModel()
        cellExtraPoints.setText(backport.text(_rBattlePass.howToEarnPoints.extraPoints()))
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabel)
        tableRow.getCell().addViewModel(cellResult)
        tableRow.getCell().addViewModel(cellExtraPoints)
        viewModel.getVehicles().addViewModel(tableRow)

    def __createVehiclesTable(self, gameType, viewModel):
        specialVehicleIntCDs = self.__battlePass.getSpecialVehicles(gameType)
        if not specialVehicleIntCDs:
            return
        self.__createVehiclesHeader(gameType, viewModel)
        vehicles = {}
        for specialVehicleIntCD in specialVehicleIntCDs:
            pointsDiff = self.__battlePass.getPointsDiffForVehicle(specialVehicleIntCD, gameMode=gameType)
            if pointsDiff.textID == 0:
                _logger.warning('No points data found for CD: %s', str(specialVehicleIntCD))
                continue
            vehicles[specialVehicleIntCD] = pointsDiff

        for specialVehicleIntCD, pointsDiff in sorted(vehicles.items(), key=lambda item: item[1].top):
            vehicle = self.__itemsCache.items.getItemByCD(specialVehicleIntCD)
            vehicleCell = GameModeCellModel()
            fillVehicleInfo(vehicleCell.vehicleInfo, vehicle)
            condition = GameModeCellModel()
            condition.setText(backport.text(_rBattlePass.howToEarnPoints.rating(), place=pointsDiff.top))
            extraPoints = GameModeCellModel()
            extraPoints.setExternalPoints(pointsDiff.bonus)
            tableRow = GameModeRowsModel()
            tableRow.getCell().addViewModel(vehicleCell)
            tableRow.getCell().addViewModel(condition)
            tableRow.getCell().addViewModel(extraPoints)
            viewModel.getVehicles().addViewModel(tableRow)

    def __goToMissions(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)

    def __goToWotPlus(self):
        showShop(getWotPlusProShopUrl())

    def __onBattlePassSettingsChange(self, *_):
        if self.__battlePass.isVisible() and not self.__battlePass.isPaused():
            self.__createGeneralModel()
        elif self.__battlePass.isPaused():
            self.destroyWindow()
        else:
            showHangar()


class BattlePassHowToEarnPointsWindow(LobbyWindow):

    def __init__(self, chapterID=0):
        super(BattlePassHowToEarnPointsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattlePassHowToEarnPointsView(chapterID))
