# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/respawn.py
import math
import BigWorld
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.EpicRespawnViewMeta import EpicRespawnViewMeta
from gui.battle_control.controllers.epic_respawn_ctrl import IEpicRespawnView
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import i18n
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.battle_control import minimap_utils
from gui.Scaleform.daapi.view.battle.shared.respawn import respawn_utils
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.sounds.epic_sound_constants import EPIC_SOUND, EPIC_TIME_WWEVENTS
import SoundGroups
_BF_EB_COUNT_DOWN_SOUND_SECONDS = 10
_DEFAULT_RESPAWN_POSITIONS = ({'position': (0, 0, 0),
  'isEnemyNear': 0},)

class EpicBattleRespawn(EpicRespawnViewMeta, IEpicRespawnView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleRespawn, self).__init__()
        self.__selectedLaneID = None
        self.__selectedPointID = None
        self.__disabled = False
        self.__buttonStates = {}
        self.__timeOver = False
        self.__countDownIsPlaying = False
        self.__mapDim = (0, 0)
        self.__lastRespawnPositions = _DEFAULT_RESPAWN_POSITIONS
        self.__carousel = None
        self.__ammunitionPanel = None
        self.__shop = None
        self.__battleCtx = None
        return

    def _onRegisterFlashComponent(self, componentPy, alias):
        if alias == BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL:
            self.__carousel = componentPy
        elif alias == BATTLE_VIEW_ALIASES.EPIC_RESPAWN_AMMUNITION_PANEL:
            self.__ammunitionPanel = componentPy

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL:
            self.__carousel = None
        elif alias == BATTLE_VIEW_ALIASES.EPIC_RESPAWN_AMMUNITION_PANEL:
            self.__ammunitionPanel = None
        super(EpicBattleRespawn, self)._onUnregisterFlashComponent(viewPy, alias)
        return

    def _populate(self):
        super(EpicBattleRespawn, self)._populate()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated += self.onRespawnInfoUpdated
        else:
            LOG_ERROR('Respawn Controller not available!')
        minSize, maxSize = self.sessionProvider.arenaVisitor.type.getBoundingBox()
        self.__mapDim = (abs(maxSize[0] - minSize[0]) * 1.0, abs(maxSize[1] - minSize[1]) * 1.0)
        mapWidthPx, mapHeightPx = minimap_utils.metersToMinimapPixels(*self.sessionProvider.arenaVisitor.type.getBoundingBox())
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)
        self.__lastRespawnPositions = _DEFAULT_RESPAWN_POSITIONS
        if self.sessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()
        return

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.onRespawnInfoUpdated
        self.__buttonStates.clear()
        self.__lastRespawnPositions = _DEFAULT_RESPAWN_POSITIONS
        super(EpicBattleRespawn, self)._dispose()
        return

    def onRespawnBtnClick(self):
        LOG_DEBUG('py_onRespawnBtnClick')
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.respawnPlayer()
        else:
            LOG_ERROR('Respawn Controller not available!')
        if self.__countDownIsPlaying is True:
            self.__playCountDownSound(False)
        return

    def onLocationSelected(self, pointId):
        if self.__selectedPointID != pointId:
            self.setSelectedPoint(pointId)

    def onDeploymentReady(self):
        self.__playSound(EPIC_SOUND.EB_READY_FOR_DEPLOYMENT)

    def onRespawnInfoUpdated(self, respawnInfo):
        vehicle = self.__carousel.getSelectedVehicle()
        if not vehicle or vehicle.intCD != respawnInfo.vehicleID:
            self.__carousel.selectVehicleByID(respawnInfo.vehicleID)
            vehicle = self.__carousel.getSelectedVehicle()
        if not vehicle:
            LOG_ERROR('RESPAWN: THIS SHOULD NEVER HAPPEN! Selected Veh ID: ', respawnInfo.vehicleID, ' available Vehicles: ', self.__carousel.getTotalVehiclesCount())

    def isVehicleChanged(self, respawnInfo):
        vehicle = self.__carousel.getSelectedVehicle()
        isVehicleChanged = True
        if vehicle:
            isVehicleChanged = vehicle.intCD != respawnInfo.vehicleID
        return isVehicleChanged

    def updateTimer(self, timeLeft, vehs, cooldowns, limits=0):
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
        self.__updateSlotData(vehs, cooldowns, limits)

    def hide(self):
        self.as_resetRespawnStateS()
        self.__ammunitionPanel.hide()
        if self.__countDownIsPlaying is True:
            self.__playCountDownSound(False)
        BigWorld.wg_enableGUIBackground(False, False)

    def show(self, selectedID, vehs, cooldowns, limits=0):
        self.__ammunitionPanel.show(selectedID, vehs, cooldowns, limits=0)
        self.__carousel.resetFilters()
        self.__updateSlotData(vehs, cooldowns, limits)
        self.__carousel.show()
        BigWorld.wg_enableGUIBackground(True, False)
        if self.__battleCtx:
            BigWorld.wg_setGUIBackground(self.__battleCtx.getArenaRespawnIcon())

    def start(self, vehs, isLimited):
        self.__carousel.sortVehicles(vehs)

    def setLimits(self, limits):
        pass

    def setSelectedLane(self, laneId):
        self.__selectedLaneID = laneId

    def setSelectedPoint(self, pointId):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            0 <= pointId < len(self.__lastRespawnPositions) and ctrl.requestPointForRespawn(self.__lastRespawnPositions[pointId]['position'])
            self.__selectedPointID = pointId
        return

    def setRespawnInfo(self, respawnInfo):
        self.__lastRespawnPositions = respawnInfo.respawnZones
        width, height = self.__mapDim
        if self.__lastRespawnPositions is None or width * height == 0:
            return
        else:

            def convert(val, dim):
                return val / dim + 0.5

            def getX(p):
                return convert(p[0], width)

            def getY(p):
                return convert(p[2], height)

            self.as_setRespawnLocationsS([ self.__makePointVO(getX(point['position']), getY(point['position']), bool(point['isEnemyNear'])) for point in self.__lastRespawnPositions ])
            positions = [ point['position'] for point in self.__lastRespawnPositions ]
            if respawnInfo.chosenRespawnZone in positions:
                self.__selectedPointID = positions.index(respawnInfo.chosenRespawnZone)
                self.as_setSelectedLocationS(self.__selectedPointID)
            return

    def setRespawnInfoExt(self, vehInfo, setupIndexes):
        self.__ammunitionPanel.setRespawnInfoExt(vehInfo, setupIndexes)

    def setLaneState(self, laneID, enabled, blockedText):
        if laneID not in self.__buttonStates or self.__buttonStates[laneID] is not enabled:
            self.as_setLaneStateS(laneID, enabled, blockedText)
            self.__buttonStates[laneID] = enabled

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def __makePointVO(self, x=0, y=0, isEnemyNear=False):
        return {'x': x,
         'y': y,
         'isEnemyNear': isEnemyNear}

    def __playCountDownSound(self, play):
        if play is True:
            SoundGroups.g_instance.playSound2D(EPIC_TIME_WWEVENTS.EB_RESPAWN_COUNT_DOWN_SOUND_ID[play])
            self.__countDownIsPlaying = True
        else:
            SoundGroups.g_instance.playSound2D(EPIC_TIME_WWEVENTS.EB_RESPAWN_COUNT_DOWN_SOUND_ID[play])
            self.__countDownIsPlaying = False

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __updateSlotData(self, vehs, cooldowns, limits):
        if not isinstance(limits, dict):
            return
        vehLimits = self.__getVehicleLimits(limits)
        slotsStatesData = respawn_utils.getSlotsStatesData(vehs, cooldowns, self.__disabled, vehLimits)
        self.__carousel.updateVehicleStates(slotsStatesData)

    def __getVehicleLimits(self, limits):
        result = []
        for vehCD in next(limits.itervalues()):
            if all([ vehCD in cdList for cdList in limits.itervalues() ]):
                result.append(vehCD)

        return result
