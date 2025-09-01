# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChargeShotComponent.py
import typing
import weakref
import BigWorld
from constants import CHARGE_SHOT_FLAGS as FLAGS
from constants import VEHICLE_SETTING
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from gui.battle_control.controllers.consumables.blockers import IShellChangeBlocker, IShotBlocker
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicState, IMechanicStatesComponent
from vehicles.mechanics.mechanic_helpers import getVehicleMechanicParams
from vehicles.components.component_wrappers import ifPlayerVehicle
if typing.TYPE_CHECKING:
    from items.components.gun_installation_components import GunInstallationSlot

class ChargeShotState(IMechanicState):
    __slots__ = ('flags', 'level', 'baseTime', 'endTime', 'hasCharging', 'hasShotBlock', 'canStart', 'isGunDestroyed')

    def __init__(self, flags, level=0, baseTime=0.0, endTime=0.0):
        self.flags = flags
        self.level = level
        self.endTime = endTime
        self.baseTime = baseTime
        self.hasCharging = bool(flags & FLAGS.CHARGING)
        self.hasShotBlock = bool(flags & FLAGS.SHOT_BLOCK)
        self.canStart = not bool(flags & FLAGS.CANT_START_MASK)
        self.isGunDestroyed = bool(flags & FLAGS.GUN_DESTROYED)

    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    def progress(self, timeLeft):
        return max(0.0, 1.0 - timeLeft / self.baseTime if self.baseTime > 0 else 1.0)

    def isTransition(self, other):
        return self.level != other.level or self.flags != other.flags

    def __str__(self):
        timeLeft = self.timeLeft()
        return 'ChargeShotState(flags={}, level={}, baseTime={}, endTime={}, canStart={}, hasShotBlock={}, timeLeft={}, progress={})'.format(bin(self.flags), self.level, self.baseTime, self.endTime, self.canStart, self.hasShotBlock, timeLeft, self.progress(timeLeft))

    __repr__ = __str__


class ChargeShotComponent(VehicleMechanicPrefabDynamicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    __defaultState = ChargeShotState(FLAGS.RELOADING)

    def __init__(self):
        super(ChargeShotComponent, self).__init__()
        self.params = None
        self.__state = self.__defaultState
        self.__shotBlocker = _ChargeShotShotBlocker()
        self.__shellChangeBlocker = _ChargeShotShellChangeBlocker()
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__commandsEvents = createMechanicCommandsEvents()
        self._initComponent()
        return

    def onDestroy(self):
        self.__shotBlocker.destroy()
        self.__shellChangeBlocker.destroy()
        self.__statesEvents.destroy()
        self.__commandsEvents.destroy()
        if hasattr(self.entity, 'onDiscreteShotDone'):
            self.entity.onDiscreteShotDone -= self.__onDiscreteShotDone
        super(ChargeShotComponent, self).onDestroy()

    @property
    def statesEvents(self):
        return self.__statesEvents

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    def getMechanicState(self):
        return self.__state

    def set_publicState(self, oldState):
        if self.privateState is not None:
            return
        else:
            self.__updateAppearance()
            return

    def set_privateState(self, oldState):
        self.__updateAppearance()

    @ifPlayerVehicle
    def tryActivate(self, player):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        state = self.__state
        flags = state.flags | FLAGS.GUN_DIVING if player.isOwnBarrelUnderWater else state.flags & ~FLAGS.GUN_DIVING
        if flags & FLAGS.CANT_START_MASK:
            if state.flags != flags:
                state = ChargeShotState(flags, state.level, state.baseTime, state.endTime)
        else:
            self.cell.tryCharge()
            baseTime = self.params.timePerLevel[0]
            endTime = BigWorld.serverTime() + baseTime
            state = ChargeShotState(flags | FLAGS.CHARGING, 0, baseTime, endTime)
        self.__updateAppearance(state)

    def _onAppearanceReady(self):
        super(ChargeShotComponent, self)._onAppearanceReady()
        self.entity.onDiscreteShotDone += self.__onDiscreteShotDone
        self.__state = self.__getCurrentState()
        self.__statesEvents.processStatePrepared()

    def _collectComponentParams(self, typeDescriptor):
        super(ChargeShotComponent, self)._collectComponentParams(typeDescriptor)
        self.params = getVehicleMechanicParams(VehicleMechanic.CHARGE_SHOT, typeDescriptor)

    @ifPlayerVehicle
    def _onAvatarReady(self, _=None):
        self.__shotBlocker.init(self.__state.hasShotBlock)
        self.__shellChangeBlocker.init(self)

    def __getCurrentState(self):
        if self.privateState is not None:
            privState = self.privateState
            newState = ChargeShotState(privState.flags, privState.level, 0.0, privState.endTime)
            if newState.hasCharging:
                newState.baseTime = self.params.timePerLevel[newState.level]
            elif newState.hasShotBlock:
                newState.baseTime = self.params.shotBlockTime
        elif self.publicState is not None:
            pubState = self.publicState
            newState = ChargeShotState(pubState.flags, pubState.level)
        else:
            newState = self.__defaultState
        return newState

    def __updateAppearance(self, newState=None):
        if not self.isAppearanceReady():
            return
        else:
            if newState is None:
                newState = self.__getCurrentState()
            if not self.__state.isTransition(newState):
                return
            self.__state = newState
            self.__shotBlocker.setHasShotBlock(newState.hasShotBlock)
            self.__statesEvents.updateMechanicState(newState)
            return

    def __onDiscreteShotDone(self, gunInstallationSlot):
        if not gunInstallationSlot.isMainInstallation():
            return
        self.__updateAppearance(ChargeShotState(self.__state.flags & ~FLAGS.CHARGING | FLAGS.RELOADING))


class _ChargeShotShellChangeBlocker(IShellChangeBlocker):
    session = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__component',)

    def __init__(self):
        self.__component = None
        return

    def init(self, component):
        self.__component = weakref.proxy(component)
        self.session.shared.ammo.addShellChangeBlocker(self)

    def destroy(self):
        self.session.shared.ammo.discardShellChangeBlocker(self)

    def isBlocked(self, code):
        state = self.__component.getMechanicState()
        res = code == VEHICLE_SETTING.CURRENT_SHELLS and (state.hasCharging or state.hasShotBlock)
        return res


CAN_SHOOT = (True, None)
CANT_SHOOT = (False, CANT_SHOOT_ERROR.CHARGE_SHOT_BLOCKING)

class _ChargeShotShotBlocker(IShotBlocker):
    session = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__canShoot',)

    def __init__(self):
        self.__canShoot = CAN_SHOOT

    def init(self, hasShotBlock):
        self.setHasShotBlock(hasShotBlock)
        self.session.shared.ammo.addShotBlocker(self)

    def destroy(self):
        self.session.shared.ammo.discardShotBlocker(self)

    def setHasShotBlock(self, hasShotBlock):
        self.__canShoot = CANT_SHOOT if hasShotBlock else CAN_SHOOT

    def canShoot(self):
        return self.__canShoot
