# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/game_objects/battleroyale/TrapPoint.py
import logging
import BigWorld
import GenericComponents
import NetworkComponents
from helpers import dependency
import Vehicle
from gui.game_control.br_battle_sounds import BREvents
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener
_logger = logging.getLogger(__name__)

class TrapAffectComponent(IVehicleCountListener):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, gameObject, config, spaceID):
        self.__instances = 1
        self.__gameObject = gameObject
        self.__spaceID = spaceID
        self.__path = config.path
        self.__rate = config.rate
        self.__offset = config.offset
        self.__particle = None
        self.__soundPlaying = False
        return

    def activate(self):
        self.__particle = self.__gameObject.createComponent(GenericComponents.ParticleComponent, self.__path, self.__rate, self.__spaceID, self.__offset)
        playerVehicleImpl = _getPlayerVehicleImpl(self.__gameObject)
        if playerVehicleImpl is not None and playerVehicleImpl.isPlayerVehicle:
            BREvents.playSound(BREvents.TRAP_POINT_ENTER)
            self.__soundPlaying = True
        ctrl = self.__guiSessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.addRuntimeView(self)
        return

    def deactivate(self):
        if self.__particle is not None:
            self.__gameObject.removeComponent(self.__particle)
        if self.__soundPlaying:
            playerVehicleImpl = _getPlayerVehicleImpl(self.__gameObject)
            if playerVehicleImpl is not None and playerVehicleImpl.isPlayerVehicle:
                BREvents.playSound(BREvents.TRAP_POINT_EXIT)
            self.__soundPlaying = False
        ctrl = self.__guiSessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.removeRuntimeView(self)
        return

    def setPlayerVehicleAlive(self, isAlive):
        if not isAlive and self.__soundPlaying:
            BREvents.playSound(BREvents.TRAP_POINT_EXIT)
            self.__soundPlaying = False

    def increment(self):
        self.__instances += 1

    def decrement(self):
        self.__instances -= 1
        return self.__instances


@dependency.replace_none_kwargs(dynObjCache=IBattleDynamicObjectsCache)
def onVehicleEnterTrap(equipment, who, where, dynObjCache=None):
    playerVehicleImpl = _getPlayerVehicleImpl(who)
    if playerVehicleImpl is None:
        return
    elif playerVehicleImpl.publicInfo.team == _getTrapTeam(where):
        return
    else:
        trapEffect = who.findComponentByType(TrapAffectComponent)
        if trapEffect is None:
            effectCfg = dynObjCache.getConfig(BigWorld.player().arenaGuiType).getTrapPointEffect().enemyVehicle
            if effectCfg is not None:
                who.createComponent(TrapAffectComponent, who, effectCfg, playerVehicleImpl.spaceID)
            else:
                _logger.warning("Couldn't find effect for the enemy vehicle!")
        else:
            trapEffect.increment()
        return


def onVehicleExitTrap(who, where):
    playerVehicleImpl = _getPlayerVehicleImpl(who)
    if playerVehicleImpl is None:
        return
    elif playerVehicleImpl.publicInfo.team == _getTrapTeam(where):
        return
    else:
        particle = who.findComponentByType(TrapAffectComponent)
        if particle is not None:
            instCount = particle.decrement()
            if instCount == 0:
                who.removeComponent(particle)
        return


def _getPlayerVehicleImpl(who):
    playerEntityRef = who.findComponentByType(NetworkComponents.NetworkEntity)
    if playerEntityRef is None:
        return
    else:
        playerEntityImpl = playerEntityRef.implementation
        return None if not isinstance(playerEntityImpl, Vehicle.Vehicle) else playerEntityImpl


def _getTrapImpl(where):
    trapEntityRef = where.findComponentByType(NetworkComponents.NetworkEntity)
    return None if trapEntityRef is None else trapEntityRef.implementation


def _getTrapTeam(where):
    trapImpl = _getTrapImpl(where)
    return trapImpl.data.get('team', -1) if trapImpl is not None and trapImpl.data is not None else -1
