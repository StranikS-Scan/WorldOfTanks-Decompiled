# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/markers2d.py
import math
from functools import partial
import BattleReplay
import BigWorld
import constants
from CTFManager import g_ctfManager
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import NEUTRAL_TEAM, PLAYER_GUI_PROPS
from helpers import i18n
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.event_mark1 import common
from helpers import time_utils

class Mark1VehicleMarkerPlugin(plugins.MarkerPlugin, IArenaVehiclesController):
    """
    This plugin is only for event mark1.
    """
    __slots__ = ('__vehiclesMarkers', '_playerVehicleID', '_mark1Markers')

    def __init__(self, parentObj):
        super(Mark1VehicleMarkerPlugin, self).__init__(parentObj)
        self.__vehiclesMarkers = {}
        self._playerVehicleID = 0
        self._mark1Markers = {}

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def init(self, *args):
        super(Mark1VehicleMarkerPlugin, self).init()
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        return

    def fini(self):
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        super(Mark1VehicleMarkerPlugin, self).fini()
        return

    def start(self):
        super(Mark1VehicleMarkerPlugin, self).start()
        self._playerVehicleID = avatar_getter.getPlayerVehicleID()
        g_sessionProvider.addArenaCtrl(self)

    def stop(self):
        self.__vehiclesMarkers = {}
        self._mark1Markers = {}
        super(Mark1VehicleMarkerPlugin, self).stop()

    def setTeamKiller(self, vID):
        if vID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vID].getMarkerID()
        ctx = g_sessionProvider.getCtx()
        if not ctx.isTeamKiller(vID=vID) or ctx.isSquadMan(vID=vID):
            return
        self._invokeMarker(handle, 'setEntityName', [PLAYER_GUI_PROPS.teamKiller.name()])

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(g_sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.addVehicleInfo(vInfo, arenaDP)

    def addVehicleInfo(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID != self._playerVehicleID:
            active = self.__isVehicleActive(vehicleID)
            vehicle = BigWorld.entity(vehicleID)
            if vehicle:
                guiProps = g_sessionProvider.getCtx().getPlayerGuiProps(vehicleID, vInfo.team)
                self.__addOrUpdateVehicleMarker(vehicle.proxy, vInfo, guiProps, active)

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            self.__setEntityName(vInfo, arenaDP)

    def invalidatePlayerStatus(self, flags, vInfo, arenaDP):
        self.__setEntityName(vInfo, arenaDP)

    def _updateFlagbearerState(self, vehID, newState):
        if vehID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehID]
            if marker.isActive() and marker.setFlagBearer(newState):
                flagType = self.__getFlagTypeByVehicle(vehID)
                self._invokeMarker(marker.getMarkerID(), 'updateFlagBearerState', [newState, flagType])

    def _hideVehicleMarker(self, vehicleID):
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehicleID]
            if marker.setActive(False):
                self._setMarkerActive(marker.getMarkerID(), False)
                self._setMarkerMatrix(marker.getMarkerID(), None)
                marker.detach()
        return

    def _notifyVehicleMarkerAdded(self, vehicleID, isMark1):
        pass

    def _getVehicleMarkers(self):
        return self.__vehiclesMarkers

    def _destroyVehicleMarker(self, vehicleID):
        if vehicleID in self._mark1Markers:
            del self._mark1Markers[vehicleID]
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers.pop(vehicleID)
            self._destroyMarker(marker.getMarkerID())
            marker.destroy()

    def __isVehicleActive(self, vehicleID):
        active = False
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None and vehicle.isStarted:
            active = True
        elif vehicleID in BigWorld.player().arena.positions:
            active = True
        return active

    def __addOrUpdateVehicleMarker(self, vProxy, vInfo, guiProps, active=True):
        speaking = self.bwProto.voipController.isPlayerSpeaking(vInfo.player.accountDBID)
        flagBearer = g_ctfManager.getVehicleCarriedFlagID(vInfo.vehicleID) is not None
        flagType = self.__getFlagTypeByVehicle(vInfo.vehicleID)
        if active:
            mProv = vProxy.model.node('HP_gui')
        else:
            mProv = None
        if vInfo.vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vInfo.vehicleID]
            if marker.setActive(active):
                self._setMarkerMatrix(marker.getMarkerID(), mProv)
                self._setMarkerActive(marker.getMarkerID(), active)
                self.__updateVehicleStates(marker, speaking, vProxy.health, flagBearer, flagType)
                marker.attach(vProxy)
        else:
            hunting = VehicleActions.isHunting(vInfo.events)
            battleCtx = g_sessionProvider.getCtx()
            result = battleCtx.getPlayerFullNameParts(vProxy.id)
            markerID = self._createMarkerWithMatrix(mProv, 'VehicleMarkerMark1UI')
            self.__vehiclesMarkers[vInfo.vehicleID] = plugins.VehicleMarker(markerID, vProxy, self._parentObj.getCanvasProxy(), active)
            vType = vInfo.vehicleType
            squadIndex = 0
            if g_sessionProvider.arenaVisitor.gui.isFalloutMultiTeam() and vInfo.squadIndex:
                squadIndex = vInfo.squadIndex
            if vType.isMark1:
                vehClassTag = guiProps.name() + 'Mark1'
                self._mark1Markers[vInfo.vehicleID] = markerID
            else:
                vehClassTag = vType.classTag
            self._invokeMarker(markerID, 'setVehicleInfo', [vehClassTag,
             vType.iconPath,
             result.vehicleName,
             vType.level,
             result.playerFullName,
             result.playerName,
             result.clanAbbrev,
             result.regionCode,
             vType.maxHealth,
             guiProps.name(),
             hunting,
             squadIndex])
            if not vProxy.isAlive():
                self.__updateMarkerState(markerID, 'dead', True)
            if active:
                self.__updateVehicleStates(self.__vehiclesMarkers[vInfo.vehicleID], speaking, vProxy.health, flagBearer, flagType)
        self._notifyVehicleMarkerAdded(vInfo.vehicleID, vInfo.vehicleType.isMark1)
        return

    def __updateVehicleStates(self, marker, speaking, health, flagBearer, flagType):
        handle = marker.getMarkerID()
        if marker.setSpeaking(speaking):
            self._invokeMarker(handle, 'setSpeaking', [speaking])
        if marker.setFlagBearer(flagBearer):
            self._invokeMarker(handle, 'updateFlagBearerState', [flagBearer, flagType])
        self._invokeMarker(handle, 'setHealth', [health])

    def __setEntityName(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vehicleID].getMarkerID()
        self._invokeMarker(handle, 'setEntityName', [arenaDP.getPlayerGuiProps(vehicleID, vInfo.team).name()])

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        self.__addOrUpdateVehicleMarker(vProxy, vInfo, guiProps)

    def __onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vehicleID].getMarkerID()
        if eventID == _EVENT_ID.VEHICLE_HIT:
            self.__updateMarkerState(handle, 'hit', value)
        elif eventID == _EVENT_ID.VEHICLE_ARMOR_PIERCED:
            self.__updateMarkerState(handle, 'hit_pierced', value)
        elif eventID == _EVENT_ID.VEHICLE_DEAD:
            self.__updateMarkerState(handle, 'dead', value)
        elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
            self.__showActionMarker(handle, value)
        elif eventID == _EVENT_ID.VEHICLE_HEALTH:
            self.__updateVehicleHealth(handle, *value)

    def __updateMarkerState(self, handle, newState, isImmediate=False):
        self._invokeMarker(handle, 'updateState', [newState, isImmediate])

    def __showActionMarker(self, handle, newState):
        self._invokeMarker(handle, 'showActionMarker', [newState])

    def __updateVehicleHealth(self, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', [newHealth])
        else:
            self._invokeMarker(handle, 'updateHealth', [newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID]])

    def __onPlayerSpeaking(self, accountDBID, flag):
        """
        Listener for event g_messengerEvents.voip.onPlayerSpeaking.
        :param accountDBID: player db ID
        :param flag: isSpeaking (true or false)
        """
        vehicleID = g_sessionProvider.getCtx().getVehIDByAccDBID(accountDBID)
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehicleID]
            if marker.setSpeaking(flag):
                self._invokeMarker(marker.getMarkerID(), 'setSpeaking', [flag])

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == avatar_getter.getPlayerVehicleID():
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = g_sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN

    @staticmethod
    def __getFlagTypeByVehicle(vehicleID):
        flagID = g_ctfManager.getVehicleCarriedFlagID(vehicleID)
        result = ''
        if flagID is not None:
            ctx = g_sessionProvider.getCtx()
            flagType = g_ctfManager.getFlagType(flagID)
            result = common.getMark1FlagType(flagType, ctx.isAlly(vehicleID))
        return result


