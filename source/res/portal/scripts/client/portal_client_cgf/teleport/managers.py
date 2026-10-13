# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/teleport/managers.py
from functools import partial
import typing
from collections import namedtuple
import BigWorld
import CGF
from GenericComponents import AnimatorComponent
from Sound import Sound3DComponent
from cgf_script.managers_registrator import onAddedQuery
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.battle_control import avatar_getter
from items.utils import isclose
from portal.sounds.sound_helpers import play2DSound
from portal_common_cgf.teleport.components import TeleportEffectComponent, TeleportRequestLinkComponent
from portal_common_cgf.portal_helpers import registerPortalManager
from portal.sounds.sound_constants import PortalBattleSound
from TeleportReplicableComponent import TeleportReplicableComponent
if typing.TYPE_CHECKING:
    from PortalBattleStateComponent import PortalBattleStateComponent

class _TeleportAnimations(object):
    BLOCK = 'Teleport_plane_block'
    BLOCK_TO_ON = 'teleport_plane_block_to_on'
    ON = 'teleport_plane_on'
    IN = 'teleport_in'
    OUT = 'teleport_out'
    ON_TO_COOLDOWN = 'teleport_plane_on_to_coldown'
    COOLDOWN_TO_ON = 'teleport_plane_coldown_to_on'
    IDLE = 'teleport_plane_idle'


_TeleportSoundTuple = namedtuple('_TeleportSoundTuple', ['All', 'PC', 'NPC'])

class _TeleportSounds(object):
    MAP = {_TeleportAnimations.BLOCK: _TeleportSoundTuple(None, None, None),
     _TeleportAnimations.BLOCK_TO_ON: _TeleportSoundTuple(PortalBattleSound.TELEPORT_PLANE_BLOCK_TO_ON, None, None),
     _TeleportAnimations.ON: _TeleportSoundTuple(PortalBattleSound.TELEPORT_PLANE_ON, None, None),
     _TeleportAnimations.IN: _TeleportSoundTuple(None, PortalBattleSound.TELEPORT_PLANE_IN_PC, None),
     _TeleportAnimations.OUT: _TeleportSoundTuple(None, PortalBattleSound.TELEPORT_PLANE_OUT_PC, None),
     _TeleportAnimations.ON_TO_COOLDOWN: _TeleportSoundTuple(PortalBattleSound.TELEPORT_PLANE_ON_TO_COOLDOWN, None, None),
     _TeleportAnimations.COOLDOWN_TO_ON: _TeleportSoundTuple(PortalBattleSound.TELEPORT_PLANE_COOLDOWN_TO_ON, None, None),
     _TeleportAnimations.IDLE: _TeleportSoundTuple(PortalBattleSound.TELEPORT_PLANE_IDLE, None, None)}


class _TeleportTransitions(object):
    MAP = {_TeleportAnimations.BLOCK_TO_ON: _TeleportAnimations.ON,
     _TeleportAnimations.ON_TO_COOLDOWN: _TeleportAnimations.IDLE,
     _TeleportAnimations.COOLDOWN_TO_ON: _TeleportAnimations.ON}


