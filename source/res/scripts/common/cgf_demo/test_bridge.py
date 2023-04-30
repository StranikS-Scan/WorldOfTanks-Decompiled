# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_bridge.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onProcessQuery, onAddedQuery
import GenericComponents
import Triggers
import math
from Math import Matrix
from cgf_demo.demo_category import DEMO_CATEGORY
import logging
_logger = logging.getLogger(__name__)

def createRTMatrix(rotation, translation):
    result = Matrix()
    result.setRotateYPR(rotation)
    result.translation = translation
    return result


@registerComponent
class TestBridge(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    moverTransform1 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Mover1', value=GenericComponents.TransformComponent)
    moverTransform2 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Mover2', value=GenericComponents.TransformComponent)
    trigger1 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Trigger1', value=Triggers.AreaTriggerComponent)
    trigger2 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Trigger2', value=Triggers.AreaTriggerComponent)
    limit = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Limit', value=0.5)
    speed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Speed', value=1)

    def __init__(self):
        super(TestBridge, self).__init__()
        _logger.debug('Bridge Created')
        self.moveDirection1 = 0
        self.moveDirection2 = 0

    def activate(self):
        _logger.debug('Bridge Activated')

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


class TestBridgeManager(CGF.ComponentManager):

    @onAddedQuery(TestBridge)
    def onAddedQuery(self, brige):
        if brige.trigger1 is not None:
            trigger = brige.trigger1()
            trigger.addEnterReaction(brige.tr1In)
            trigger.addExitReaction(brige.tr1Out)
        if brige.trigger2 is not None:
            trigger = brige.trigger2()
            trigger.addEnterReaction(brige.tr2In)
            trigger.addExitReaction(brige.tr2Out)
        return

    @onProcessQuery(TestBridge, tickGroup='Simulation')
    def processQuery(self, bridge):
        self.__simulate(bridge, self.clock.gameDelta)

    def __simulate(self, bridge, dt):
        speed = bridge.speed * dt
        if bridge.moverTransform1() is not None:
            transform1 = bridge.moverTransform1()
            if transform1 is not None and bridge.moveDirection1 != 0:
                rotation = transform1.rotation
                pitch = rotation[1] - bridge.moveDirection1 * speed
                if math.fabs(pitch) >= bridge.limit:
                    pitch = -bridge.limit
                if pitch >= 0.0:
                    bridge.moveDirection1 = 0
                    pitch = 0.0
                rotation[1] = pitch
                transform1.rotation = rotation
        if bridge.moverTransform2() is not None:
            transform2 = bridge.moverTransform2()
            if bridge.moverTransform2 is not None and bridge.moveDirection2 != 0:
                rotation = transform2.rotation
                pitch = rotation[1] + bridge.moveDirection2 * speed
                if math.fabs(pitch) >= bridge.limit:
                    pitch = bridge.limit
                if pitch <= 0.0:
                    bridge.moveDirection2 = 0
                    pitch = 0.0
                rotation[1] = pitch
                transform2.rotation = rotation
        return