class Mark1RespawnableVehicleMarkerPlugin(Mark1VehicleMarkerPlugin):

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)


class Mark1VehicleAndFlagsMarkerPlugin(Mark1RespawnableVehicleMarkerPlugin):
    """
    This plugin handles Flags on 3d scene, also it switches flagBearer state for the base (vehicles) class.
    The flags are created at start and then they can be only updated for the remain life cycle.
    """
    __slots__ = ('__markers', '__spawnPoints', '__playerTeam', '__isTeamPlayer')

    def __init__(self, parentObj):
        super(Mark1VehicleAndFlagsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__spawnPoints = []
        self.__playerTeam = NEUTRAL_TEAM
        self.__isTeamPlayer = False

    def init(self):
        super(Mark1VehicleAndFlagsMarkerPlugin, self).init()
        g_ctfManager.onFlagSpawning += self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase += self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle += self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onAbsorbed
        g_ctfManager.onFlagRemoved += self.__onRemoved

    def fini(self):
        g_ctfManager.onFlagSpawning -= self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase -= self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onRemoved
        super(Mark1VehicleAndFlagsMarkerPlugin, self).fini()

    def start(self):
        visitor = g_sessionProvider.arenaVisitor
        self.__playerTeam = avatar_getter.getPlayerTeam()
        self.__isTeamPlayer = not visitor.isSoloTeam(self.__playerTeam)
        self.__spawnPoints = visitor.type.getFlagSpawnPoints()
        for flagID, flagInfo in g_ctfManager.getFlags():
            vehicleID = flagInfo['vehicle']
            if vehicleID is None:
                flagState = flagInfo['state']
                if flagState == constants.FLAG_STATE.WAITING_FIRST_SPAWN:
                    self.__onFlagSpawning(flagID, flagInfo['respawnTime'])
                elif flagState in (constants.FLAG_STATE.ON_GROUND, constants.FLAG_STATE.ON_SPAWN):
                    self.__onSpawnedAtBase(flagID, flagInfo['team'], flagInfo['minimapPos'])

        super(Mark1VehicleAndFlagsMarkerPlugin, self).start()
        return

    def stop(self):
        for flagMarker in self.__markers.values():
            self.__cancelCallback(flagMarker)

        self.__markers = None
        self.__spawnPoints = None
        super(Mark1VehicleAndFlagsMarkerPlugin, self).stop()
        return

    def _notifyVehicleMarkerAdded(self, vehicleID, isMark1):
        self.__updateMark1AbsorbState()

    def __addOrUpdateFlagMarker(self, flagID, flagPos, marker):
        position = flagPos + common.FLAG_MARKER2D_POSITION_ADJUSTMENT
        if flagID in self.__markers:
            flagMarker = self.__markers[flagID]
            handle = flagMarker.getMarkerID()
            self._setMarkerPos(handle, position)
            if flagMarker.setActive(True):
                self._setMarkerActive(handle, True)
            self.__cancelCallback(flagMarker)
        else:
            handle = self._createMarker(position, common.FLAG_MARK1)
            self.__markers[flagID] = plugins.FlagMarker(handle)
        self._invokeMarker(handle, 'setIcon', [marker])

    def __cancelCallback(self, flagMarker):
        callbackID = flagMarker.getCallbackID()
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
            flagMarker.setCallbackID(None)
            self._invokeMarker(flagMarker.getMarkerID(), 'setLabel', '')
        return

    def __hideFlagMarker(self, flagID):
        if flagID in self.__markers:
            flagMarker = self.__markers[flagID]
            if flagMarker.setActive(False):
                self._setMarkerActive(flagMarker.getMarkerID(), False)
            self.__cancelCallback(flagMarker)

    def __initTimer(self, timer, flagID):
        if flagID not in self.__markers:
            LOG_ERROR('VehicleAndFlagsMarkerPlugin does not have marker with flag id: ', flagID)
            return
        else:
            timer -= 1
            flagMarker = self.__markers[flagID]
            if timer < 0:
                flagMarker.setCallbackID(None)
                self._invokeMarker(flagMarker.getMarkerID(), 'setLabel', '')
                return
            self._invokeMarker(flagMarker.getMarkerID(), 'setLabel', [i18n.makeString(INGAME_GUI.FLAGS_TIMER, time=str(timer))])
            callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, flagID))
            flagMarker.setCallbackID(callbackId)
            return

    def __onFlagSpawning(self, flagID, respawnTime):
        flagType = settings.FLAG_TYPE.COOLDOWN
        flagPos = self.__spawnPoints[flagID]['position']
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)
        self.__updateMark1AbsorbState()

    def __onSpawnedAtBase(self, flagID, flagTeam, flagPos):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        self.__updateMark1AbsorbState()

    def __onCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self._updateFlagbearerState(vehicleID, True)
        self.__hideFlagMarker(flagID)
        self.__updateMark1AbsorbState()

    def __onDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self._updateFlagbearerState(loserVehicleID, False)
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)
        self.__updateMark1AbsorbState()

    def __onAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if common.isFlagNeedsUpdate(flagID):
            self._updateFlagbearerState(vehicleID, False)
            self.__updateMark1AbsorbState()
        self.__hideFlagMarker(flagID)

    def __onRemoved(self, flagID, flagTeam, vehicleID):
        self.__hideFlagMarker(flagID)
        if vehicleID is not None:
            self._updateFlagbearerState(vehicleID, False)
        self.__updateMark1AbsorbState()
        return

    def __getFlagMarkerType(self, flagID, flagTeam=0):
        flagType = g_ctfManager.getFlagType(flagID)
        return common.getMark1FlagType(flagType, flagTeam == self.__playerTeam)

    def __updateMark1AbsorbState(self):
        flagID = g_ctfManager.getVehicleCarriedFlagID(self._playerVehicleID)
        state = common.getMarkers2DAbsorbState(flagID is not None)
        for markerID in self._mark1Markers.itervalues():
            self._invokeMarker(markerID, 'showAnimation', [state])

        return


