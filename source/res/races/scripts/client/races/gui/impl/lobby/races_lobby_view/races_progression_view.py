# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_lobby_view/races_progression_view.py
import logging
import typing
from races.gui.impl.gen.view_models.views.lobby.races_progression_view_model import RacesProgressionViewModel
from races.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers import time_utils
from races.skeletons.progression_controller import IRacesProgressionController
from skeletons.gui.game_control import IRacesBattleController
from skeletons.gui.impl import IGuiLoader
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui import GUI_SETTINGS
from helpers.CallbackDelayer import CallbackDelayer
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from ui_packers import fillQuestsModel, getRacesBonusPacker
from gui.impl.lobby.loot_box.loot_box_helper import getKeyByID
from gui.impl.gen import R
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, TypeVar, Optional
    from gui.server_events.bonuses import TokensBonus
    TokenBonusType = TypeVar('TokenBonusType', bound=TokensBonus)
_logger = logging.getLogger(__name__)

class RacesProgressionView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__currentRoute', '_previouslySeenPoints', '__callbackDelayer', '__tooltipData')
    _racesController = dependency.descriptor(IRacesBattleController)
    _racesProgression = dependency.descriptor(IRacesProgressionController)
    _uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RacesProgressionViewModel()
        self.__tooltipData = {}
        super(RacesProgressionView, self).__init__(settings)
        self.__callbackDelayer = CallbackDelayer()

    @property
    def viewModel(self):
        return super(RacesProgressionView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        _logger.debug('[RacesProgressionView] initialize')
        super(RacesProgressionView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader()

    def _onLoading(self, *args, **kwargs):
        super(RacesProgressionView, self)._onLoading(*args, **kwargs)
        _logger.debug('[RacesProgressionView] loading')
        self._fillModel()

    def _onLoaded(self, *args, **kwargs):
        super(RacesProgressionView, self)._onLoaded(*args, **kwargs)
        _logger.debug('[RacesProgressionView] loaded')

    def _finalize(self):
        super(RacesProgressionView, self)._finalize()
        self.resumeLobbyHeader()
        _logger.debug('[RacesProgressionView] finalizing')

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose), (self._racesProgression.onProgressPointsUpdated, self._fillModel), (self.viewModel.onAboutEvent, self.onAboutEvent))

    def onClose(self):
        _logger.debug('[RacesLobbyView] close button clicked')
        self.closeProgressionWindow()
        self._racesController.selectRaces()
        self._racesController.openEventLobby()

    def onAboutEvent(self, *args, **kwargs):
        _logger.debug('[RacesProgressionView] info button clicked')
        self._showInfoPage()

    def _getInfoPageURL(self):
        return GUI_SETTINGS.infoPageRaces

    def _showInfoPage(self):
        url = self._getInfoPageURL()
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def closeProgressionWindow(self, *args, **kwargs):
        self.destroyWindow()

    def createToolTipContent(self, event, contentID):
        tooltipData = self.getTooltipData(event)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip() and tooltipData:
            lootBoxKeyID = tooltipData.get('lootBoxKeyID')
            lootBoxKey = getKeyByID(lootBoxKeyID)
            return LootboxKeyTooltip(lootBoxKey)
        return super(RacesProgressionView, self).createToolTipContent(event=event, contentID=contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RacesProgressionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            if isinstance(data, unicode):
                data = createTooltipData(tooltip=data)
            return data

    def _fillModel(self):
        points = self._racesProgression.getCurrentPoints()
        _logger.debug('[RacesProgressionView] filling model. points: ' + str(points))
        progression = self._racesProgression.getBonuses()
        self.__tooltipData = {}
        quests = self._racesProgression.collectSortedDailyQuests()
        with self.viewModel.transaction() as model:
            model.setPrevProgressPoints(self._racesProgression.getLastSeenPoints())
            model.setPointsForLevel(self._racesProgression.getPointsForLevel())
            self._racesProgression.updateLastSeenPoints()
            progressionLevels = model.getProgressLevels()
            progressionLevels.clear()
            progressionLevels.reserve(len(progression))
            for _, bonuses in progression:
                level = ProgressLevelModel()
                rewards = level.getRewards()
                packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getRacesBonusPacker())
                progressionLevels.addViewModel(level)

            progressionLevels.invalidate()
            model.setCurProgressPoints(points)
            endSeasonDateSeconds = self._racesController.getCurrentSeason().getEndDate()
            serverUTC = time_utils.getServerUTCTime()
            isLastDay = endSeasonDateSeconds - serverUTC < time_utils.ONE_DAY
            model.quests.setIsLastSeasonDay(isLastDay)
            model.quests.setExpirationTime(quests.values()[0].getProgressExpiryTime() - serverUTC if len(quests) else 0)
            fillQuestsModel(model.quests.getMissions(), quests, self.__tooltipData)
