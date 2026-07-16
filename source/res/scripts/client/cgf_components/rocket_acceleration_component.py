# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rocket_acceleration_component.py
from __future__ import absolute_import
import logging
import CGF
import BigWorld
from functools import partial
from cgf_script.registration import ComponentProperty, registerComponent
from GameplayDebug import DebugTextComponent
from constants import IS_CLIENT, HAS_DEV_RESOURCES
from constants import ROCKET_ACCELERATION_STATE
from GenericComponents import VSEComponent
if IS_CLIENT:
    from RocketAccelerationController import RocketAccelerationController
else:

    class RocketAccelerationController(object):
        pass


_logger = logging.getLogger(__name__)

class SoundEvents(object):
    ROCKET_ACCELERATION_READY = 'ev_rocket_accel_ready'
    ROCKET_ACCELERATION_ACTIVE_PC = 'ev_rocket_accel_start_PC'
    ROCKET_ACCELERATION_ACTIVE_NPC = 'ev_rocket_accel_start_NPC'
    ROCKET_ACCELERATION_STOP_PC = 'ev_rocket_accel_stop_PC'
    ROCKET_ACCELERATION_STOP_NPC = 'ev_rocket_accel_stop_NPC'
    ROCKET_ACCELERATION_DISABLE = 'ev_rocket_accel_disable'
    ROCKET_ACCELERATION_EMPTY = 'ev_rocket_accel_empty'


@registerComponent
class RocketAccelerationTerrainEffect(object):
    category = 'Rocket Accelerator'
    editorTitle = 'Rocket Accelerator Terrain Effect'
    domain = CGF.Domain.Client
    snow = ComponentProperty(type=CGF.PropertyType.Link, editorName='Snow', value=CGF.GameObject)
    sand = ComponentProperty(type=CGF.PropertyType.Link, editorName='Sand', value=CGF.GameObject)
    ground = ComponentProperty(type=CGF.PropertyType.Link, editorName='Ground', value=CGF.GameObject)
    stone = ComponentProperty(type=CGF.PropertyType.Link, editorName='Stone', value=CGF.GameObject)


@registerComponent
class RocketAccelerationStateListener(object):
    category = 'Rocket Accelerator'
    editorTitle = 'Rocket Accelerator State Listener'
    domain = CGF.Domain.Client
    vseComponent = ComponentProperty(type=CGF.PropertyType.Link, editorName='VS Plan', value=VSEComponent)
    start = ComponentProperty(type=CGF.PropertyType.Link, editorName='Start Object', value=CGF.GameObject)
    idle = ComponentProperty(type=CGF.PropertyType.Link, editorName='Idle Object', value=CGF.GameObject)
    end = ComponentProperty(type=CGF.PropertyType.Link, editorName='Stop Object', value=CGF.GameObject)
    sound_l = ComponentProperty(type=CGF.PropertyType.Link, editorName='Left Sound', value=CGF.GameObject)
    sound_r = ComponentProperty(type=CGF.PropertyType.Link, editorName='Right Sound', value=CGF.GameObject)
    startDuration = ComponentProperty(type=CGF.PropertyType.Float, editorName='Start Duration', value=0.2)
    endDuration = ComponentProperty(type=CGF.PropertyType.Float, editorName='End Duration', value=0.2)
    soundReady = ComponentProperty(type=CGF.PropertyType.String, editorName='Ready sound', value=SoundEvents.ROCKET_ACCELERATION_READY)
    soundActivePC = ComponentProperty(type=CGF.PropertyType.String, editorName='Active PC sound', value=SoundEvents.ROCKET_ACCELERATION_ACTIVE_PC)
    soundActiveNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Active NPC sound', value=SoundEvents.ROCKET_ACCELERATION_ACTIVE_NPC)
    soundStopPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop PC sound', value=SoundEvents.ROCKET_ACCELERATION_STOP_PC)
    soundStopNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop NPC sound', value=SoundEvents.ROCKET_ACCELERATION_STOP_NPC)
    soundDisable = ComponentProperty(type=CGF.PropertyType.String, editorName='Disable sound', value=SoundEvents.ROCKET_ACCELERATION_DISABLE)
    soundEmpty = ComponentProperty(type=CGF.PropertyType.String, editorName='Empty sound', value=SoundEvents.ROCKET_ACCELERATION_EMPTY)


