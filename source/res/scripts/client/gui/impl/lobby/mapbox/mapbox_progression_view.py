# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/mapbox_progression_view.py
import logging
from ArenaType import g_geometryNamesToIDs
from async import async, await
from constants import QUEUE_TYPE
from frameworks.wulf import ViewSettings, ViewFlags, WindowStatus
from frameworks.wulf.gui_constants import ViewStatus, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.mapbox_progression_model import MapboxProgressionModel
from gui.impl.gen.view_models.views.lobby.mapbox.progression_reward_model import ProgressionRewardModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_model import MapModel
from gui.impl.pub import ViewImpl
from gui.mapbox.mapbox_bonus_packers import getMapboxBonusPacker
from gui.mapbox.mapbox_helpers import packMapboxRewardModelAndTooltip, getMapboxRewardTooltip
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MissionsMapboxViewMeta import MissionsMapboxViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.Waiting import Waiting
from gui.server_events import IEventsCache
from gui.shared.event_dispatcher import showMapboxRewardChoice, showHangar, showMapboxIntro, showBrowserOverlayView
from gui.shared.formatters.time_formatters import getTillTimeByResource
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class MapboxProgressionsComponent(InjectComponentAdaptor, MissionsMapboxViewMeta):
    __slots__ = ()

    def markVisited(self):
        pass

    def _makeInjectView(self):
        return MapboxProgressionView(self.as_showViewS, flags=ViewFlags.COMPONENT)


