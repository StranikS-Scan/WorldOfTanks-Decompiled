# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/battle_control/controllers/races_sound_controller.py
import logging
import BigWorld
import typing
import SoundGroups
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController, SoundPlayer
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from races.gui.shared.event import RacesEvent
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.period_ctrl import ArenaPeriodController
_logger = logging.getLogger(__name__)
_PLAYER_NOT_FINISHED = 0

class RacesSoundController(SoundPlayersBattleController):

    def _initializeSoundPlayers(self):
        return (_RacesArenaSoundPlayer(),)


class _RacesArenaSoundPlayer(SoundPlayer):
    appLoader = dependency.descriptor(IAppLoader)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    EVENT_RACE_LOADING = 'ev_race_setting_set'
    EVENT_RACE_MUSIC = 'ev_race_music_gameplay'
    EVENT_RACE_PRE_START = 'ev_race_pre_start'
    EVENT_RACE_START = 'ev_race_start'
    EVENT_RACE_EXIT = 'ev_race_setting_reset'
    EVENT_VO_PRE_START = 'ev_race_vo_2024_pc_pre_start'
    EVENT_VO_START = 'ev_race_vo_2024_pc_start'
    EVENT_VO_PRE_END = 'ev_race_vo_2024_pc_pre_end'
    EVENT_VO_NPC_1_FINISH = 'ev_race_vo_2024_npc_1_finish'
    EVENTS_VO_PC_FINISHED = {1: 'ev_race_vo_2024_pc_1_finish',
     2: 'ev_race_vo_2024_pc_2_finish',
     3: 'ev_race_vo_2024_pc_3_finish'}
    EVENT_VO_PC_4_FINISH = 'ev_race_vo_2024_pc_4_finish'
    EVENT_VO_PC_UNCOMPLETE = 'ev_race_vo_2024_pc_uncomplete'
    SWITCH_RACE_DRIVER = 'SWITCH_ext_ev_race_driver'
    VEHICLE_TO_DRIVER_SWITCH = {'GB00_AEC_Armoured_Car_03': 'SWITCH_ext_ev_race_driver_Eugene',
     'F00_AMD_Panhard_178B_03': 'SWITCH_ext_ev_race_driver_Matthew',
     'F00_AMD_Panhard_178B_02': 'SWITCH_ext_ev_race_driver_Darya',
     'GB00_AEC_Armoured_Car_02': 'SWITCH_ext_ev_race_driver_Natalya'}

    def __init__(self):
        super(_RacesArenaSoundPlayer, self).__init__()
        self.__callbackId = None
        self.__raceEntered = False
        return

    @property
    def arenaPeriod(self):
        return self.__sessionProvider.shared.arenaPeriod

    def _subscribe(self):
        g_eventBus.addListener(RacesEvent.ON_RACE_FIRST_LIGHTS, self.__onRacesFirstLights, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(RacesEvent.ON_RACE_LAST_LIGHTS, self.__onRacesLastLights, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        arenaInfo = self.__getArenaInfoComponent()
        if arenaInfo:
            arenaInfo.onRaceEndTimeUpdated += self.__clearOneMinuteCallback
            arenaInfo.onRankListUpdated += self.__onVehicleFinished
        if self.arenaPeriod.getPeriod() == ARENA_PERIOD.BATTLE and (arenaInfo is None or arenaInfo.raceEndTime == 0):
            self.__registerOneMinuteCallback()
        return

    def _unsubscribe(self):
        g_eventBus.removeListener(RacesEvent.ON_RACE_FIRST_LIGHTS, self.__onRacesFirstLights, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(RacesEvent.ON_RACE_LAST_LIGHTS, self.__onRacesLastLights, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        arenaInfo = self.__getArenaInfoComponent()
        if arenaInfo:
            arenaInfo.onRaceEndTimeUpdated -= self.__clearOneMinuteCallback
            arenaInfo.onRankListUpdated -= self.__onVehicleFinished
        self.__clearOneMinuteCallback()
        if self.__raceEntered:
            self.__onRacesExit()

    def __onRacesLoading(self, *_):
        self._playSound2D(self.EVENT_RACE_LOADING)

    def __onRacesExit(self, *_):
        self._playSound2D(self.EVENT_RACE_EXIT)

    def __onRacesFirstLights(self, *_):
        self._playSound2D(self.EVENT_RACE_PRE_START)

    def __onRacesLastLights(self, *_):
        self._playSound2D(self.EVENT_RACE_START)
        self._playVoiceOver(self.EVENT_VO_START)

    def __onGUISpaceEntered(self, spaceID):
        _logger.debug('Entering GUI space %r', spaceID)
        if spaceID == GuiGlobalSpaceID.BATTLE_LOADING:
            self._playSound2D(self.EVENT_RACE_LOADING)
            self.__raceEntered = True
        elif spaceID == GuiGlobalSpaceID.BATTLE:
            self.__setDriverSwitch()
            self._playSound2D(self.EVENT_RACE_MUSIC)
            self._playVoiceOver(self.EVENT_VO_PRE_START)

    def __setDriverSwitch(self):
        vehicleDescriptor = BigWorld.player().vehicle.typeDescriptor
        if vehicleDescriptor is None:
            _logger.error('Can not set driver switch: vehicle is None')
            return
        else:
            vehicleName = getNationLessName(vehicleDescriptor.name)
            state = self.VEHICLE_TO_DRIVER_SWITCH.get(vehicleName)
            if state is None:
                _logger.error('Can not set driver switch: no alias for %s', vehicleName)
                return
            _logger.debug('Set %s to %s state', self.SWITCH_RACE_DRIVER, state)
            SoundGroups.g_instance.setSwitch(self.SWITCH_RACE_DRIVER, state)
            return

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.BATTLE:
            self.__registerOneMinuteCallback()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            ownVehicleId = self.__sessionProvider.shared.vehicleState.getControllingVehicleID()
            arenaInfo = self.__getArenaInfoComponent()
            if arenaInfo:
                if arenaInfo.getPositionById(ownVehicleId) == _PLAYER_NOT_FINISHED:
                    self._playVoiceOver(self.EVENT_VO_PC_UNCOMPLETE)
        else:
            self.__clearOneMinuteCallback()

    def __registerOneMinuteCallback(self):
        self.__clearOneMinuteCallback()
        delta = self.arenaPeriod.getEndTime() - BigWorld.serverTime() - ONE_MINUTE
        if delta > 0:
            _logger.debug('Set one minute callback %d', delta)
            self.__callbackId = BigWorld.callback(delta, self.__onOneMinuteRemaining)

    def __clearOneMinuteCallback(self, *_):
        if self.__callbackId is not None:
            _logger.debug('Clear callback')
            BigWorld.cancelCallback(self.__callbackId)
            self.__callbackId = None
        return

    def __onOneMinuteRemaining(self, *_):
        _logger.debug('One minute remaining')
        self._playVoiceOver(self.EVENT_VO_PRE_END)
        self.__callbackId = None
        return

    def __getArenaInfoComponent(self):
        arenaInfo = self.__sessionProvider.arenaVisitor.getArenaInfo()
        if arenaInfo is not None:
            if arenaInfo:
                return arenaInfo.dynamicComponents.get('arenaInfoRacesComponent', None)
        return

    @staticmethod
    def _playVoiceOver(event):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications is not None:
            soundNotifications.play(event)
        else:
            _logger.error('Sound notification is None')
        return

    def __onVehicleFinished(self, vehicleId, position):
        event = None
        ownVehicleId = self.__sessionProvider.shared.vehicleState.getControllingVehicleID()
        if ownVehicleId == vehicleId:
            event = self.EVENTS_VO_PC_FINISHED.get(position)
            if not event:
                event = self.EVENT_VO_PC_4_FINISH
        elif position == 1:
            event = self.EVENT_VO_NPC_1_FINISH
        if event:
            self._playVoiceOver(event)
        return
