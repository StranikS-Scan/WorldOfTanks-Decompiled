# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/respawn_ctrl.py
from collections import namedtuple, defaultdict
from itertools import izip
import BigWorld
import Event
from constants import RESPAWN_TYPES, REQUEST_COOLDOWN
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.veh_post_progression.battle_cooldown_manager import BattleCooldownManager
from helpers import dependency
from items import vehicles
from post_progression_common import unpackVehSetupsIndexes
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IVehiclePostProgressionController
_Vehicle = namedtuple('_Vehicle', ('intCD', 'strCD', 'battleAbilities', 'crewDescrs', 'customRoleSlotTypeId', 'settings', 'vehPostProgression', 'vehSetups', 'vehSetupsIndexes', 'disabledSwitchGroupIDs'))
_RespawnInfo = namedtuple('_RespawnInfo', ('vehicleID', 'respawnTime', 'respawnType', 'autoRespawnTime', 'respawnZones', 'chosenRespawnZone', 'vehSetupsIndexes'))

class IRespawnView(object):

    def start(self, vehs, isLimited):
        pass

    def show(self, selectedID, vehs, cooldowns, limits=0):
        pass

    def hide(self):
        pass

    def updateTimer(self, timeLeft, vehs, cooldowns, limits=0):
        pass

    def setLimits(self, respawnLimits):
        pass

    def setBattleCtx(self, battleCtx):
        pass

    def setRespawnInfoExt(self, vehInfo, setupIndexes):
        pass


_RESPAWN_SOUND_ID = 'start_battle'
_SWITCH_SETUPS_ACTION = 0

