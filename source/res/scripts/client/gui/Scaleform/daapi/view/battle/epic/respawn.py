# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/respawn.py
import math
import BigWorld
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.EpicRespawnViewMeta import EpicRespawnViewMeta
from gui.battle_control.controllers.epic_respawn_ctrl import IEpicRespawnView
from gui.battle_control.controllers.epic_respawn_ctrl import EB_MIN_RESPAWN_LANE_IDX, EB_MAX_RESPAWN_LANE_IDX
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import i18n
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.battle_control import minimap_utils
from gui.Scaleform.daapi.view.battle.shared.respawn import respawn_utils
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.sounds.epic_sound_constants import EPIC_SOUND
_BF_EB_COUNT_DOWN_SOUND_ID = {True: 'eb_respawn_screen_count_down',
 False: 'eb_respawn_screen_count_down_STOP'}
_BF_EB_READY_FOR_DEPLOYMENT_ID = {True: 'eb_ready_for_deployment',
 False: 'eb_stop_ready_for_deployment'}
_BF_EB_COUNT_DOWN_SOUND_SECONDS = 10

class EpicBattleRespawn(EpicRespawnViewMeta, IEpicRespawnView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleRespawn, self).__init__()
        self.__selectedLaneID = None
        self.__disabled = False
        self.__buttonStates = {}
        self.__timeOver = False
        self.__countDownIsPlaying = False
        self.__mapDim = (0, 0)
        self.__lastRespawnPositions = {}
        self.__carousel = None
        self.__shop = None
        self.__battleCtx = None
        return

    def _onRegisterFlashComponent(self, componentPy, alias):
        if alias == BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL:
            self.__carousel = componentPy

    def _populate(self):
        super(EpicBattleRespawn, self)._populate()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated += self.onRespawnInfoUpdated
        else:
            LOG_ERROR('Respawn Controller not available!')
        minSize, maxSize = self.sessionProvider.arenaVisitor.type.getBoundingBox()
        self.__mapDim = (abs(maxSize[0] - minSize[0]) * 1.0, abs(maxSize[1] - minSize[1]) * 1.0)
        dimx, dimy = self.__mapDim
        mapWidthPx = int(dimx * 0.001 * minimap_utils.EPIC_1KM_IN_PX)
        mapHeightPx = int(dimy * 0.001 * minimap_utils.EPIC_1KM_IN_PX)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)
        for lane in range(EB_MIN_RESPAWN_LANE_IDX, EB_MAX_RESPAWN_LANE_IDX):
            self.__lastRespawnPositions[lane] = [0, 0]

        return

    def _dispose(self):
        super(EpicBattleRespawn, self)._dispose()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.onRespawnInfoUpdated
        self.__buttonStates.clear()
        self.__lastRespawnPositions.clear()
        return

    def py_onRespawnBtnClick(self):
        LOG_DEBUG('py_onRespawnBtnClick')
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.respawnPlayer()
        else:
            LOG_ERROR('Respawn Controller not available!')
        if self.__countDownIsPlaying is True:
            self.__playCountDownSound(False)
        return

    def py_onLaneSelected(self, laneID):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.requestLaneForRespawn(laneID)
        return

    def py_onDeploymentReady(self):
        self.__playSound(_BF_EB_READY_FOR_DEPLOYMENT_ID[True])

    def onRespawnInfoUpdated(self, respawnInfo):
        vehicle = self.__carousel.getSelectedVehicle()
        if not vehicle or vehicle.intCD != respawnInfo.vehicleID:
            self.__carousel.selectVehicleByID(respawnInfo.vehicleID)
            vehicle = self.__carousel.getSelectedVehicle()
        if not vehicle:
            LOG_ERROR('RESPAWN: THIS SHOULD NEVER HAPPEN! Selected Veh ID: ', respawnInfo.vehicleID, ' available Vehicles: ', self.__carousel.getTotalVehiclesCount())

    def updateTimer(self, timeLeft, vehsList, cooldowns, limits=0):
        mainTimer = i18n.makeString(EPIC_BATTLE.RESPAWNSCREEN_SECONDSTIMERTEXT, seconds=int(round(timeLeft[0])))
        secondsLeft = int(math.ceil(timeLeft[0]))
        if secondsLeft <= 0 and not self.__timeOver:
            self.__timeOver = True
            self.as_updateTimerS(True, mainTimer)
            if self.__countDownIsPlaying is True:
                self.__playCountDownSound(False)
        elif secondsLeft > 0:
            self.__timeOver = False
            if 0 < secondsLeft <= _BF_EB_COUNT_DOWN_SOUND_SECONDS:
                if self.__countDownIsPlaying is False:
                    self.__playCountDownSound(True)
        if not self.__timeOver:
            self.as_updateTimerS(secondsLeft == 0, mainTimer)
        secondsLeft = int(math.ceil(timeLeft[1]))
        if secondsLeft <= 10:
            autoTimer = i18n.makeString(EPIC_BATTLE.RESPAWN_AUTO_TIMER_TXT, seconds=int(round(timeLeft[1])))
            self.as_updateAutoTimerS(secondsLeft == 0.0, autoTimer)
            if self.__countDownIsPlaying is False:
                self.__playCountDownSound(True)
        if secondsLeft <= 0:
            if self.__countDownIsPlaying is True:
                self.__playCountDownSound(False)
        self.__updateSlotData(vehsList, cooldowns, limits)

    def hide(self):
        self.as_resetRespawnStateS()
        if self.__countDownIsPlaying is True:
            self.__playCountDownSound(False)
        BigWorld.wg_enableGUIBackground(False, False)

    def show(self, selectedID, vehsList, cooldowns, limits=0):
        self.__carousel.resetFilters()
        self.__updateSlotData(vehsList, cooldowns, limits)
        BigWorld.wg_enableGUIBackground(True, False)
        if self.__battleCtx:
            BigWorld.wg_setGUIBackground(self.__battleCtx.getArenaRespawnIcon())

    def start(self, vehsList, isLimited):
        self.__carousel.sortVehicles(vehsList)

    def setLimits(self, limits):
        pass

    def setSelectedLane(self, laneId):
        self.__selectedLaneID = laneId
        self.as_setSelectedLaneS(laneId)

    def setRespawnPositions(self, frontlineCenters, respawnOffsets):
        width, height = self.__mapDim
        if frontlineCenters is None or width * height == 0:
            return
        else:
            classTag = None
            vehicle = self.__carousel.getSelectedVehicle()
            if vehicle:
                classTag = vehicle.type
            offset = respawnOffsets.get(classTag, 0.0)
            for key in frontlineCenters:
                xPos = frontlineCenters[key][0]
                yPos = frontlineCenters[key][1] + offset
                xPos = xPos / width + 0.5
                yPos = yPos / height + 0.5
                yPos = max(0, min(1, yPos))
                self.__lastRespawnPositions[key] = [xPos, yPos]

            self.as_setRespawnLocationsS(self.__lastRespawnPositions)
            return

    def setLaneState(self, laneID, enabled, blockedText):
        if laneID not in self.__buttonStates or self.__buttonStates[laneID] is not enabled:
            self.as_setLaneStateS(laneID, enabled, blockedText)
            self.__buttonStates[laneID] = enabled

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def __playCountDownSound(self, play):
        if play is True:
            self.__playSound(_BF_EB_COUNT_DOWN_SOUND_ID[play])
            self.__countDownIsPlaying = True
        else:
            self.__playSound(_BF_EB_COUNT_DOWN_SOUND_ID[play])
            self.__countDownIsPlaying = False

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __updateSlotData(self, vehsList, cooldowns, limits):
        if not isinstance(limits, dict):
            return
        laneLimits = limits.get(self.__selectedLaneID, {})
        slotsStatesData = respawn_utils.getSlotsStatesData(vehsList, cooldowns, self.__disabled, laneLimits)
        self.__carousel.updateVehicleStates(slotsStatesData)