class RocketAccelerationSystem(CGF.System):
    AccelerationActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(RocketAccelerationStateListener))
    AccelerationDeactivated = CGF.DeactivateReaction(CGF.ReactRw(RocketAccelerationStateListener))
    RocketAccelerationControllerAccess = CGF.AccessReaction(CGF.Rw(RocketAccelerationController))
    VSEComponentAccess = CGF.AccessReaction(VSEComponent)
    Reactions = CGF.Reactions(AccelerationActivated, AccelerationDeactivated, RocketAccelerationControllerAccess, VSEComponentAccess)

    def update(self):
        controllerAccess = self.reaction(self.RocketAccelerationControllerAccess)
        vsAccess = self.reaction(self.VSEComponentAccess)
        hierarchy = self.hierarchy
        for listener in self.reaction(self.AccelerationDeactivated):
            plan = vsAccess.find(listener.vseComponent)
            if plan:
                plan.stop()

        for go, listener in self.reaction(self.AccelerationActivated):
            root = hierarchy.getTopMostParent(go)
            provider = controllerAccess.find(root)
            if provider is None:
                _logger.error('Failed to find RocketAccelerationController')
                continue
            plan = vsAccess.find(listener.vseComponent)
            if plan:
                plan.start()
                continue
            _logger.error('RAM: Failed to setup visual script plan')

        return


if HAS_DEV_RESOURCES:

    class RocketAccelerationSystemDebug(CGF.System):
        ListenerActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(RocketAccelerationStateListener))
        ListenerDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(RocketAccelerationStateListener))
        RocketAccelerationControllerAccess = CGF.AccessReaction(CGF.Rw(RocketAccelerationController))
        DebugTextAccess = CGF.AccessReaction(CGF.Rw(DebugTextComponent))
        Reactions = CGF.Reactions(ListenerActivated, ListenerDeactivated, RocketAccelerationControllerAccess, DebugTextAccess)

        def __init__(self):
            super(RocketAccelerationSystemDebug, self).__init__()
            self.__texts = {}
            self.__listeners = {}

        def commonUpdate(self):
            hierarchy = self.hierarchy
            controllerAccess = self.reaction(self.RocketAccelerationControllerAccess)
            for go, _ in self.reaction(self.ListenerDeactivated):
                root = hierarchy.getTopMostParent(go)
                self.__texts.pop(go, None)
                callback = self.__listeners.pop(go, None)
                provider = controllerAccess.find(root)
                if provider is not None:
                    provider.unsubscribe(callback)

            queue = CGF.CommandQueue(self.spaceID)
            for go, _ in self.reaction(self.ListenerActivated):
                root = hierarchy.getTopMostParent(go)
                provider = controllerAccess.find(root)
                self.__setupDebugStateHandling(go, provider, queue)

            return

        def periodUpdate(self):
            for updater in self.__texts.values():
                updater()

        def onStateUpdate(self, root, status, _):
            self.__updateState(root, ROCKET_ACCELERATION_STATE.toString(status.status).upper(), status)

        def __updateState(self, root, value, status):
            textAccess = self.reaction(self.DebugTextAccess)
            text = textAccess.find(root)
            if status.timeLeft > 0.0:
                self.__updateTextWithDuration(text, value, status.reuseCount, status.endTime)
                self.__texts[root] = partial(self.__updateTextWithDuration, text, value, status.reuseCount, status.endTime)
            else:
                self.__updateText(text, value, status.reuseCount)
                self.__texts.pop(root, None)
            return

        def __updateText(self, text, value, count):
            if text is not None:
                text.setText('[RAM][{}][{}]'.format(value, count), (0, 0, 0), (1.0, 1.0, 1.0, 1.0))
            return

        def __updateTextWithDuration(self, text, value, count, end):
            duration = max(0, end - BigWorld.serverTime())
            if text is not None:
                text.setText('[RAM][{}][{}][{:.2f}]'.format(value, count, duration), (0, 0, 0), (1.0, 1.0, 1.0, 1.0))
            return

        def __setupDebugStateHandling(self, root, provider, queue):
            if not root.hasComponent(DebugTextComponent):
                queue.createComponent(root, DebugTextComponent, '', (0, 0, 0), (1.0, 1.0, 1.0, 1.0))
            self.__listeners[root] = partial(self.onStateUpdate, root)
            if provider is not None:
                provider.subscribe(self.__listeners[root])
            return
