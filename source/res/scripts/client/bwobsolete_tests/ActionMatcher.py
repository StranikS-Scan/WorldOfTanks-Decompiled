# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_tests/ActionMatcher.py
import BigWorld
import Math
import GUI
import math
from functools import partial
preload = BigWorld.Model('helpers/models/hemisphere.model')
preload2 = BigWorld.Model('helpers/models/entity_arrow.model')
preload3 = BigWorld.Model('helpers/models/directional_arrow.model')

class MatchInfo:

    def __init__(self, tuple):
        self.trigger_minEntitySpeed, self.trigger_maxEntitySpeed, self.trigger_minEntityAux1, self.trigger_maxEntityAux1, self.trigger_minModelYaw, self.trigger_maxModelYaw, self.cancel_minEntitySpeed, self.cancel_maxEntitySpeed, self.cancel_minEntityAux1, self.cancel_maxEntityAux1, self.cancel_minModelYaw, self.cancel_maxModelYaw = tuple


class ActionDisplay:

    def __init__(self):
        self.dummy = BigWorld.Model('')
        self.turnTrigger = self.angleGizmo(red=False)
        self.turnCancel = self.angleGizmo(red=True)
        self.strafeTrigger = self.angleGizmo2(red=False)
        self.speedTrigger = self.rulerGizmo(red=False)
        self.speedCancel = self.rulerGizmo(red=True)
        self.guiAttachment = GUI.Attachment()
        self.actionText = GUI.Text('')
        self.guiAttachment.component = self.actionText

    def angleGizmo(self, red=False):
        m = BigWorld.Model('helpers/models/hemisphere.model')
        m.gen_shadow = ['green', 'red'][red]
        return m

    def angleGizmo2(self, red=False):
        m = BigWorld.Model('helpers/models/hemisphere.model')
        m.gen_shadow = ['green_hollow', 'red_hollow'][red]
        return m

    def rulerGizmo(self, red=False):
        f = GUI.Frame2('helpers/maps/ruler.tga')
        f.transform = GUI.MatrixShader()
        f.transform.target = Math.Matrix()
        f.transform.target.setRotateX(1.57)
        f.verticalAnchor = GUI.Simple.eVAnchor.BOTTOM
        f.filterType = GUI.Simple.eFilterType.LINEAR
        f.colour = [(92, 255, 92, 255), (255, 92, 92, 255)][red]
        f.size = (1.0, 5.0)
        tr = Math.Matrix()
        tr.setTranslate((0, 0, -1))
        f.transform.target.preMultiply(tr)
        att = GUI.Attachment()
        att.component = f
        return att

    def uvRotationMatrix(self, deg):
        m = Math.Matrix()
        pre = Math.Matrix()
        pre.setTranslate((-0.5, -0.5, 0))
        post = Math.Matrix()
        post.setTranslate((0.5, 0.5, 0))
        m.setRotateZ(math.radians(deg))
        m.preMultiply(pre)
        m.postMultiply(post)
        return m

    def setAngle(self, g, deg):
        deg = 90 - deg / 2.0
        m = uvRotationMatrix(deg)
        n = uvRotationMatrix(-deg)
        g.gen_shadow.uTransform_diffuse = (m.get(0, 0),
         m.get(1, 0),
         0,
         m.get(3, 0))
        g.gen_shadow.vTransform_diffuse = (m.get(0, 1),
         m.get(1, 1),
         0,
         m.get(3, 1))
        g.gen_shadow.uTransform = (n.get(0, 0),
         n.get(1, 0),
         0,
         n.get(3, 0))
        g.gen_shadow.vTransform = (n.get(0, 1),
         n.get(1, 1),
         0,
         n.get(3, 1))

    def setAngles(self, g, min, max):
        if max - min > 180:
            max = min + 180
        shaveOffLeft = min - -90
        m = self.uvRotationMatrix(-shaveOffLeft)
        shaveOffRight = 90 - max
        n = self.uvRotationMatrix(shaveOffRight)
        g.gen_shadow.uTransform_diffuse = (m.get(0, 0),
         m.get(1, 0),
         0,
         m.get(3, 0))
        g.gen_shadow.vTransform_diffuse = (m.get(0, 1),
         m.get(1, 1),
         0,
         m.get(3, 1))
        g.gen_shadow.uTransform = (n.get(0, 0),
         n.get(1, 0),
         0,
         n.get(3, 0))
        g.gen_shadow.vTransform = (n.get(0, 1),
         n.get(1, 1),
         0,
         n.get(3, 1))

    def showActionInfo(self, entity, actionName):
        entity.model.root.attach(self.dummy)
        self.addMatchedActionLabel()
        try:
            mi = MatchInfo(entity.model.motors[0].matchInfo(actionName))
            self.actionText.text = actionName
        except TypeError:
            self.actionText.text = 'Unmatched'
            return

        if mi.trigger_minEntityAux1 > -math.pi or mi.trigger_maxEntityAux1 < math.pi:
            self.setAngles(self.turnTrigger, math.degrees(mi.trigger_minEntityAux1), math.degrees(mi.trigger_maxEntityAux1))
            self.dummy.root.attach(self.turnTrigger)
        if mi.cancel_minEntityAux1 > -math.pi or mi.cancel_maxEntityAux1 < math.pi:
            self.setAngles(self.turnCancel, math.degrees(mi.cancel_minEntityAux1), math.degrees(mi.cancel_maxEntityAux1))
            self.dummy.root.attach(self.turnCancel)
        if mi.trigger_minModelYaw > -math.pi or mi.trigger_maxModelYaw < math.pi:
            self.setAngles(self.strafeTrigger, math.degrees(mi.trigger_minModelYaw), math.degrees(mi.trigger_maxModelYaw))
            self.dummy.root.attach(self.strafeTrigger)
        if mi.cancel_minModelYaw > -math.pi or mi.cancel_maxModelYaw < math.pi:
            self.setAngles(self.strafeCancel, math.degrees(mi.cancel_minModelYaw), math.degrees(mi.cancel_maxModelYaw))
            self.dummy.root.attach(self.strafeCancel)
        if mi.trigger_minEntitySpeed > -1000.0 or mi.trigger_maxEntitySpeed < 1000.0:
            self.speedTrigger.component.height = mi.trigger_maxEntitySpeed - mi.trigger_minEntitySpeed
            self.speedTrigger.component.position = (0, mi.trigger_minEntitySpeed, 0.0)
            self.speedTrigger.component.transform.target.setIdentity()
            tran = Math.Matrix()
            tran.setTranslate((0, 0, -1))
            rot = Math.Matrix()
            rot.setRotateZ((mi.trigger_maxModelYaw + mi.trigger_minModelYaw) / 2.0)
            vert = Math.Matrix()
            vert.setRotateX(1.57)
            self.speedTrigger.component.transform.target.setIdentity()
            self.speedTrigger.component.transform.target.postMultiply(rot)
            self.speedTrigger.component.transform.target.postMultiply(tran)
            self.speedTrigger.component.transform.target.postMultiply(vert)
            self.dummy.root.attach(self.speedTrigger)
        if mi.cancel_minEntitySpeed > -1000 or mi.cancel_maxEntitySpeed < 1000.0:
            self.dummy.root.attach(self.speedCancel)
            self.speedCancel.component.height = mi.cancel_maxEntitySpeed - mi.cancel_minEntitySpeed
            self.speedCancel.component.position = (0, mi.cancel_minEntitySpeed, 0.0)

    def addMatchedActionLabel(self):
        self.actionText.position = (-0.1, 0.0, 0.0)
        self.actionText.transform = GUI.MatrixShader()
        self.actionText.filterType = GUI.Simple.eFilterType.LINEAR
        self.actionText.font = 'Heading.font'
        self.actionText.horizontalAnchor = GUI.Simple.eHAnchor.RIGHT
        rot = Math.Matrix()
        rot.setRotateX(1.57)
        sc = Math.Matrix()
        sc.setScale((5, 5, 5))
        rot.postMultiply(sc)
        self.actionText.transform.target = rot
        self.dummy.root.attach(self.guiAttachment)

    def floatAway(self, entity):
        entity.model.root.detach(self.dummy)
        initial = Math.Matrix(entity.model.root)
        final = Math.Matrix()
        final.setTranslate((0, -5, 0))
        final.preMultiply(initial)
        ma = Math.MatrixAnimation()
        ma.keyframes = [(0.0, initial), (5.0, final)]
        ma.loop = False
        ma.time = 0.0
        motor = BigWorld.Servo(ma)
        self.dummy.addMotor(motor)
        BigWorld.addModel(self.dummy)
        BigWorld.callback(5.0, partial(BigWorld.delModel, self.dummy))


