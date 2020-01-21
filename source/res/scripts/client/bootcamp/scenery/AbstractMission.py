# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/AbstractMission.py
import weakref
import BattleReplay
import BigWorld
import SoundGroups
from constants import ARENA_PERIOD
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.hints.HintCustom import HintCustom
from bootcamp.scenery.HintLink import HintLink
from bootcamp.scenery.MarkerLink import MarkerLink
from bootcamp.scenery.TriggerListener import TriggerListener
from bootcamp.scenery.VehicleLink import VehicleLink
from bootcamp.BootcampConstants import HINT_TYPE
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from debug_utils import LOG_ERROR
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
import TriggersManager
import MusicControllerWWISE as MC
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider

class AbstractMission(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, assistant):
        super(AbstractMission, self).__init__()
        LOG_DEBUG_DEV_BOOTCAMP('Mission {0} __init__'.format(self.__class__.__name__))
        self.__vehicles = []
        self.__hints = []
        self.__markers = []
        self.__detectedVehicles = set()
        self.__triggerListener = TriggerListener(self)
        self.__callbackID = None
        self._markerMgrRef = weakref.proxy(assistant.getMarkers())
        self._avatar = BigWorld.player()
        self._assistant = assistant
        self._actionEventMap = {BOOTCAMP_BATTLE_ACTION.PLAYER_MOVE: self.__onActionPlayerMove,
         BOOTCAMP_BATTLE_ACTION.PLAYER_SPOTTED: self.__onActionPlayerSpoted,
         BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE: self.__onActionPlayerHitVehicle,
         BOOTCAMP_BATTLE_ACTION.SET_SCENERY_CONSTANT: self.__onActionSetSceneryConstant}
        self.__combatMusic = None
        BigWorld.player().arena.onPeriodChange += self._onPeriodChange
        return

    def destroy(self):
        self.stop()
        self.__vehicles = []
        self.__hints = None
        self.__markers = None
        self.__detectedVehicles = None
        self.__triggerListener.destroy()
        self.__triggerListener = None
        self._avatar = None
        self._assistant = None
        self._actionEventMap = None
        g_bootcampEvents.onBattleAction -= self.__onBattleAction
        if BigWorld.player().arena:
            BigWorld.player().arena.onPeriodChange -= self._onPeriodChange
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        LOG_DEBUG_DEV_BOOTCAMP('Mission {0} destroy'.format(self.__class__.__name__))
        return

    @staticmethod
    def updatePeriod():
        pass

    def start(self):
        LOG_DEBUG_DEV_BOOTCAMP('Mission {0} start'.format(self.__class__.__name__))
        for id_, vehicle in self._avatar.arena.vehicles.items():
            vehLink = self.__getVehLink(id_)
            if vehLink is None:
                self.createVehicle(vehicle['name'])

        MC.g_musicController.skipArenaChanges = True
        self._avatar.muteSounds(())
        for vehicle in self._avatar.vehicles:
            self.__onVehicleEnterWorld(vehicle)

        hintSystem = self._assistant.getHintSystem()
        for hintLink in self.__hints:
            hint = HintCustom(self._avatar, hintLink.hintTypeId, hintLink.timeCompleted, hintLink.cooldownAfter, hintLink.message, hintLink.timeStartDelay, hintLink.timeDuration, hintLink.timeInnerCooldown, hintLink.timeCompleteDuration, hintLink.voiceover)
            hintLink.hintObject = hint
            hintSystem.addHint(hint)
            hint.start()

        self._avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        self._avatar.onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        g_bootcampEvents.onBattleAction += self.__onBattleAction
        self._avatar.arena.onTeamBasePointsUpdate += self.onTeamBasePointsUpdate
        self._avatar.arena.onTeamBaseCaptured += self.onTeamBaseCaptured
        for markerLink in self.__markers:
            markerLink.hide(True)

        self.update()
        return

    def stop(self):
        g_bootcampEvents.onBattleAction -= self.__onBattleAction
        self._avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        self._avatar.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        arena = self._avatar.arena
        if arena is not None:
            self._avatar.arena.onTeamBasePointsUpdate -= self.onTeamBasePointsUpdate
            self._avatar.arena.onTeamBaseCaptured -= self.onTeamBaseCaptured
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        MC.g_musicController.skipArenaChanges = False
        LOG_DEBUG_DEV_BOOTCAMP('Mission {0} stop'.format(self.__class__.__name__))
        return

    def update(self):
        self.__callbackID = BigWorld.callback(self.updatePeriod(), self.update)

    def createMarker(self, name):
        markerLink = None
        for marker in self.__markers:
            if marker.name == name:
                markerLink = marker
                break

        if markerLink is None:
            markerLink = MarkerLink(name)
            markerLink.resolve(self._markerMgrRef)
            self.__markers.append(markerLink)
        return markerLink

    def createVehicle(self, name):
        vehLink = None
        for veh in self.__vehicles:
            if veh.name == name:
                vehLink = veh
                break

        if vehLink is None:
            vehLink = VehicleLink({'name': name})
            vehLink.resolve(self._avatar)
            if not vehLink.isValid:
                LOG_ERROR("Vehicle {0} isn't valid".format(vehLink.name))
                return
            self.__vehicles.append(vehLink)
        return vehLink

    def playSound2D(self, soundId):
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            SoundGroups.g_instance.playSound2D(soundId)

    def createHint(self, hintTypeId=HINT_TYPE.HINT_CUSTOM, timeCompleted=0, cooldownAfter=0, message='default message', timeStartDelay=0.4, timeDuration=-1.0, timeInnerCooldown=-1.0, timeCompleteDuration=3.0, voiceover=None):
        hintLink = HintLink(hintTypeId, timeCompleted, cooldownAfter, message, timeStartDelay, timeDuration, timeInnerCooldown, timeCompleteDuration, voiceover)
        self.__hints.append(hintLink)
        return hintLink

    def playerVehicle(self):
        player = BigWorld.player()
        return self.createVehicle(player.name)

    def onPlayerMove(self, flags):
        pass

    def onPlayerShoot(self, aimInfo):
        pass

    def onPlayerDetectEnemy(self, new, lost):
        pass

    def onEnemyDetectPlayer(self, spotedBy):
        pass

    def onReceiveDamage(self, targetVehicle):
        pass

    def onPlayerHit(self, damagedVehicle, flags):
        pass

    def onEnemyObserved(self, isObserved):
        pass

    def onVehicleDestroyed(self, vehicle):
        pass

    def onSetConstant(self, vehicle, name, value):
        return None

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED:
            self.onEnemyObserved(True)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE:
            vehicleId = params['attackerId']
            vehLink = self.__getVehLink(vehicleId)
            self.onReceiveDamage(vehLink)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            aimingInfo = params['aimingInfo']
            self.onPlayerShoot(aimingInfo)
        elif triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED:
            targetId = params['vehicleId']
            vehLink = self.__getVehLink(targetId)
            if vehLink is not None:
                self.onVehicleDestroyed(vehLink)
        elif triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            isVisible = params['isVisible']
            targetId = params['vehicleId']
            new = []
            lost = []
            vehLink = self.__getVehLink(targetId)
            if vehLink is not None:
                if isVisible:
                    new.append(vehLink)
                else:
                    lost.append(vehLink)
                if vehLink.isEnemy:
                    self.onPlayerDetectEnemy(new, lost)
        elif 'name' in params:
            self.onZoneTriggerActivated(params['name'])
        return

    def onTriggerDeactivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED:
            self.onEnemyObserved(False)
        elif 'name' in params:
            self.onZoneTriggerDeactivated(params['name'])

    def onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        pass

    def onZoneTriggerActivated(self, name):
        pass

    def onZoneTriggerDeactivated(self, name):
        pass

    def onTeamBaseCaptured(self, team, baseID):
        pass

    def _onPeriodChange(self, *args):
        if args[0] == ARENA_PERIOD.BATTLE and self.__combatMusic is None:
            player = BigWorld.player()
            if not isPlayerAvatar():
                return
            if player.arena is None:
                return
            arenaType = player.arena.arenaType
            soundEventName = None
            if arenaType.wwmusicSetup is not None:
                soundEventName = arenaType.wwmusicSetup.get('wwmusicRelaxed', None)
            if soundEventName:
                self.__combatMusic = SoundGroups.g_instance.getSound2D(soundEventName)
        return

    def _muteCombatMusic(self):
        if self.__combatMusic is not None and self.__combatMusic.isPlaying:
            self.__combatMusic.stop()
        return

    def _playCombatMusic(self):
        if self.__combatMusic is not None and not self.__combatMusic.isPlaying and not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.__combatMusic.play()
        return

    def __getVehLink(self, vehId):
        for vehLink in self.__vehicles:
            if vehLink.id == vehId:
                return vehLink

        return None

    def __onVehicleEnterWorld(self, vehicle):
        vehLink = self.__getVehLink(vehicle.id)
        if vehLink is not None:
            vehLink.setVehicle(vehicle)
        return

    def __onVehicleLeaveWorld(self, vehicle):
        vehLink = self.__getVehLink(vehicle.id)
        if vehLink is not None:
            vehLink.setVehicle(None)
        return

    def __onBattleAction(self, actionId, actionArgs):
        processor = self._actionEventMap.get(actionId, None)
        if callable(processor):
            processor(actionArgs)
        return

    def __onActionPlayerMove(self, args):
        flags = args[0]
        self.onPlayerMove(flags)

    def __onActionPlayerSpoted(self, args):
        spottedBy = []
        for vehId in args:
            vehLink = self.__getVehLink(vehId)
            if vehLink is not None:
                spottedBy.append(vehLink)

        self.onEnemyDetectPlayer(spottedBy)
        return

    def __onActionPlayerHitVehicle(self, args):
        damagedVehicle = args[0]
        flags = args[1]
        vehLink = self.__getVehLink(damagedVehicle)
        self.onPlayerHit(vehLink, flags)

    def __onActionSetSceneryConstant(self, args):
        vehicleId = args[0]
        vehLink = self.__getVehLink(vehicleId)
        value = args[1]
        bName = bytearray()
        bName.extend(args[2:])
        name = str(bName)
        newValue = self.onSetConstant(vehLink, name, value)
        if newValue is not None:
            value = newValue
        setattr(self, name, value)
        return