class MapboxProgressionView(ViewImpl):
    __slots__ = ('__showViewCallback', '__tooltips', '__notifier')
    __mapboxController = dependency.descriptor(IMapboxController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, showViewCallback, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.mapbox.MapBoxProgression(), flags=flags, model=MapboxProgressionModel())
        self.__notifier = None
        self.__showViewCallback = showViewCallback
        self.__tooltips = []
        super(MapboxProgressionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(MapboxProgressionView, self).getViewModel()

    def createToolTip(self, event):
        tooltip = getMapboxRewardTooltip(event, self.__tooltips, self.getParentWindow())
        return tooltip or super(MapboxProgressionView, self).createToolTip(event)

    @async
    def _initialize(self, *args, **kwargs):
        super(MapboxProgressionView, self)._initialize(*args, **kwargs)
        Waiting.show('loadContent')
        result = yield await(self.__mapboxController.forceUpdateProgressData())
        Waiting.hide('loadContent')
        if self.viewStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            return
        if result:
            progressionData = self.__mapboxController.getProgressionData()
            self.__updateProgressionData(progressionData)
            self.__notifier = PeriodicNotifier(self.__getDeltaTime, self.__updateProgressionAlert, (time_utils.ONE_MINUTE,))
            self.__notifier.startNotification()
        else:
            self.__setErrorStatus()
        self.__addListeners()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        self.__removeListeners()
        self.__showViewCallback = None
        super(MapboxProgressionView, self)._finalize()
        return

    def __addListeners(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        self.viewModel.onSelectMapboxBattle += self.__onSelectMapboxBattle
        self.viewModel.onShowInfo += self.__onShowInfo
        self.viewModel.onRemoveBubble += self.__onRemoveBubble
        self.viewModel.onShowSurvey += self.__onShowSurvey
        self.viewModel.onTakeReward += self.__onTakeReward
        self.viewModel.onAnimationEnded += self.__onAnimationEnded
        self.__mapboxController.addProgressionListener(self.__onProgressionDataUpdated)
        self.__mapboxController.onMapboxSurveyShown += self.__doRemoveBubble
        self.__mapboxController.onMapboxSurveyCompleted += self.__onSurveyCompleted
        self.__mapboxController.onUpdated += self.__onSettingsUpdated
        g_prbCtrlEvents.onPreQueueJoined += self.__onPreQueueJoined
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        g_prbCtrlEvents.onPreQueueJoined -= self.__onPreQueueJoined
        self.__mapboxController.onMapboxSurveyCompleted -= self.__onSurveyCompleted
        self.__mapboxController.onMapboxSurveyShown -= self.__doRemoveBubble
        self.__mapboxController.removeProgressionListener(self.__onProgressionDataUpdated)
        self.__mapboxController.onUpdated -= self.__onSettingsUpdated
        self.viewModel.onAnimationEnded -= self.__onAnimationEnded
        self.viewModel.onTakeReward -= self.__onTakeReward
        self.viewModel.onShowSurvey -= self.__onShowSurvey
        self.viewModel.onShowInfo -= self.__onShowInfo
        self.viewModel.onRemoveBubble -= self.__onRemoveBubble
        self.viewModel.onSelectMapboxBattle -= self.__onSelectMapboxBattle
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def __onAnimationEnded(self, *args):
        progressionData = self.__mapboxController.getProgressionData()
        self.viewModel.setPrevTotalBattlesPlayed(progressionData.totalBattles)
        self.__mapboxController.setPrevBattlesPlayed(progressionData.totalBattles)

    def __onWindowStatusChanged(self, _, newState):

        def predicate(window):
            return WindowLayer.FULLSCREEN_WINDOW <= window.layer <= WindowLayer.OVERLAY and window != self.getParentWindow()

        if newState == WindowStatus.LOADED or newState == WindowStatus.DESTROYED:
            overlappingWindows = self.__gui.windowsManager.findWindows(predicate)
            self.viewModel.setIsOverlapped(bool(overlappingWindows))

    def __onClose(self):
        showHangar()

    def __onPreQueueJoined(self, prbType):
        if prbType == QUEUE_TYPE.MAPBOX:
            self.viewModel.setIsMapboxModeSelected(True)

    def __onSelectMapboxBattle(self):
        self.viewModel.setIsMapboxModeSelected(True)
        isKnownBattletype = SelectorBattleTypesUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.MAPBOX)
        if not isKnownBattletype:
            SelectorBattleTypesUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.MAPBOX)
        self.__mapboxController.selectMapboxBattle()
        if not isKnownBattletype:
            showMapboxIntro(showHangar)
        else:
            showHangar()

    def __onProgressionDataUpdated(self):
        self.__updateProgressionData()

    def __onShowInfo(self):
        url = GUI_SETTINGS.lookup('infoPageMapbox')
        showBrowserOverlayView(url, VIEW_ALIAS.MAP_BOX_INFO_OVERLAY)

    def __onSurveyCompleted(self, mapId):
        with self.viewModel.transaction() as model:
            mapsList = model.getMaps()
            for mapModel in mapsList:
                if mapModel.getMapName() == mapId:
                    mapModel.setMapSurveyPassed(True)
                    break

            mapsList.invalidate()

    def __onRemoveBubble(self, args):
        self.__doRemoveBubble(args.get('mapName'))

    def __doRemoveBubble(self, name):
        if not self.__mapboxController.isMapVisited(name):
            self.__mapboxController.addVisitedMap(name)
            with self.viewModel.transaction() as model:
                mapsList = model.getMaps()
                for mapModel in mapsList:
                    if mapModel.getMapName() == name:
                        mapModel.setIsBubble(False)
                        self.__eventsCache.onEventsVisited()
                        break

                mapsList.invalidate()

    def __onShowSurvey(self, args):
        self.__mapboxController.showSurvey(args.get('mapName'))

    def __onTakeReward(self, args):
        numBattles = args.get('numBattles')
        itemIdx = args.get('itemIdx')
        itemName = args.get('name')
        if itemIdx is not None and numBattles is not None and itemName is not None:
            progressionData = self.__mapboxController.getProgressionData()
            crewbook = first([ crewbook for crewbook in progressionData.rewards[int(numBattles)].bonusList[int(itemIdx)].getItems() if crewbook.name == itemName ])
            showMapboxRewardChoice(crewbook)
        return

    def __onSettingsUpdated(self):
        progressionData = self.__mapboxController.getProgressionData()
        if progressionData is None:
            self.viewModel.setIsError(True)
            return
        else:
            with self.viewModel.transaction() as model:
                actualSeason = self.__mapboxController.getCurrentSeason() or self.__mapboxController.getNextSeason()
                self.__fillMaps(model, progressionData, actualSeason)
            return

    def __updateProgressionData(self, progression=None):
        progressionData = progression if progression is not None else self.__mapboxController.getProgressionData()
        if progressionData is None:
            self.viewModel.setIsError(True)
            return
        else:
            with self.viewModel.transaction() as model:
                model.setIsDataSynced(True)
                model.setIsError(False)
                actualSeason = self.__mapboxController.getCurrentSeason() or self.__mapboxController.getNextSeason()
                model.setPrevTotalBattlesPlayed(self.__mapboxController.getPrevBattlesPlayed())
                self.__mapboxController.setPrevBattlesPlayed(progressionData.totalBattles)
                totalRequeredBattles = max(progressionData.rewards.keys())
                model.setTotalBattlesPlayed(min(progressionData.totalBattles, totalRequeredBattles))
                model.setTotalBattles(totalRequeredBattles)
                self.__fillMaps(model, progressionData, actualSeason)
                model.setIsMapboxModeSelected(self.__mapboxController.isMapboxMode())
                model.setSeasonNumber(actualSeason.getNumber())
                model.setStartEvent(actualSeason.getCycleStartDate())
                model.setEndEvent(actualSeason.getCycleEndDate())
                progressionRewardsList = model.getProgressionRewards()
                progressionRewardsList.clear()
                packer = getMapboxBonusPacker()
                self.__packRewards(progressionData.rewards, packer, progressionRewardsList, self.__tooltips)
                progressionSubstage = progressionData.nextSubstage
                if progressionSubstage >= time_utils.getCurrentTimestamp():
                    self.__updateProgressionAlert(progressionSubstage)
            return

    def __packRewards(self, rewards, packer, rewardModelsList, tooltipsList=None):
        for battles, progressionReward in rewards.iteritems():
            if not progressionReward:
                continue
            progressionRewardModel = ProgressionRewardModel()
            progressionRewardModel.setNumBattles(battles)
            rewardsModel = progressionRewardModel.getRewards()
            packMapboxRewardModelAndTooltip(rewardsModel, progressionReward.bonusList, packer, battles, tooltipsList)
            rewardsModel.invalidate()
            rewardModelsList.addViewModel(progressionRewardModel)

        rewardModelsList.invalidate()

    def __fillMaps(self, model, progressionData, actualSeason):
        geometryIDsToNames = {geometryID:geometryName for geometryName, geometryID in g_geometryNamesToIDs.iteritems()}
        geometryNames = ['all'] + sorted([ geometryIDsToNames[geometryID] for geometryID in self.__mapboxController.getModeSettings().geometryIDs[actualSeason.getSeasonID()] ])
        mapsData = progressionData.surveys
        mapsList = model.getMaps()
        mapsList.clear()
        for mapName in geometryNames:
            if mapName not in mapsData:
                continue
            mapData = mapsData[mapName]
            mapModel = MapModel()
            mapModel.setMapBattles(mapData.total)
            mapModel.setMapBattlesPlayed(mapData.progress)
            mapModel.setMapName(mapName)
            mapModel.setRating(progressionData.minRank)
            mapModel.setIsBubble(not self.__mapboxController.isMapVisited(mapName) and mapData.available and mapData.progress == mapData.total)
            mapModel.setMapSurveyPassed(mapData.passed)
            mapModel.setIsSurveyAvailable(mapData.available)
            mapsList.addViewModel(mapModel)

        mapsList.invalidate()

    def __setErrorStatus(self):
        with self.viewModel.transaction() as model:
            model.setIsDataSynced(True)
            model.setIsError(True)

    def __getDeltaTime(self):
        endTime = self.__mapboxController.getProgressionRestartTime()
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(endTime))

    def __updateProgressionAlert(self, endTime=None):
        if endTime is None:
            endTime = self.__mapboxController.getProgressionRestartTime()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(endTime))
        timeLeftStr = '' if timeLeft <= 0 else getTillTimeByResource(timeLeft, R.strings.mapbox.progression.timeLeft, removeLeadingZeros=True)
        self.viewModel.setTimeTillProgressionRestart(timeLeftStr)
        return
