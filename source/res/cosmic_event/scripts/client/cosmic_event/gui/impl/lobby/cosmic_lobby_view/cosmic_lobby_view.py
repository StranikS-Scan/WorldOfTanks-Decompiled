# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_lobby_view/cosmic_lobby_view.py
import logging
import typing
from cosmic_event.gui.battle_results import CosmicBattleResultEvent
from cosmic_event_common.cosmic_event_common import ScoreEvents
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from helpers.CallbackDelayer import CallbackDelayer
from Event import Event
from adisp import adisp_process
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import CosmicLobbyViewModel, LobbyRouteEnum
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringTypeEnum
from cosmic_event.gui.impl.lobby.quest_helpers import fillDailyQuestModel, getDailyQuestModelFromQuest
from cosmic_event.gui.impl.lobby.quest_packer import DailyCosmicQuestUIDataPacker, getCosmicBonusPacker
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from cosmic_sound import CosmicHangarSounds
from debug_utils import LOG_ERROR
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, ViewStatus
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.event_dispatcher import showBrowserOverlayView, showShop
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getCosmic2024ShopUrl
from helpers import dependency, time_utils
from skeletons.gui.impl import INotificationWindowController, IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
if typing.TYPE_CHECKING:
    from typing import Tuple, Sequence, Callable, Optional, List, Dict
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.event_items import Quest
    from cosmic_event.gui.game_control.battle_controller import CosmicEventBattleController
    from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.progression_model import ProgressionModel
    from gui.shared.missions.packers.bonus import BonusUIPacker
_logger = logging.getLogger(__name__)
_SCORE_EVENTS_TO_MODEL_ENUM = {ScoreEvents.ARTIFACT_SCAN: ScoringTypeEnum.SCAN,
 ScoreEvents.KILL: ScoringTypeEnum.KILL,
 ScoreEvents.PICKUP: ScoringTypeEnum.PICKUP,
 ScoreEvents.RAMMING: ScoringTypeEnum.RAM,
 ScoreEvents.SHOT: ScoringTypeEnum.SHOT,
 ScoreEvents.ABILITY_HIT: ScoringTypeEnum.ABILITYHIT}
_SCORE_EVENTS_TO_ORDERED_LIST = [ScoreEvents.KILL,
 ScoreEvents.ARTIFACT_SCAN,
 ScoreEvents.PICKUP,
 ScoreEvents.RAMMING,
 ScoreEvents.SHOT,
 ScoreEvents.ABILITY_HIT]
