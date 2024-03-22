# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/info_page.py
import itertools
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.impl.gen import R
from battle_royale.gui.impl.gen.view_models.views.lobby.views.info_page_model import InfoPageModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.game_mode_model import GameModeModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_cell_model import GameModeCellModel
from gui.impl import backport
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from battle_royale.gui.shared.tooltips.helper import fillProgressionPointsTableModel
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from gui.shared.event_dispatcher import showBrowserOverlayView
from constants import ARENA_BONUS_TYPE
from skeletons.gui.game_control import IBattlePassController
_rBattleRoyale = R.strings.battle_royale_infopage.battleTypes

class InfoPage(ViewImpl):
    __battleRoyaleCtrl = dependency.descriptor(IBattleRoyaleController)
    __battlePassCtrl = dependency.descriptor(IBattlePassController)
    __slots__ = ('_webBridgeUrl', '_isModeSelector')

    def __init__(self, isModeSelector):
        settings = ViewSettings(R.views.battle_royale.lobby.views.InfoPage())
        settings.model = InfoPageModel()
        self._webBridgeUrl = self.__battleRoyaleCtrl.getIntroVideoURL()
        self._isModeSelector = isModeSelector
        super(InfoPage, self).__init__(settings)

    @property
    def viewModel(self):
        return super(InfoPage, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(InfoPage, self)._onLoading(args, kwargs)
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillSeasonDateModel(tx)
            tx.setIsModeSelector(self._isModeSelector)
            fillProgressionPointsTableModel(tx.modesSH, self.__battleRoyaleCtrl.getProgressionPointsTableData(), _rBattleRoyale)
            if self.__battlePassCtrl.isEnabled() and self.__battlePassCtrl.isVisible():
                tx.getModesBP().addViewModel(self.__createBattlePassTable())

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._onClose
        self.viewModel.onOpenVideo += self._onOpenVideo

    def _finalize(self):
        self.viewModel.onClose -= self._onClose
        self.viewModel.onOpenVideo -= self._onOpenVideo

    def _onClose(self):
        self.destroyWindow()

    def _onOpenVideo(self):
        showBrowserOverlayView(self._webBridgeUrl, BATTLEROYALE_ALIASES.BATTLE_ROYALE_BROWSER_VIEW, forcedSkipEscape=True)

    def __fillSeasonDateModel(self, viewModel):
        currentSeason = self.__battleRoyaleCtrl.getCurrentSeason() or self.__battleRoyaleCtrl.getNextSeason()
        if currentSeason is not None:
            viewModel.setStartDate(currentSeason.getStartDate())
            viewModel.setEndDate(currentSeason.getEndDate())
        return

    def __createBattlePassTable(self):
        viewModel = GameModeModel()
        self.__createTableHeader(viewModel)
        previousLevelSolo = 1
        previousLevelSquad = 1
        for pointsSolo, pointsSquad in itertools.izip_longest(self.__battlePassCtrl.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, needPlacesWithoutPoints=True), self.__battlePassCtrl.getPerBattleRoyalePoints(gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, needPlacesWithoutPoints=True), fillvalue=0):
            cellSoloPoints = GameModeCellModel()
            if pointsSolo == 0:
                cellLabelSolo, cellSoloPoints = self.__createEmptyCell()
            else:
                cellLabelSolo, previousLevelSolo = self.__createCellName(pointsSolo, previousLevelSolo)
                cellSoloPoints.setPoints(pointsSolo.points)
            cellSquadPoints = GameModeCellModel()
            if pointsSquad == 0:
                cellLabelSquad, cellSquadPoints = self.__createEmptyCell()
            else:
                cellLabelSquad, previousLevelSquad = self.__createCellName(pointsSquad, previousLevelSquad)
                cellSquadPoints.setPoints(pointsSquad.points)
            tableRow = GameModeRowsModel()
            tableRow.getCell().addViewModel(cellLabelSolo)
            tableRow.getCell().addViewModel(cellSoloPoints)
            tableRow.getCell().addViewModel(cellLabelSquad)
            tableRow.getCell().addViewModel(cellSquadPoints)
            viewModel.getTableRows().addViewModel(tableRow)

        return viewModel

    @staticmethod
    def __createCellName(points, previousLevel):
        cell = GameModeCellModel()
        if points.label - previousLevel > 0:
            numRange = (previousLevel, points.label)
            cell.setText(backport.text(_rBattleRoyale.text.places(), place='-'.join(map(str, numRange))))
        else:
            cell.setText(backport.text(_rBattleRoyale.text.place(), place=points.label))
        previousLevel = points.label + 1
        return (cell, previousLevel)

    @staticmethod
    def __createEmptyCell():
        cellLabel = GameModeCellModel()
        cellPoints = GameModeCellModel()
        cellLabel.setText('')
        cellPoints.setPoints(0)
        return (cellLabel, cellPoints)

    @staticmethod
    def __createTableHeader(viewModel):
        cellLabelSolo = GameModeCellModel()
        cellLabelSolo.setText(backport.text(_rBattleRoyale.battleTypesHeader.num(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO)()))
        cellSoloPoints = GameModeCellModel()
        cellSoloPoints.setText('')
        cellLabelSquad = GameModeCellModel()
        cellLabelSquad.setText(backport.text(_rBattleRoyale.battleTypesHeader.num(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)()))
        cellSquadPoints = GameModeCellModel()
        cellSquadPoints.setText('')
        tableRow = GameModeRowsModel()
        tableRow.getCell().addViewModel(cellLabelSolo)
        tableRow.getCell().addViewModel(cellSoloPoints)
        tableRow.getCell().addViewModel(cellLabelSquad)
        tableRow.getCell().addViewModel(cellSquadPoints)
        viewModel.getTableRows().addViewModel(tableRow)


class InfoPageWindow(LobbyWindow):

    def __init__(self, isModeSelector):
        super(InfoPageWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=InfoPage(isModeSelector))
