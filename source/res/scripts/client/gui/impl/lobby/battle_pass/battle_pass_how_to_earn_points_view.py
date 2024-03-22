# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_how_to_earn_points_view.py
import logging
import itertools
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import Array, ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_how_to_earn_points_view_model import BattlePassHowToEarnPointsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_card_model import GameModeCardModel, PointsCardType
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_cell_model import GameModeCellModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_model import GameModeModel, ArenaBonusType
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_item_model import VehicleItemModel
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
REVERSE_GAME_MODE_ORDER = (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO,
 ARENA_BONUS_TYPE.EPIC_BATTLE,
 ARENA_BONUS_TYPE.COMP7,
 ARENA_BONUS_TYPE.REGULAR)
REVERSE_GAME_MODE_ORDER_MAP = {bonusType:idx for idx, bonusType in enumerate(REVERSE_GAME_MODE_ORDER)}
_rBattlePass = R.strings.battle_pass
_logger = logging.getLogger(__name__)

class BattlePassHowToEarnPointsView(ViewImpl):
    __slots__ = ('__chapterID',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, layoutID, chapterID):
        settings = ViewSettings(layoutID)
        settings.model = BattlePassHowToEarnPointsViewModel()
        self.__chapterID = chapterID
        super(BattlePassHowToEarnPointsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassHowToEarnPointsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassHowToEarnPointsView, self)._onLoading(*args, **kwargs)
        self.__createGeneralModel()

    def __getGameMode(self, arenaType):
        return self.__createBattleRoyalGameModel() if arenaType == ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO else self.__createGameModel(arenaType)

    def __createGeneralModel(self):
        with self.viewModel.transaction() as model:
            model.getGameModes().clear()
            gameModeModels = Array()
            for arenaType in sorted(self.__battlePass.getVisibleGameModes(), key=REVERSE_GAME_MODE_ORDER_MAP.get, reverse=True):
                if any((bonusType.value == arenaType for bonusType in ArenaBonusType.__members__.values())):
                    gameModeModels.addViewModel(self.__getGameMode(arenaType))
                _logger.error('ArenaBonusType %s is not supported in BattlePassHowToEarnPointsView', arenaType)

            model.setGameModes(gameModeModels)
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)
            model.setChapterID(self.__chapterID)

    def __createGameModel(self, gameType):
        viewModel = self.__createViewHeader(gameType)
        self.__createTable(gameType, viewModel)
        self.__createCardsModel(gameType, viewModel)
        return viewModel

    def __createBattleRoyalGameModel(self):
        viewModel = self.__createViewHeader(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO)
        self.__createBattleRoyalTable(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, viewModel)
        self.__createBattleRoyalCardsModel(viewModel)
        return viewModel

    @staticmethod
    def __createViewHeader(gameType):
        viewModel = GameModeModel()
        viewModel.setArenaBonusType(ArenaBonusType(gameType))
        viewModel.setTitle(backport.text(_rBattlePass.howToEarnPoints.battleTypeTitle.num(gameType)()))
        viewModel.setText(backport.text(_rBattlePass.howToEarnPoints.text.num(gameType)()))
        return viewModel

    def __createBattleRoyalTable(self, gameType, viewModel):
        self.__createBattleRoyalTableHeader(gameType, viewModel)
        previousLevelSolo = 1
        previousLevelSquad = 1
        for pointsSolo, pointsSquad in itertools.izip_longest(self.__battlePass.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO), self.__battlePass.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD), fillvalue=0):
            cellSoloPoints = GameModeCellModel()
            if pointsSolo == 0:
                cellLabelSolo, cellSoloPoints = self.__createEmptyCell()
            else:
                cellLabelSolo, previousLevelSolo = self.__createCellName(gameType, pointsSolo, previousLevelSolo, viewModel)
                cellSoloPoints.setPoints(pointsSolo.points)
            cellSquadPoints = GameModeCellModel()
            if pointsSquad == 0:
                cellLabelSquad, cellSquadPoints = self.__createEmptyCell()
            else:
                cellLabelSquad, previousLevelSquad = self.__createCellName(gameType, pointsSquad, previousLevelSquad, viewModel)
                cellSquadPoints.setPoints(pointsSquad.points)
            tableRow = GameModeRowsModel()
            tableRow.getCell().addViewModel(cellLabelSolo)
            tableRow.getCell().addViewModel(cellSoloPoints)
            tableRow.getCell().addViewModel(cellLabelSquad)
            tableRow.getCell().addViewModel(cellSquadPoints)
            viewModel.getTableRows().addViewModel(tableRow)

    @staticmethod
    def __createCellName(gameType, points, previousLevel, viewModel):
        cell = GameModeCellModel()
        if points.label - previousLevel > 0:
            cell.setText(backport.text(_rBattlePass.howToEarnPoints.rangeLevels.num(gameType)(), startLevel=previousLevel, endLevel=points.label))
        else:
            cell.setText(backport.text(_rBattlePass.howToEarnPoints.singleLevel.num(gameType)(), level=points.label))
        previousLevel = points.label + 1
        return (cell, previousLevel)

    @staticmethod
    def __createEmptyCell():
        cellLabel = GameModeCellModel()
        cellPoints = GameModeCellModel()
        cellLabel.setText('')
        cellPoints.setPoints(0)
        return (cellLabel, cellPoints)

    def __createTable(self, gameType, viewModel):
        self.__createTableHeader(gameType, viewModel)
        for points in self.__battlePass.getPerBattlePoints(gameMode=gameType):
            cellLabel = GameModeCellModel()
            cellLabel.setText(backport.text(_rBattlePass.howToEarnPoints.rating.num(gameType)(), level=points.label))
            cellWinPoints = GameModeCellModel()
            cellWinPoints.setPoints(points.winPoint)
            cellLosePoints = GameModeCellModel()
            cellLosePoints.setPoints(points.losePoint)
            tableRow = GameModeRowsModel()
            tableRow.getCell().addViewModel(cellLabel)
            tableRow.getCell().addViewModel(cellWinPoints)
            tableRow.getCell().addViewModel(cellLosePoints)
            viewModel.getTableRows().addViewModel(tableRow)

    @staticmethod
    def __createBattleRoyalTableHeader(battleType, viewModel):
        cellLabelSolo = GameModeCellModel()
        cellLabelSolo.setText(backport.text(_rBattlePass.howToEarnPoints.solo.num(battleType)()))
        cellSoloPoints = GameModeCellModel()
        cellSoloPoints.setText('')
        cellLabelSquad = GameModeCellModel()
        cellLabelSquad.setText(backport.text(_rBattlePass.howToEarnPoints.squad.num(battleType)()))
        cellSquadPoints = GameModeCellModel()
        cellSquadPoints.setText('')
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabelSolo)
        tableRow.getCell().addViewModel(cellSoloPoints)
        tableRow.getCell().addViewModel(cellLabelSquad)
        tableRow.getCell().addViewModel(cellSquadPoints)
        viewModel.getTableRows().addViewModel(tableRow)

    @staticmethod
    def __createTableHeader(gameType, viewModel):
        cellLabel = GameModeCellModel()
        cellLabel.setText('')
        cellWinPoints = GameModeCellModel()
        cellWinPoints.setText(backport.text(_rBattlePass.howToEarnPoints.win.num(gameType)()))
        cellLosePoints = GameModeCellModel()
        cellLosePoints.setText(backport.text(_rBattlePass.howToEarnPoints.lose.num(gameType)()))
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabel)
        tableRow.getCell().addViewModel(cellWinPoints)
        tableRow.getCell().addViewModel(cellLosePoints)
        viewModel.getTableRows().addViewModel(tableRow)

    def __createCardsModel(self, gameType, viewModel):
        if gameType == ARENA_BONUS_TYPE.REGULAR:
            self.__createRandomCardsModel(gameType, viewModel)
        elif gameType == ARENA_BONUS_TYPE.RANKED:
            self.__createRankedCardsModel(viewModel, ARENA_BONUS_TYPE.RANKED)
        elif gameType == ARENA_BONUS_TYPE.EPIC_BATTLE:
            self.__createEpicBattleCardsModel(viewModel)
        elif gameType == ARENA_BONUS_TYPE.COMP7:
            self.__createComp7CardsModel(gameType, viewModel)

    def __createRankedCardsModel(self, viewModel, gameType):
        self.__createSpecialVehCard(viewModel, gameType)
        self.__createLimitCard(viewModel)

    def __createEpicBattleCardsModel(self, viewModel):
        self.__createEpicBattlePointsCard(viewModel)

    def __createComp7CardsModel(self, gameType, viewModel):
        self.__createSpecialVehCard(viewModel, gameType)
        self.__createDailyCard(gameType, viewModel, PointsCardType.COMP7)

    def __createRandomCardsModel(self, gameType, viewModel):
        self.__createSpecialVehCard(viewModel, gameType)
        self.__createLimitCard(viewModel)
        self.__createDailyCard(gameType, viewModel)

    @staticmethod
    def __createDailyCard(gameType, viewModel, pointsCardType=PointsCardType.DAILY):
        gameModeCard = GameModeCardModel()
        gameModeCard.setCardType(pointsCardType)
        gameModeCard.setViewId(str(gameType))
        viewModel.getCards().addViewModel(gameModeCard)

    @staticmethod
    def __createLimitCard(viewModel):
        gameModeCard = GameModeCardModel()
        gameModeCard.setCardType(PointsCardType.LIMIT)
        viewModel.getCards().addViewModel(gameModeCard)

    @staticmethod
    def __createEpicBattlePointsCard(viewModel):
        gameModeCard = GameModeCardModel()
        gameModeCard.setCardType(PointsCardType.EPIC_BATTLE_POINTS)
        viewModel.getCards().addViewModel(gameModeCard)

    @staticmethod
    def __createBattleRoyalCardsModel(viewModel):
        gameModeCard = GameModeCardModel()
        gameModeCard.setCardType(PointsCardType.BATTLE)
        viewModel.getCards().addViewModel(gameModeCard)

    def __createSpecialVehCard(self, viewModel, gameType=ARENA_BONUS_TYPE.REGULAR):
        gameModeCard = GameModeCardModel()
        gameModeCard.setCardType(PointsCardType.TECH)
        specialTanksIntCDs = self.__battlePass.getSpecialVehicles()
        for specialTanksIntCD in specialTanksIntCDs:
            vehicle = self.__itemsCache.items.getItemByCD(specialTanksIntCD)
            pointsDiff = self.__battlePass.getPointsDiffForVehicle(specialTanksIntCD, gameMode=gameType)
            if vehicle is None or pointsDiff.textID == 0:
                _logger.warning('No vehicle or points data found for CD: %s', str(specialTanksIntCD))
                continue
            item = VehicleItemModel()
            item.setVehicleType(vehicle.type)
            item.setVehicleLevel(vehicle.level)
            item.setVehicleName(vehicle.userName)
            item.setVehicleBonus(pointsDiff.bonus)
            item.setVehicleTop(pointsDiff.top)
            item.setTextResource(backport.text(pointsDiff.textID))
            item.setIsElite(vehicle.isElite)
            gameModeCard.getVehiclesList().addViewModel(item)

        viewModel.getCards().addViewModel(gameModeCard)
        return

    def _getEvents(self):
        return ((self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChange), (self.__battlePass.onSeasonStateChanged, self.__onSeasonStateChanged), (self.viewModel.onLinkClick, self.__onLinkClick))

    def __onLinkClick(self, args):
        viewModel = args.get('viewId')
        if int(viewModel) == ARENA_BONUS_TYPE.REGULAR:
            showDailyQuests(subTab=DailyTabs.QUESTS)
        self.destroyWindow()

    def __onBattlePassSettingsChange(self, *_):
        if self.__battlePass.isVisible() and not self.__battlePass.isPaused():
            self.__createGeneralModel()
        elif self.__battlePass.isPaused():
            self.destroyWindow()
        else:
            showHangar()

    def __onSeasonStateChanged(self):
        if not self.__battlePass.isActive():
            showHangar()


class BattlePassHowToEarnPointsWindow(LobbyWindow):

    def __init__(self, parent=None, chapterID=0):
        super(BattlePassHowToEarnPointsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattlePassHowToEarnPointsView(R.views.lobby.battle_pass.BattlePassHowToEarnPointsView(), chapterID))
