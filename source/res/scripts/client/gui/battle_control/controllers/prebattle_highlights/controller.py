# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/controller.py
from __future__ import absolute_import
import logging
import SoundGroups
import typing
from enum import Enum
from future.utils import viewvalues
import BattleReplay
import BigWorld
import Event
import Keys
import constants
from account_helpers.settings_core.settings_constants import GAME, GRAPHICS
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from gui import InputHandler
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE
from gui.battle_control.avatar_getter import getInputHandler
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.prebattle_highlights.pbh_constants import TankSizes, TANK_SIZE_LOWER_BOUNDS
from gui.battle_control.controllers.prebattle_highlights.pbh_helpers import timeUntilEndOfPeriod, PbhSounds
from gui.battle_control.controllers.prebattle_highlights.pbh_prefab_loader import PBHPrefabLoader, PrefabLoaderStatus
from gui.battle_control.controllers.prebattle_highlights.sub_systems.pbh_gamelogic_observer import PbhGameLogicObserver
from gui.battle_control.controllers.prebattle_highlights.sub_systems.pbh_sequence_handler import PbhSequenceHandler, EMPTY_SEQUENCE_LAYER_VALUE
from gui.battle_control.controllers.prebattle_highlights.sub_systems.pbh_vehicle_apperance_mover import PbhVehicleAppearanceMover
from gui.battle_control.controllers.prebattle_highlights.sub_systems.pbh_window_handler import PbhWindowHandler
from gui.battle_control.view_components import ViewComponentsController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.prebattle_highlights.constants import PrebattleHighlightsLogKeys
from uilogging.prebattle_highlights.loggers import PrebattleHighlightsEventLogger, PBHViewingLogInfo
from vehicle_systems.tankStructure import selectItemByTankSize, getVehicleAABB
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.battle_control.controllers.prebattle_highlights.sub_systems.base_sub_system import BasePbhSubSystem
_logger = logging.getLogger(__name__)

class PbhSubSystemsNames(Enum):
    SEQUENCE_HANDLER = 'sequence_handler'
    GAME_LOGIC_OBSERVER = 'game_logic_observer'
    WINDOW_HANDLER = 'window_handler'
    VEHICLE_APPEARANCE_MOVER = 'vehicle_appearance_mover'