class Mark1VehiclesFlagsBonusesMarkerPlugin(Mark1VehicleAndFlagsMarkerPlugin):

    def init(self):
        super(Mark1VehiclesFlagsBonusesMarkerPlugin, self).init()
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken += self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken += self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded += self.__onBonusEnded
            bonusCtrl.onBombPlanted += self.__onBombPlanted
            bonusCtrl.onBombExploded += self.__onBombExploded
        return

    def fini(self):
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken -= self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken -= self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded -= self.__onBonusEnded
            bonusCtrl.onBombPlanted -= self.__onBombPlanted
            bonusCtrl.onBombExploded -= self.__onBombExploded
        super(Mark1VehiclesFlagsBonusesMarkerPlugin, self).fini()
        return

    def _notifyVehicleMarkerAdded(self, vehicleID, isMark1):
        super(Mark1VehiclesFlagsBonusesMarkerPlugin, self)._notifyVehicleMarkerAdded(vehicleID, isMark1)
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            if isMark1:
                timeLeft = bonusCtrl.getMark1BombTimeLeft()
                if timeLeft > 0:
                    self.__onBombPlanted(timeLeft)
                else:
                    self.__onBombExploded()
            else:
                bonus = bonusCtrl.getVehicleBonus(vehicleID)
                isBearer = bonus is not None
                self.__updateBonus(vehicleID, isBearer, common.BONUS_EXTRA_TO_NAME[bonus])
        return

    def __onBonusBigGunTaken(self, vehicleID):
        if vehicleID != self._playerVehicleID:
            self.__updateBonus(vehicleID, True, common.BONUS_NAMES.BIG_GUN)

    def __onBonusMachineGunTaken(self, vehicleID):
        if vehicleID != self._playerVehicleID:
            self.__updateBonus(vehicleID, True, common.BONUS_NAMES.MACHINE_GUN)

    def __onBonusEnded(self, vehicleID):
        if vehicleID != self._playerVehicleID:
            self.__updateBonus(vehicleID, False, '')

    def __onBombPlanted(self, timeLeft):
        timeString = time_utils.getTimeLeftFormat(timeLeft)
        for markerID in self._mark1Markers.itervalues():
            self._invokeMarker(markerID, 'bombPlanted', [timeString])

    def __onBombExploded(self):
        for markerID in self._mark1Markers.itervalues():
            self._invokeMarker(markerID, 'hideBombInfo', [markerID])

    def __updateBonus(self, vehicleID, isBearer, bonus):
        markers = self._getVehicleMarkers()
        if vehicleID in markers:
            marker = markers[vehicleID]
            if marker.isActive():
                self._invokeMarker(marker.getMarkerID(), 'updateBonusBearerState', [isBearer, bonus])