def vizModel():
    m = BigWorld.Model('helpers/models/entity_arrow.model')
    return m


def transformVizModel():
    m = BigWorld.Model('helpers/models/basic_entity_arrow.model')
    return m


def velocityVizModel():
    m = BigWorld.Model('helpers/models/directional_arrow.model')
    return m


def addEntityTransformViz(entity, scale=0.25):
    m = transformVizModel()
    m.empty = 'Custom'
    m.empty.clothesColour4 = (1, 1, 0.5, 0)
    mp = Math.MatrixProduct()
    translate = Math.Matrix()
    translate.setTranslate((0, 0.35, 0))
    t = entity.matrix
    t.notModel = True
    mp.a = t
    mp.b = translate
    mp2 = Math.MatrixProduct()
    mp2.a = Math.Matrix()
    mp2.a.setScale((scale, scale, scale))
    mp2.b = mp
    s = BigWorld.Servo(mp2)
    m.motors = [s]
    entity.addModel(m)


def addModelTransformViz(entity, scale=0.25):
    m = transformVizModel()
    m.empty = 'Custom'
    m.empty.clothesColour4 = (1.0, 0.33, 0.33, 1.0)
    t = entity.matrix
    t.notModel = False
    mp = Math.MatrixProduct()
    mp.a = Math.Matrix()
    mp.a.setScale((scale, scale, scale))
    mp.b = t
    s = BigWorld.Servo(mp)
    m.motors = [s]
    entity.addModel(m)