class PrebattleHighlightsController(IArenaPeriodController, ViewComponentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __gameplayLogic = dependency.descriptor(IGameplayLogic)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(PrebattleHighlightsController, self).__init__()
        self.__triggeredByDevHotkey = False
        self.__displayingHighlights = False
        self.__ending = False
        self.__winnersStats = None
        self.__pbhWasShown = False
        self.__pbhSize = None
        self.__meetsHistoricalCompliance = False
        self.__prefabLoader = PBHPrefabLoader(lambda : self.winnersStats, self.getPBHSize)
        self.__uiLogger = PrebattleHighlightsEventLogger()
        self.onVehiclesDataReady = Event.Event()
        self.onStartPbhStage = Event.Event()
        self.__subSystems = {PbhSubSystemsNames.SEQUENCE_HANDLER: PbhSequenceHandler(self.__start, self.__end, self.onStartPbhStage),
         PbhSubSystemsNames.GAME_LOGIC_OBSERVER: PbhGameLogicObserver(self.__start),
         PbhSubSystemsNames.WINDOW_HANDLER: PbhWindowHandler(self.__start),
         PbhSubSystemsNames.VEHICLE_APPEARANCE_MOVER: PbhVehicleAppearanceMover(self.__start, lambda : self.winnersStats, self.getPBHSize, self.onVehiclesDataReady)}
        return

    @property
    def sequenceHandler(self):
        return self.__subSystems[PbhSubSystemsNames.SEQUENCE_HANDLER]

    @property
    def gameLogicObserver(self):
        return self.__subSystems[PbhSubSystemsNames.GAME_LOGIC_OBSERVER]

    @property
    def windowHandler(self):
        return self.__subSystems[PbhSubSystemsNames.WINDOW_HANDLER]

    @property
    def vehicleAppearanceMover(self):
        return self.__subSystems[PbhSubSystemsNames.VEHICLE_APPEARANCE_MOVER]

    @property
    def vehiclesData(self):
        return self.vehicleAppearanceMover.getPresentingVehiclesData()

    @property
    def meetsHistoricalCompliance(self):
        return self.__meetsHistoricalCompliance

    @property
    def displayingHighlights(self):
        return self.__displayingHighlights

    @property
    def winnersStats(self):
        return self.__winnersStats

    @property
    def pbhWasShown(self):
        return self.__pbhWasShown

    def startControl(self, battleCtx, arenaVisitor):
        if constants.IS_DEVELOPMENT:
            InputHandler.g_instance.onKeyDown += self.__toggleHighlights
        for subSystem in viewvalues(self.__subSystems):
            subSystem.subscribe()

    def stopControl(self):
        if constants.IS_DEVELOPMENT:
            InputHandler.g_instance.onKeyDown -= self.__toggleHighlights
        for subSystem in viewvalues(self.__subSystems):
            subSystem.unsubscribe()
            subSystem.clear()

        self.onVehiclesDataReady.clear()
        self.onStartPbhStage.clear()
        self.__meetsHistoricalCompliance = False
        self.__winnersStats = None
        self.__pbhSize = None
        self.__pbhWasShown = False
        self.__ending = False
        if self.__prefabLoader:
            self.__prefabLoader.clear()
            self.__prefabLoader = None
        return

    def getCtrlScope(self):
        return ARENA_LISTENER_SCOPE.PERIOD

    def getControllerID(self):
        return BATTLE_CTRL_ID.PREBATTLE_HIGHLIGHTS

    def setWinnersStats(self, winners):
        _logger.debug('[PBH] setWinnersStats %s', winners)
        self.__winnersStats = winners
        if self.__winnersStats:
            self.__start()
        else:
            self.__skipPrebattleHighlights()

    def getPBHSize(self):
        if self.__pbhSize is None:
            tankSizes = []
            for data in self.__winnersStats:
                tankEntity = BigWorld.entities.get(data.get('id'))
                if tankEntity is None:
                    tankSizes.append(TankSizes.SMALL)
                    continue
                tankSize = selectItemByTankSize(TANK_SIZE_LOWER_BOUNDS, TankSizes.ORDERED_SIZES, TankSizes.SMALL, getVehicleAABB(tankEntity.appearance.collisions))
                tankSizes.append(tankSize)

            self.__pbhSize = max(tankSizes, key=TankSizes.ORDERED_SIZES.index) if tankSizes else TankSizes.SMALL
            _logger.info('[PBH] size: %s', self.__pbhSize)
        return self.__pbhSize

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        _logger.debug('[PBH] invalidatePeriodInfo, period %s, self.__displayingHighlights %s', period, self.__displayingHighlights)
        if period == ARENA_PERIOD.BATTLE and self.windowHandler.isReady():
            self.__end()

    def handleEscClose(self):
        if self.windowHandler.isReady() and self.__displayingHighlights:
            SoundGroups.g_instance.playSound2D(PbhSounds.ESC_EVENT)
            self.__uiLogger.logStopViewingAction(PrebattleHighlightsLogKeys.ESC)
            self.__end()

    @wg_async
    def __start(self):
        if BattleReplay.isPlaying():
            self.__skipPrebattleHighlights()
            return
        elif not self.__settingsCore.getSetting(GRAPHICS.SHOW_PREBATTLE_HIGHLIGHTS):
            self.__skipPrebattleHighlights()
            self.__uiLogger.logSkipViewingEvent({'view_status': PrebattleHighlightsLogKeys.SETTINGS_PBH.value})
            return
        else:
            teamInfo = BigWorld.player().arena.teamInfo
            if 'pbh' not in teamInfo.components:
                _logger.info('[PBH] Component does not exist on server, skipping showing.')
                self.__skipPrebattleHighlights()
                return
            elif self.__winnersStats is None:
                _logger.info('[PBH] winners stats was not initialized')
                return
            elif not self.__winnersStats:
                _logger.info('[PBH] Empty winners stats, skipping start.')
                self.__skipPrebattleHighlights()
                return
            hLevel = self.__settingsCore.getSetting(GAME.CUSTOMIZATION_DISPLAY_TYPE)
            self.__meetsHistoricalCompliance = yield wg_await(self.vehicleAppearanceMover.historicalOutfitCompliance(hLevel))
            period = self.__sessionProvider.arenaVisitor.getArenaPeriod()
            if self.__triggeredByDevHotkey:
                if not self.windowHandler.isReady():
                    _logger.info('[PBH] Window is not ready, skipping start triggered by dev hotkey.')
                    return
            elif not (self.gameLogicObserver.isReady() and self.windowHandler.isReady()) and period not in (ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE):
                _logger.info('[PBH] Prebattle highlights state not reached or window not ready, skipping start.')
                return
            if self.__displayingHighlights:
                _logger.warning("[PBH] Attempted to start Prebattle Highlights while it's already active.")
                return
            elif self.__prefabLoader.status == PrefabLoaderStatus.LOADING:
                return
            elif self.__prefabLoader.status == PrefabLoaderStatus.FAILED:
                self.__skipPrebattleHighlights()
                return
            elif self.__prefabLoader.status == PrefabLoaderStatus.INITIAL:
                self.__prefabLoader.loadPBHPrefab(self.__start)
                return
            elif not self.sequenceHandler.isReady():
                _logger.info('[PBH] Prefab sequence is not ready.')
                return
            sequenceLayerInfo = self.sequenceHandler.getSequenceLayerInfo()
            notEnoughTime = sequenceLayerInfo == EMPTY_SEQUENCE_LAYER_VALUE
            if period in (ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE) and not self.__triggeredByDevHotkey or notEnoughTime:
                _logger.info('[PBH] Player reconnected and joined an ongoing battle or Player loads into battle when there is little time remaining before the start.')
                self.__skipPrebattleHighlights()
                if notEnoughTime:
                    self.__uiLogger.logSkipViewingEvent({'view_status': PrebattleHighlightsLogKeys.NOT_ENOUGH_TIME.value,
                     'time_to_battle_start': timeUntilEndOfPeriod()})
                return
            self.__displayingHighlights = True
            yield wg_await(self.windowHandler.toggleFadeManager(True))
            self.windowHandler.startFlow()
            inputHandler = getInputHandler()
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.PREBATTLE_HIGHLIGHTS)
            g_eventBus.handleEvent(GameEvent(GameEvent.GO_TO_PREBATTLE_HIGHLIGHTS), scope=EVENT_BUS_SCOPE.BATTLE)
            SoundGroups.g_instance.setState(PbhSounds.GROUP, PbhSounds.GROUP_ON)
            SoundGroups.g_instance.playSound2D(PbhSounds.ENTER_EVENT)
            self.vehicleAppearanceMover.startFlow()
            self.sequenceHandler.startFlow()
            yield wg_await(self.windowHandler.toggleFadeManager(False))
            self.__uiLogger.logStartViewingAction(PBHViewingLogInfo(sequence_layer=sequenceLayerInfo, historical_level=hLevel, was_historical_compliance=not self.__meetsHistoricalCompliance))
            return

    def __skipPrebattleHighlights(self):
        _logger.debug('[PBH] skip showing')
        self.__prefabLoader.reset()
        self.windowHandler.forceStopFlow()
        self.gameLogicObserver.postPbhEnd()

    @wg_async
    def __end(self):
        _logger.debug('[PBH] __end, self.__displayingHighlights %s', self.__displayingHighlights)
        if self.__ending:
            return
        self.__ending = True
        yield wg_await(self.windowHandler.toggleFadeManager(True))
        self.windowHandler.stopFlow()
        if self.__displayingHighlights:
            self.__pbhWasShown = True
            self.vehicleAppearanceMover.stopFlow()
            inputHandler = getInputHandler()
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
        self.__displayingHighlights = False
        self.__prefabLoader.reset()
        g_eventBus.handleEvent(GameEvent(GameEvent.RETURN_FROM_PREBATTLE_HIGHLIGHTS), scope=EVENT_BUS_SCOPE.BATTLE)
        SoundGroups.g_instance.playSound2D(PbhSounds.EXIT_EVENT)
        SoundGroups.g_instance.setState(PbhSounds.GROUP, PbhSounds.GROUP_OFF)
        self.gameLogicObserver.postPbhEnd()
        self.__triggeredByDevHotkey = False
        yield wg_await(self.windowHandler.toggleFadeManager(False))
        self.__ending = False
        self.__uiLogger.logStopViewingAction(PrebattleHighlightsLogKeys.FULLY_VIEWED)

    if constants.IS_DEVELOPMENT:

        def __toggleHighlights(self, event):
            if event.key is not Keys.KEY_F2 or not BigWorld.isKeyDown(Keys.KEY_CAPSLOCK):
                return
            if self.__displayingHighlights:
                self.__end()
            elif self.__winnersStats:
                self.__triggeredByDevHotkey = True
                self.windowHandler.preload()
                self.__start()