COSMIC_SOUND_SPACE = CommonSoundSpaceSettings(name='hangar', entranceStates={'STATE_hangar_place': 'STATE_hangar_place_garage'}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

def _getScoreEventTypeEnum(eventName):
    return _SCORE_EVENTS_TO_MODEL_ENUM[ScoreEvents[eventName]]


def _getScoreEventListOrder(eventName):
    return _SCORE_EVENTS_TO_ORDERED_LIST.index(ScoreEvents[eventName])


class CosmicLobbyView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__tooltipData', '__currentRoute', '__callbackDelayer', '_previouslySeenPoints', '_postBattleOpenedAfterBattle', '_soundProgressionObject')
    _cosmicController = dependency.descriptor(ICosmicEventBattleController)
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _uiLoader = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = COSMIC_SOUND_SPACE

    def __init__(self, layoutID):
        _logger.debug('[CosmicLobbyView] created')
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CosmicLobbyViewModel()
        super(CosmicLobbyView, self).__init__(settings)
        self.__tooltipData = {}
        self.__currentRoute = self._cosmicController.getLobbyRoute()
        self.__callbackDelayer = CallbackDelayer()
        self._previouslySeenPoints = 0
        self._postBattleOpenedAfterBattle = False
        self._soundProgressionObject = None
        g_eventBus.addListener(CosmicBattleResultEvent.POST_BATTLE_SCREEN_OPENING, self._postBattleOpening, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @property
    def viewModel(self):
        return super(CosmicLobbyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CosmicLobbyView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            _logger.debug('tooltipId: %s, data: %s', tooltipId, data)
            return data

    def createToolTipContent(self, event, contentID):
        _logger.debug('CosmicLobbyView::createToolTipContent')
        if contentID == R.views.lobby.missions.DailyQuestsTooltip():
            missionId = event.getArgument('missionId')
            quests = self._cosmicProgression.getDailyQuests()
            quest = quests.get(missionId, None)
            if quest is None:
                return
            self._cosmicProgression.setQuestProgressAsViewed(quest)
            questUIPacker = DailyCosmicQuestUIDataPacker(quest)
            model = questUIPacker.pack()
            return ViewImpl(ViewSettings(R.views.lobby.missions.DailyQuestsTooltip(), model=model))
        else:
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
                tooltipId = event.getArgument('tooltipId')
                lootBoxIdStr = self.__tooltipData.get(tooltipId)
                if lootBoxIdStr:
                    lootBox = self._itemsCache.items.tokens.getLootBoxByID(int(lootBoxIdStr))
                    return LootboxTooltip(lootBox)
            return super(CosmicLobbyView, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, *args, **kwargs):
        super(CosmicLobbyView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader()

    def __onViewStatusChanged(self, uniqueID, newStatus):
        view = self._uiLoader.windowsManager.getView(uniqueID)
        postBattleLayoutID = R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView()
        if view and view.layoutID == postBattleLayoutID and self._postBattleOpenedAfterBattle:
            if self.viewModel.getLobbyRoute() == LobbyRouteEnum.ARTEFACT:
                if newStatus == ViewStatus.LOADING:
                    with self.viewModel.transaction() as model:
                        points = self._cosmicProgression.getLastSeenPoints() - 1
                        model.setArtefactProgressDeltaFrom(points)
                newStatus == ViewStatus.DESTROYING and self._cosmicProgression.updateLastSeenPoints(self._previouslySeenPoints)
                self._fillModel()
                self._cosmicProgression.updateLastSeenPoints()
                self._postBattleOpenedAfterBattle = False

    def _getEvents(self):
        return ((self.viewModel.onLobbyRouteChange, self.onLobbyRouteChange),
         (self.viewModel.onClose, self.onClose),
         (self.viewModel.onAboutEvent, self.onAboutEvent),
         (self.viewModel.onShopClicked, self.onShopClicked),
         (self._itemsCache.onSyncCompleted, self._onItemSyncCompleted),
         (self._cosmicProgression.onProgressPointsUpdated, self._fillModel),
         (self._cosmicController.onLobbyRouteChange, self.onLobbyRouteChangeImpl),
         (self._eventsCache.onSyncCompleted, self._onEventSyncCompleted),
         (self._uiLoader.windowsManager.onViewStatusChanged, self.__onViewStatusChanged))

    def _onLoading(self, *args, **kwargs):
        _logger.debug('[CosmicLobbyView] loading')
        super(CosmicLobbyView, self)._onLoading(*args, **kwargs)
        self._fillModel(self.__currentRoute)

    def _onLoaded(self, *args, **kwargs):
        super(CosmicLobbyView, self)._onLoaded(*args, **kwargs)
        self._notificationMgr.releasePostponed()
        self.__playProgressionSound()

    def _fillModel(self, newRoute=None):
        _logger.debug('[CosmicLobbyView] filling model, route %s', newRoute)
        with self.viewModel.transaction() as model:
            model.setLobbyRoute(newRoute or self.__currentRoute)
            currentPoints, currentStage, limitPoints = self._cosmicProgression.getProgression()
            lastSeenPoints = self._cosmicProgression.getLastSeenPoints()
            model.setMarsPoints(min(currentPoints, limitPoints))
            model.setMarsPointsLimit(limitPoints)
            model.setCurrentProgressSectionIndex(currentStage)
            model.setArtefactProgressDeltaFrom(lastSeenPoints)
            model.setFadeOut(False)
            _logger.debug('[marsProgression] earned: %s, limit: %s, stage %s, delta: %s', currentPoints, limitPoints, currentStage, currentPoints - lastSeenPoints)
            if newRoute == LobbyRouteEnum.ARTEFACT:
                self._cosmicProgression.updateLastSeenPoints()
                self._previouslySeenPoints = lastSeenPoints
                self._fillMissionsModel(model=model)
                self._fillScoreModel(model=model)
                self._fillProgression(model=model)
            self._updateVehicleState(model=model)

    def _fillProgression(self, model):
        packer = getCosmicBonusPacker()
        progression = self._cosmicProgression.getBonuses()
        progressionArray = model.getProgression()
        progressionArray.clear()
        progressionArray.reserve(len(progression))
        self.__tooltipData = {}
        for pointsCondition, bonuses in progression:
            progressionModel = model.getProgressionType()()
            progressionModel.setMarsPoints(pointsCondition)
            _logger.debug('[marsProgression] condition: %s, bonuses: %s', pointsCondition, bonuses)
            bonusArray = progressionModel.getBonuses()
            bonusArray.clear()
            bonusArray.reserve(len(bonuses))
            packBonusModelAndTooltipData(bonuses, bonusArray, self.__tooltipData, packer)
            bonusArray.invalidate()
            progressionArray.addViewModel(progressionModel)

        _logger.debug('tooltipData: %s', self.__tooltipData)
        progressionArray.invalidate()

    def _fillScoreModel(self, model):
        scoresSystem = sorted(self._getScoreSystem(), key=lambda scoreEvent: _getScoreEventListOrder(scoreEvent[0]))
        scoreArray = model.getScoring()
        scoreArray.clear()
        scoreArray.reserve(len(scoresSystem))
        for event, points in scoresSystem:
            _logger.debug('adding score event [type: %s, points: %s]', event, points)
            scoringModel = model.getScoringType()()
            scoringModel.setType(_getScoreEventTypeEnum(event))
            scoringModel.setMarsPoints(points)
            scoreArray.addViewModel(scoringModel)

        scoreArray.invalidate()

    def _getScoreSystem(self):
        scoreSystem = self._cosmicController.getModeSettings().scoreSystem
        return scoreSystem.get('eventsConfig', {}).items()

    @replaceNoneKwargsModel
    def _fillMissionsModel(self, model=None):
        quests = self._cosmicProgression.collectSortedDailyQuests()
        missionsModel = model.getMissions()
        missionsModel.clear()
        missionsModel.reserve(len(quests))
        for quest in quests.values():
            dailyQuestModel = WidgetQuestModel()
            fullQuestModel = getDailyQuestModelFromQuest(quest)
            fillDailyQuestModel(dailyQuestModel, fullQuestModel)
            missionsModel.addViewModel(dailyQuestModel)
            fullQuestModel.unbind()

        missionsModel.invalidate()

    def _finalize(self):
        _logger.debug('[CosmicLobbyView] finalizing')
        if self._soundProgressionObject and self._soundProgressionObject.isPlaying:
            self._soundProgressionObject.stop()
            self._soundProgressionObject = None
        self.resumeLobbyHeader()
        g_eventBus.removeListener(CosmicBattleResultEvent.POST_BATTLE_SCREEN_OPENING, self._postBattleOpening, scope=EVENT_BUS_SCOPE.LOBBY)
        super(CosmicLobbyView, self)._finalize()
        return

    def onLobbyRouteChangeImpl(self, newRoute):
        _logger.debug('[CosmicLobbyView] onLobbyRoute changed - %s', newRoute)
        self.__currentRoute = newRoute
        self._fillModel(self.__currentRoute)
        self._cosmicController.setLobbyRoute(self.__currentRoute)

    @args2params(str)
    def onLobbyRouteChange(self, newRoute):
        self.onLobbyRouteChangeImpl(LobbyRouteEnum(newRoute))

    def onClose(self):
        _logger.debug('[CosmicLobbyView] close button clicked')
        if not self.__callbackDelayer.hasDelayedCallback(self.closeLobby):
            self.viewModel.setFadeOut(True)
            self.__callbackDelayer.delayCallback(time_utils.ONE_SECOND, self.closeLobby)

    @adisp_process
    def closeLobby(self, *args, **kwargs):
        dispatcher = g_prbLoader.getDispatcher()
        result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if result:
            self._cosmicController.setLobbyRoute(LobbyRouteEnum.MAIN)
            self.destroyWindow()

    def onAboutEvent(self, *args, **kwargs):
        _logger.debug('[CosmicLobbyView] info button clicked')
        self._showInfoPage()

    @replaceNoneKwargsModel
    def _updateVehicleState(self, model=None):
        vehicle = self._cosmicController.getEventVehicle()
        if vehicle:
            model.setIsVehicleInBattle(vehicle.isInBattle)

    def _onItemSyncCompleted(self, *_):
        self._updateVehicleState()

    def _onEventSyncCompleted(self, *_):
        self._fillMissionsModel()
        self.__playProgressionSound()

    def _getInfoPageURL(self):
        return GUI_SETTINGS.cosmicInfoPageURL

    def _showInfoPage(self):
        url = self._getInfoPageURL()
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _postBattleOpening(self, *args, **kwargs):
        self._postBattleOpenedAfterBattle = True

    def onShopClicked(self):
        _logger.debug('[CosmicLobbyView] shop button clicked')
        showShop(getCosmic2024ShopUrl())

    def __playProgressionSound(self):
        currentStage = self._cosmicProgression.getCurrentStage()
        self._soundProgressionObject = CosmicHangarSounds.CosmicProgression.getSoundObject(currentStage)
        if self._soundProgressionObject:
            self._soundProgressionObject.play()
        else:
            LOG_ERROR('[COSMIC] Error on playing sound for cosmic progression')