def addWorldVelocityViz(entity):
    m = velocityVizModel()
    m.empty = 'Custom'
    m.empty.clothesColour4 = (0.33, 1.0, 0.33, 1.0)
    t = entity.model.motors[0].debugWorldVelocity
    ma = Math.Vector4MatrixAdaptor()
    ma.source = t
    ma.style = 'LOOKAT_SCALEZ'
    ma.position = Math.Vector4Translation(entity.matrix)
    s = BigWorld.Servo(ma)
    m.motors = [s]
    entity.addModel(m)


def setPlayerEntityModel():
    m = vizModel()
    BigWorld.player().model = m


def dumpActionInfo(entity):
    actions = entity.model.motors[0].actions
    for a in actions:
        mi = MatchInfo(entity.model.motors[0].matchInfo(a))
        print '----------------------------------------------------'
        print a
        print '----------------------------------------------------'
        print 'trigger_minEntitySpeed', mi.trigger_minEntitySpeed
        print 'trigger_maxEntitySpeed', mi.trigger_maxEntitySpeed
        print 'trigger_minEntityAux1', mi.trigger_minEntityAux1
        print 'trigger_maxEntityAux1', mi.trigger_maxEntityAux1
        print 'trigger_minModelYaw', mi.trigger_minModelYaw
        print 'trigger_maxModelYaw', mi.trigger_maxModelYaw
        print 'cancel_minEntitySpeed', mi.cancel_minEntitySpeed
        print 'cancel_maxEntitySpeed', mi.cancel_maxEntitySpeed
        print 'cancel_minEntityAux1', mi.cancel_minEntityAux1
        print 'cancel_maxEntityAux1', mi.cancel_maxEntityAux1
        print 'cancel_minModelYaw', mi.cancel_minModelYaw
        print 'cancel_maxModelYaw', mi.cancel_maxModelYaw


g_lastActionDisplay = None

def onMatchAction(entity, actionName):
    global g_lastActionDisplay
    if g_lastActionDisplay != None:
        try:
            g_lastActionDisplay.floatAway(entity)
        except:
            pass

        g_lastActionDisplay = None
    if entity is not None:
        g_lastActionDisplay = ActionDisplay()
        g_lastActionDisplay.showActionInfo(entity, actionName)
    return


def test(entity=None):
    if entity == None:
        entity = BigWorld.player()
    entity.model.motors[0].matchNotifier = partial(onMatchAction, entity)
    addEntityTransformViz(entity)
    addModelTransformViz(entity)
    addWorldVelocityViz(entity)
    return


def testSSO(entity=None):
    if entity == None:
        entity = BigWorld.player()
    m = BigWorld.Model('art/characters/foe/guard/guard.model')
    BigWorld.player().model = m
    BigWorld.player().model.motors[0].matchNotifier = partial(onMatchAction, entity)
    addEntityTransformViz(BigWorld.player())
    addModelTransformViz()
    addWorldVelocityViz()
    addMatchedActionLabel()
    return
