# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/teleport/managers.py
import typing
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
from shared_utils import nextTick
if typing.TYPE_CHECKING:
    from PortalBattleStateComponent import PortalBattleStateComponent

class _TeleportAnimations(object):
    ACTIVE = 'active'
    OCCUPIED = 'occupied'
    INACTIVE = 'inactive'


@registerPortalManager(CGF.DomainOption.DomainClient)
class TeleportManager(CGF.ComponentManager):
    __MODEL_GO_NAME = 'model'
    __FLASH_GO_NAME = 'flash'

    def __init__(self):
        super(TeleportManager, self).__init__()
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
            self.__changeAnimation(animationsGO, _TeleportAnimations.INACTIVE)

    @staticmethod
    def getCampTeleport(teleportGO, spaceID):
        _, campTeleportGO = TeleportManager.__getTeleportTunnel(teleportGO, spaceID)
        return campTeleportGO

    def __onTeleportLinked(self, teleportGO):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        self.__activateModel(animationsGO)
        self.__activateTeleportFlash(animationsGO)
        if self.__isCampTeleport(teleportGO):
            self.__playTeleport3DSound(teleportGO, PortalBattleSound.TELEPORT_ON)

    def __onTeleportOccupied(self, teleportGO, vehicleID):
        self.__changeModelAnimation(teleportGO, _TeleportAnimations.OCCUPIED)

    def __onTeleportFreed(self, teleportGO):
        self.__changeModelAnimation(teleportGO, _TeleportAnimations.ACTIVE)

    def __onTeleportingChanged(self, teleportGO, vehicleID, finishTime):
        if vehicleID == avatar_getter.getVehicleIDAttached():
            isTeleporting = not isclose(finishTime, 0.0)
            if isTeleporting:
                play2DSound(PortalBattleSound.TELEPORT_START)
            else:
                play2DSound(PortalBattleSound.TELEPORT_LEAVE)

    def __onCooldownChanged(self, teleportGO, isCooldown):
        if isCooldown and self.__isTeleportOccupiedBy(teleportGO, avatar_getter.getVehicleIDAttached()):
            if self.__isCampTeleport(teleportGO):
                play2DSound(PortalBattleSound.TELEPORT_END)

    def __isTeleportOccupiedBy(self, teleportGO, vehicleID):
        teleportComponent = teleportGO.findComponentByType(TeleportReplicableComponent)
        return teleportComponent.teleportingVehicleID == vehicleID

    @nextTick
    def __changeAnimation(self, go, animation):
        animator = go.findComponentByType(AnimatorComponent)
        if not animator:
            LOG_ERROR('Could not find an Animator Component on GO', go.name)
            return
        if animator.isValid():
            animator.stop()
            if animation:
                animator.startLayerByName(animation)

    def __activateModel(self, animationsGO):
        self.__changeAnimation(animationsGO, None)
        modelGO = self.__getChild(animationsGO, self.__MODEL_GO_NAME)
        if modelGO:
            modelGO.activate()
        return

    def __changeModelAnimation(self, teleportGO, animation):
        animationsGO = self.__getAnimationsGOFromTeleport(teleportGO)
        if not animationsGO:
            return
        modelGO = self.__getChild(animationsGO, self.__MODEL_GO_NAME)
        if not modelGO:
            return
        self.__changeAnimation(modelGO, animation)

    def __activateTeleportFlash(self, animationsGO):
        flashGO = self.__getChild(animationsGO, self.__FLASH_GO_NAME)
        if flashGO:
            flashGO.activate()

    def __getChild(self, go, childName):
        for childGO in self.hm.getChildrenIncludingInactive(go):
            if childGO.name == childName:
                return childGO

        LOG_ERROR('Could not find {} on {}'.format(childName, go.name))
        return None

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
