# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_movers.py
import CGF
import GenericComponents
from Math import Matrix
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, tickGroup, onAddedQuery
from cgf_demo.demo_category import DEMO_CATEGORY

def createRotationMatrix(rotation):
    result = Matrix()
    result.setRotateYPR(rotation)
    return result


clamp = lambda minVal, maxVal, val: (minVal if val < minVal else maxVal if val > maxVal else val)

@registerComponent
class TestScriptAxisRotator(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainAll
    rotationSpeedYaw = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='rotation speed yaw', value=1.0)
    rotationSpeedPitch = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='rotation speed pitch', value=1.0)
    rotationSpeedRoll = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='rotation speed roll', value=1.0)
    transform = ComponentProperty(type=CGFMetaTypes.LINK, editorName='transform', value=GenericComponents.TransformComponent)

    def __init__(self):
        super(TestScriptAxisRotator, self).__init__()


@registerComponent
class TestScriptMover(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainAll
    finalPoint = ComponentProperty(type=CGFMetaTypes.LINK, editorName='finalPoint', value=GenericComponents.TransformComponent)
    period = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='period', value=1.0)
    transform = ComponentProperty(type=CGFMetaTypes.LINK, editorName='transform', value=GenericComponents.TransformComponent)

    def __init__(self):
        self.simTime = 0.0
        self.startTransform = Matrix()

    def prepare(self, transform):
        self.startMatrix = transform.transform
        self.simTime = 0.0


class TestAxisRotatorManager(CGF.ComponentManager):
    queryRotator = CGF.QueryConfig(GenericComponents.TransformComponent, TestScriptAxisRotator)
    queryMover = CGF.QueryConfig(GenericComponents.TransformComponent, TestScriptMover)

    @onAddedQuery(GenericComponents.TransformComponent, TestScriptMover)
    def setupMover(self, myTransform, mover):
        transform = mover.transform()
        if transform is None:
            transform = myTransform
        mover.prepare(transform)
        return

    @tickGroup('Simulation')
    def tick(self):
        delta = self.clock.gameDelta
        for transformComp, axisrotator in self.queryRotator:
            transform = transformComp.transform
            m = createRotationMatrix((clamp(-100, 100, axisrotator.rotationSpeedYaw * delta), clamp(-100, 100, axisrotator.rotationSpeedPitch * delta), clamp(-100, 100, axisrotator.rotationSpeedRoll * delta)))
            transform.preMultiply(m)
            transformComp.transform = transform

        for transformComp, mover in self.queryMover:
            self.__move(transformComp, mover, delta)

    def __move(self, myTransform, mover, delta):
        transform = mover.transform()
        if transform is None:
            transform = myTransform
        mover.simTime += delta
        if mover.simTime > mover.period:
            mover.simTime -= mover.period
        startPos = mover.startMatrix.applyToOrigin()
        shift = mover.finalPoint().position - startPos
        t = 2 * mover.simTime / mover.period
        if t > 1.0:
            t = 2 - t
        transform.position = startPos + shift * t
        return
