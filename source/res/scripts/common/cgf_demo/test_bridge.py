# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_bridge.py
from __future__ import absolute_import
import CGF
import Triggers
import math
import logging
from cgf_script.registration import ComponentProperty, registerComponent
from Math import Matrix
from cgf_demo.demo_category import DEMO_CATEGORY
_logger = logging.getLogger(__name__)

def createRTMatrix(rotation, translation):
    result = Matrix()
    result.setRotateYPR(rotation)
    result.translation = translation
    return result


@registerComponent
class TestBridge(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Bridge'
    domain = CGF.Domain.ClientEditor
    moverTransform1 = ComponentProperty(type=CGF.PropertyType.Link, editorName='Mover1', value=CGF.TransformComponent)
    moverTransform2 = ComponentProperty(type=CGF.PropertyType.Link, editorName='Mover2', value=CGF.TransformComponent)
    trigger1 = ComponentProperty(type=CGF.PropertyType.Link, editorName='Trigger1', value=Triggers.AreaTriggerComponent)
    trigger2 = ComponentProperty(type=CGF.PropertyType.Link, editorName='Trigger2', value=Triggers.AreaTriggerComponent)
    limit = ComponentProperty(type=CGF.PropertyType.Float, editorName='Limit', value=0.5)
    speed = ComponentProperty(type=CGF.PropertyType.Float, editorName='Speed', value=1)

    def tr1In(self, who, where):
        _logger.debug('Bridge Trigger 1 Entered')
        self.moveDirection1 = 1

    def tr1Out(self, who, where):
        self.moveDirection1 = -1

    def tr2In(self, who, where):
        _logger.debug('Bridge Trigger 2 Entered')
        self.moveDirection2 = 1

    def tr2Out(self, who, where):
        self.moveDirection2 = -1


class TestBridgeSystem(CGF.System):
    BridgeCreated = CGF.CreateReaction(CGF.ReactRw(TestBridge))
    BridgeActivated = CGF.ActivateReaction(CGF.ReactRw(TestBridge))
    BridgeIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(TestBridge))
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    AreaTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    Reactions = CGF.Reactions(BridgeCreated, BridgeActivated, BridgeIterate, TransformAccess, AreaTriggerAccess)

    def update(self):
        for bridge in self.reaction(self.BridgeCreated):
            self._createBridge(bridge)

        triggerAccess = self.reaction(self.AreaTriggerAccess)
        for bridge in self.reaction(self.BridgeActivated):
            self._activateBridge(bridge, triggerAccess)

        transformAccess = self.reaction(self.TransformAccess)
        for bridge in self.reaction(self.BridgeIterate):
            self.__simulate(bridge, self.clock.updateDelta, transformAccess)

    def _createBridge(self, bridge):
        _logger.debug('Bridge Created')
        bridge.moveDirection1 = 0
        bridge.moveDirection2 = 0

    def _activateBridge(self, bridge, triggerAccess):
        _logger.debug('Bridge Activated')
        if bridge.trigger1 is not None:
            trigger = triggerAccess.find(bridge.trigger1)
            trigger.addEnterReaction(bridge.tr1In)
            trigger.addExitReaction(bridge.tr1Out)
        if bridge.trigger2 is not None:
            trigger = triggerAccess.find(bridge.trigger2)
            trigger.addEnterReaction(bridge.tr2In)
            trigger.addExitReaction(bridge.tr2Out)
        return

    def __simulate(self, bridge, dt, transformAccess):
        speed = bridge.speed * dt
        foundTransform1 = transformAccess.find(bridge.moverTransform1)
        if foundTransform1 is not None:
            transform1 = foundTransform1
            if transform1 is not None and bridge.moveDirection1 != 0:
                rotation = transform1.rotationYPR
                pitch = rotation[1] - bridge.moveDirection1 * speed
                if math.fabs(pitch) >= bridge.limit:
                    pitch = -bridge.limit
                if pitch >= 0.0:
                    bridge.moveDirection1 = 0
                    pitch = 0.0
                rotation[1] = pitch
                transform1.rotationYPR = rotation
        foundTransform2 = transformAccess.find(bridge.moverTransform2)
        if foundTransform2 is not None:
            transform2 = foundTransform2
            if bridge.moverTransform2 is not None and bridge.moveDirection2 != 0:
                rotation = transform2.rotationYPR
                pitch = rotation[1] + bridge.moveDirection2 * speed
                if math.fabs(pitch) >= bridge.limit:
                    pitch = bridge.limit
                if pitch <= 0.0:
                    bridge.moveDirection2 = 0
                    pitch = 0.0
                rotation[1] = pitch
                transform2.rotationYPR = rotation
        return