class RespawnsController(ViewComponentsController):
    __slots__ = ('__weakref__', '__isUIInited', '__vehicles', '__cooldowns', '__respawnInfo', '__timerCallback', '__eManager', 'onRespawnVisibilityChanged', 'onVehicleDeployed', 'onRespawnInfoUpdated', 'onPlayerRespawnLivesUpdated', 'onTeamRespawnLivesRestored', 'onRespawnVehiclesUpdated', '__isUiShown', '__isShowUiAllowed', '__limits', '__playerRespawnLives', '__respawnSoundNotificationRequest', '__respawnSoundNotificationCallbackID', '__battleCtx', '__setupsIndexes', '__cooldownsManager')
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)
    __battleSession = dependency.descriptor(IBattleSessionProvider)
    showUiAllowed = property(lambda self: self.__isShowUiAllowed, lambda self, value: self.__setShowUiAllowed(value))
    respawnInfo = property(lambda self: self.__respawnInfo)
    playerLives = property(lambda self: self.__playerRespawnLives)
    vehicles = property(lambda self: self.__vehicles)

    def __init__(self, setup):
        super(RespawnsController, self).__init__()
        self.__isUIInited = False
        self.__vehicles = {}
        self.__cooldowns = {}
        self.__limits = {}
        self.__respawnInfo = None
        self.__timerCallback = None
        self.__isUiShown = False
        self.__isShowUiAllowed = False
        self.__playerRespawnLives = -1
        self.__respawnSoundNotificationCallbackID = None
        self.__respawnSoundNotificationRequest = False
        self.__battleCtx = setup.battleCtx
        self.__setupsIndexes = defaultdict(dict)
        self.__cooldownsManager = BattleCooldownManager()
        self.__eManager = Event.EventManager()
        self.onRespawnVisibilityChanged = Event.Event(self.__eManager)
        self.onVehicleDeployed = Event.Event(self.__eManager)
        self.onRespawnInfoUpdated = Event.Event(self.__eManager)
        self.onPlayerRespawnLivesUpdated = Event.Event(self.__eManager)
        self.onTeamRespawnLivesRestored = Event.Event(self.__eManager)
        self.onRespawnVehiclesUpdated = Event.Event(self.__eManager)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.RESPAWN

    def startControl(self):
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def stopControl(self):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__stopTimer()
        self.__clearRespawnSoundNotificationCallback()
        self.clearViewComponents()
        self.__vehicles = None
        self.__cooldowns = None
        self.__respawnInfo = None
        self.__limits = None
        self.__battleCtx = None
        self.__setupsIndexes = None
        self.__cooldownsManager.reset(_SWITCH_SETUPS_ACTION)
        self.__cooldownsManager = None
        return

    def setViewComponents(self, *components):
        super(RespawnsController, self).setViewComponents(*components)
        if not self._viewComponents:
            return
        self.__refresh()
        for viewCmp in self._viewComponents:
            viewCmp.setBattleCtx(self.__battleCtx)

    def respawnPlayer(self):
        BigWorld.player().base.respawnController_performRespawn()

    def chooseVehicleForRespawn(self, intCD):
        self.__updateRespawnInfoExt(intCD)
        BigWorld.player().base.respawnController_chooseVehicleForRespawn(intCD)

    def switchVehSetupsLayout(self, vehCD, groupID, layoutIdx):
        if self.__battleSession.isReplayPlaying:
            return
        if self.__cooldownsManager.isInProcess(_SWITCH_SETUPS_ACTION):
            return
        self.__setupsIndexes[vehCD][groupID] = layoutIdx
        self.__updateRespawnInfoExt(vehCD)
        self.__cooldownsManager.process(_SWITCH_SETUPS_ACTION, REQUEST_COOLDOWN.POST_PROGRESSION_CELL)
        BigWorld.player().base.respawnController_switchSetup(vehCD, groupID, layoutIdx)

    def movingToRespawn(self):
        self.__respawnInfo = None
        self.__stopTimer()
        self.__respawnSoundNotificationRequest = True
        return

    def spawnVehicle(self, _):
        if BigWorld.player().isVehicleAlive:
            self.__respawnInfo = None
            self.onVehicleDeployed()
        self.__setRespawnSoundNotificationCallback()
        self.__hide()
        return

    def updateRespawnVehicles(self, vehsList):
        self.__vehicles = {}
        battleAbilities = {vehTypeCompDescr:compDescrList for vehTypeCompDescr, compDescrList in izip(BigWorld.player().ammoViews['vehTypeCompDescrs'], BigWorld.player().ammoViews['compDescrs'])}
        for v in vehsList:
            descr = vehicles.getVehicleType(v['compDescr'])
            self.__vehicles[descr.compactDescr] = _Vehicle(descr.compactDescr, v['compDescr'], battleAbilities.get(descr.compactDescr, ()), v['crewCompactDescrs'], v['customRoleSlotTypeId'], v['settings'], v['vehPostProgression'], v['vehSetups'], unpackVehSetupsIndexes(list(v['vehSetupsIndexes'])), v['vehDisabledSetupSwitches'])

        self.onRespawnVehiclesUpdated(self.__vehicles)
        if self.__respawnInfo is not None and self.__respawnInfo.vehicleID in self.__vehicles:
            self.__updateRespawnInfoExt(self.__respawnInfo.vehicleID)
        return

    def updateRespawnCooldowns(self, cooldowns):
        self.__cooldowns = cooldowns

    def updateRespawnInfo(self, respawnInfo):
        intCD = vehicles.getVehicleTypeCompactDescr(respawnInfo['compDescr'])
        self.__respawnInfo = _RespawnInfo(intCD, respawnInfo['manualRespawnPiT'], respawnInfo['respawnType'], respawnInfo['autoRespawnPiT'], respawnInfo['respawnZones'], respawnInfo['chosenRespawnZone'], unpackVehSetupsIndexes(list(respawnInfo['vehSetupsIndexes'])))
        self.__setupsIndexes[intCD].update(self.__respawnInfo.vehSetupsIndexes)
        self.__refresh()
        self.onRespawnInfoUpdated(self.__respawnInfo)
        if self.__vehicles is not None and intCD in self.__vehicles:
            self.__updateRespawnInfoExt(intCD)
        return

    def updateVehicleLimits(self, respawnLimits):
        self.__limits = respawnLimits
        if not self._viewComponents:
            return
        for viewCmp in self._viewComponents:
            viewCmp.setLimits(respawnLimits)

    def updatePlayerRespawnLives(self, respawnLives):
        self.__playerRespawnLives = respawnLives
        self.onPlayerRespawnLivesUpdated(respawnLives)

    def restoredTeamRespawnLives(self, teams):
        self.onTeamRespawnLivesRestored(teams)

    def isRespawnVisible(self):
        return self.__isUiShown

    def getLimits(self):
        return self.__limits

    def _show(self):
        if not self._viewComponents:
            return
        if not self.__isUIInited:
            self.__isUIInited = True
            isLimited = self.__respawnInfo.respawnType == RESPAWN_TYPES.LIMITED
            for viewCmp in self._viewComponents:
                viewCmp.start(self.__vehicles, isLimited)

        for viewCmp in self._viewComponents:
            viewCmp.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns, self.__limits)

        self.__isUiShown = True
        self.__startTimer()
        self.onRespawnVisibilityChanged(True)
        self.__startTimer()
        self.__isUiShown = True

    def __setShowUiAllowed(self, value):
        self.__isShowUiAllowed = value
        self.__refresh()

    def __clearRespawnSoundNotificationCallback(self):
        if self.__respawnSoundNotificationCallbackID is not None:
            BigWorld.cancelCallback(self.__respawnSoundNotificationCallbackID)
            self.__respawnSoundNotificationCallbackID = None
        return

    def __setRespawnSoundNotificationCallback(self):
        self.__clearRespawnSoundNotificationCallback()
        if self.__respawnSoundNotificationRequest:
            self.__respawnSoundNotificationCallbackID = BigWorld.callback(1.0, self.__triggerRespawnSoundNotification)
            self.__respawnSoundNotificationRequest = False

    def __triggerRespawnSoundNotification(self):
        self.__respawnSoundNotificationCallbackID = None
        notifications = getSoundNotifications()
        if notifications is not None:
            notifications.play(_RESPAWN_SOUND_ID)
        return

    def __onRoundFinished(self, *args):
        self.__hide()

    def __refresh(self):
        if self.__respawnInfo is None or self._viewComponents is None:
            return
        else:
            if self.__respawnInfo is not None and not self.__isUiShown and self.__isShowUiAllowed:
                self._show()
            elif self.__isUiShown and not self.__isShowUiAllowed:
                self.__hide()
            elif self.__isUiShown:
                self.__stopTimer()
                self.__startTimer()
            return

    def __hide(self):
        if not self.__isUiShown:
            return
        self.__stopTimer()
        self.__setupsIndexes.clear()
        self.__cooldownsManager.reset(_SWITCH_SETUPS_ACTION)
        if not self._viewComponents:
            return
        for viewCmp in self._viewComponents:
            viewCmp.hide()
            self.__isUiShown = False
            self.onRespawnVisibilityChanged(False)

    def __startTimer(self):
        self.__timerCallback = None
        if self.__respawnInfo is None:
            return
        else:
            respawnTime = self.__respawnInfo.respawnTime
            timeLeft = max(0, respawnTime - BigWorld.serverTime())
            autoRespawnTime = self.__respawnInfo.autoRespawnTime
            autoTimeLeft = max(0, autoRespawnTime - BigWorld.serverTime())
            if self.__isUiShown:
                for viewCmp in self._viewComponents:
                    viewCmp.updateTimer([timeLeft, autoTimeLeft], self.__vehicles, self.__cooldowns, self.__limits)

            if timeLeft > 0 or autoTimeLeft > 0:
                self.__timerCallback = BigWorld.callback(1, self.__startTimer)
            return

    def __stopTimer(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __updateRespawnInfoExt(self, intCD):
        for component in self._viewComponents:
            component.setRespawnInfoExt(self.__vehicles[intCD], self.__setupsIndexes[intCD])