@registerPortalManager(CGF.DomainOption.DomainClient)
class TeleportManager(CGF.ComponentManager):

    def __init__(self):
        super(TeleportManager, self).__init__()
        self.__lastFinishTime = {}
        self.__animationCallbacks = {}
        self.__npcTeleportOrigin = {}
        TeleportReplicableComponent.onTeleportLinked += self.__onTeleportLinked
        TeleportReplicableComponent.onTeleportOccupied += self.__onTeleportOccupied
        TeleportReplicableComponent.onTeleportFreed += self.__onTeleportFreed
        TeleportReplicableComponent.onTeleportingChanged += self.__onTeleportingChanged
        TeleportReplicableComponent.onCooldownChanged += self.__onCooldownChanged

    def destroy(self):
        TeleportReplicableComponent.onCooldownChanged -= self.__onCooldownChanged
        TeleportReplicableComponent.onTeleportingChanged -= self.__onTeleportingChanged
        TeleportReplicableComponent.onTeleportFreed -= self.__onTeleportFreed
        TeleportReplicableComponent.onTeleportOccupied -= self.__onTeleportOccupied
        TeleportReplicableComponent.onTeleportLinked -= self.__onTeleportLinked
        self.__lastFinishTime = None
        self.__npcTeleportOrigin = None
        for callbackID in self.__animationCallbacks.values():
            BigWorld.cancelCallback(callbackID)

        self.__animationCallbacks = None
        return

    @property
    def hm(self):
        return CGF.HierarchyManager(self.spaceID)

    @property
    def battleState(self):
        arenaInfo = BigWorld.player().arena.arenaInfo
        return arenaInfo.portalBattleStateComponent

    @onAddedQuery(CGF.GameObject, TeleportReplicableComponent)
    def onAdded(self, teleportGO, comp):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if animationsGO:
            self.__changeAnimation(animationsGO, _TeleportAnimations.BLOCK, None)
        return

    @staticmethod
    def getCampTeleport(teleportGO, spaceID):
        _, campTeleportGO = TeleportManager.__getTeleportTunnel(teleportGO, spaceID)
        return campTeleportGO

    def __onTeleportLinked(self, teleportGO):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        else:
            self.__changeAnimation(animationsGO, _TeleportAnimations.BLOCK_TO_ON, None)
            return

    def __onTeleportOccupied(self, teleportGO, vehicleID):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        self.__changeAnimation(animationsGO, _TeleportAnimations.ON, vehicleID)

    def __onTeleportFreed(self, teleportGO):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        else:
            self.__changeAnimation(animationsGO, _TeleportAnimations.ON, None)
            return

    def __onTeleportingChanged(self, teleportGO, vehicleID, finishTime):
        if vehicleID != BigWorld.player().playerVehicleID:
            if vehicleID and not isclose(finishTime, 0.0):
                self.__npcTeleportOrigin[teleportGO.id] = vehicleID
            return
        lastFinish = self.__lastFinishTime.get(teleportGO.id, 0.0)
        wasTeleporting = not isclose(lastFinish, 0.0)
        isTeleporting = not isclose(finishTime, 0.0)
        if isTeleporting and not wasTeleporting:
            play2DSound(PortalBattleSound.TELEPORT_START)
        elif wasTeleporting and not isTeleporting:
            play2DSound(PortalBattleSound.TELEPORT_LEAVE)
        self.__lastFinishTime[teleportGO.id] = finishTime

    def __onCooldownChanged(self, teleportGO, prevVehicleIDs, curVehicleIDs):
        attachedVehicleID = avatar_getter.getVehicleIDAttached()
        justEntered = attachedVehicleID in curVehicleIDs and attachedVehicleID not in prevVehicleIDs
        justExited = attachedVehicleID in prevVehicleIDs and attachedVehicleID not in curVehicleIDs
        self.__onNpcTeleportFinished(teleportGO, prevVehicleIDs, curVehicleIDs, attachedVehicleID)
        if not justEntered and not justExited:
            return
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        if justEntered:
            lastFinish = self.__lastFinishTime.get(teleportGO.id, 0.0)
            if lastFinish > 0:
                if self.__isCampTeleport(teleportGO):
                    play2DSound(PortalBattleSound.TELEPORT_END)
                animator = animationsGO.findComponentByType(AnimatorComponent)
                outDuration = animator.getDurationByName(_TeleportAnimations.OUT)
                if outDuration > 0:
                    BigWorld.callback(outDuration, partial(self.__changeAnimation, animationsGO, _TeleportAnimations.ON_TO_COOLDOWN, attachedVehicleID))
            else:
                self.__changeAnimation(animationsGO, _TeleportAnimations.IN, attachedVehicleID)
                BigWorld.callback(1.0, partial(self.__changeAnimation, animationsGO, _TeleportAnimations.ON_TO_COOLDOWN, attachedVehicleID))
        else:
            self.__changeAnimation(animationsGO, _TeleportAnimations.COOLDOWN_TO_ON, attachedVehicleID)

    def __onNpcTeleportFinished(self, teleportGO, prevVehicleIDs, curVehicleIDs, attachedVehicleID):
        npcVehicleID = self.__npcTeleportOrigin.pop(teleportGO.id, None)
        if npcVehicleID is None or npcVehicleID == attachedVehicleID:
            return
        elif npcVehicleID in prevVehicleIDs or npcVehicleID not in curVehicleIDs:
            return
        else:
            self.__playNpcTeleportEffects(teleportGO, npcVehicleID)
            return

    def __playNpcTeleportEffects(self, teleportGO, npcVehicleID):
        originAnimationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if originAnimationsGO:
            self.__changeAnimation(originAnimationsGO, _TeleportAnimations.OUT, npcVehicleID)
        baseTeleportGO, campTeleportGO = TeleportManager.__getTeleportTunnel(teleportGO, self.spaceID)
        if not baseTeleportGO or not campTeleportGO:
            return
        destinationGO = campTeleportGO if teleportGO.id == baseTeleportGO.id else baseTeleportGO
        destinationAnimationsGO = self.__getAnimationsGOFromTeleport(destinationGO)
        if destinationAnimationsGO:
            self.__changeAnimation(destinationAnimationsGO, _TeleportAnimations.IN, npcVehicleID)

    def __changeAnimation(self, go, animation, vehicleID=None):
        callbackID = self.__animationCallbacks.pop(go.id, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        animator = go.findComponentByType(AnimatorComponent)
        if not animator:
            LOG_ERROR('Could not find an Animator Component on GO', go.name)
            return
        else:
            if animator.isValid() and animation:
                if animation == _TeleportAnimations.ON:
                    animator.stopLayerByName(_TeleportAnimations.BLOCK_TO_ON)
                    animator.stopLayerByName(_TeleportAnimations.COOLDOWN_TO_ON)
                elif animation == _TeleportAnimations.IN or animation == _TeleportAnimations.OUT:
                    animator.stopLayerByName(_TeleportAnimations.BLOCK)
                    animator.stopLayerByName(_TeleportAnimations.BLOCK_TO_ON)
                    animator.stopLayerByName(_TeleportAnimations.COOLDOWN_TO_ON)
                elif animation == _TeleportAnimations.ON_TO_COOLDOWN:
                    animator.stopLayerByName(_TeleportAnimations.IDLE)
                    animator.stopLayerByName(_TeleportAnimations.ON)
                else:
                    animator.stop()
                animator.startLayerByName(animation)
                sound = _TeleportSounds.MAP.get(animation)
                if sound is not None:
                    soundName = None
                    if sound.All is not None:
                        soundName = sound.All
                    elif vehicleID is not None:
                        isPC = vehicleID == BigWorld.player().playerVehicleID
                        soundName = sound.PC if isPC else sound.NPC
                    if soundName is not None:
                        self.__playTeleport3DSound(go, soundName)
            nextLayer = _TeleportTransitions.MAP.get(animation)
            if nextLayer is not None:
                duration = animator.getDurationByName(animation)
                if duration > 0:
                    self.__animationCallbacks[go.id] = BigWorld.callback(duration, partial(self.__onLayerFinished, go, nextLayer, vehicleID))
            return

    def __onLayerFinished(self, go, nextLayer, vehicleID=None):
        self.__animationCallbacks.pop(go.id, None)
        self.__changeAnimation(go, nextLayer, vehicleID)
        return

    def __getAnimationsGOFromTeleport(self, teleportGO):
        data = self.hm.findComponentsInHierarchy(teleportGO, TeleportEffectComponent)
        if data:
            if len(data) != 1:
                LOG_WARNING('[PortalBattle]: %s must have only 1 child with TeleportEffectComponent' % (teleportGO.name,))
            return data[0][0]
        else:
            LOG_ERROR('TeleportEffectComponent is missing in the hierarchy', teleportGO.name)
            return None

    def __playTeleport3DSound(self, teleportGO, sound):
        soundComponent = teleportGO.findComponentByType(Sound3DComponent)
        if soundComponent:
            teleportGO.removeComponent(soundComponent)
        teleportGO.createComponent(Sound3DComponent, sound, sound, True)

    @staticmethod
    def __isBaseTeleport(teleportGO):
        return bool(teleportGO.findComponentByType(TeleportRequestLinkComponent))

    @staticmethod
    def __isCampTeleport(teleportGO):
        return not teleportGO.findComponentByType(TeleportRequestLinkComponent)

    @staticmethod
    def __getTeleportTunnel(teleportGO, spaceID):
        teleportComponent = teleportGO.findComponentByType(TeleportReplicableComponent)
        query = CGF.Query(spaceID, (CGF.GameObject, TeleportReplicableComponent))
        tunnelTeleports = [ go for go, component in query if component.index == teleportComponent.index ]
        if len(tunnelTeleports) != 2:
            return (None, None)
        else:
            baseTeleportGO = None
            campTeleportGO = None
            for go in tunnelTeleports:
                if TeleportManager.__isBaseTeleport(go):
                    baseTeleportGO = go
                campTeleportGO = go

            return (baseTeleportGO, campTeleportGO)
