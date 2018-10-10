# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_tests/GUITest.py
import math
import BigWorld, GUI, Math
import Keys
import random
from functools import partial
BigWorld.camera(BigWorld.CursorCamera())
BigWorld.setCursor(GUI.mcursor())
GUI.mcursor().visible = True

def clear():
    for x in GUI.roots():
        GUI.delRoot(x)

    GUI.mcursor().visible = True
    GUI.mcursor().clipped = False
    BigWorld.setCursor(GUI.mcursor())


def _setAllModeCombinations(c, name):
    setattr(c, name, 'PIXEL')
    setattr(c, name, 'LEGACY')
    setattr(c, name, 'PIXEL')
    setattr(c, name, 'CLIP')
    setattr(c, name, 'PIXEL')
    setattr(c, name, 'CLIP')
    setattr(c, name, 'LEGACY')
    setattr(c, name, 'CLIP')


def mode_conv():

    def add_conv_test_child(p, hAnchor, vAnchor, pos):
        c = GUI.Simple('system/maps/col_white.bmp')
        c.colour = (255, 0, 0, 255)
        c.width = 0.1
        c.height = 0.1
        c.materialFX = 'SOLID'
        c.horizontalPositionMode = 'CLIP'
        c.verticalPositionMode = 'CLIP'
        c.position.x = pos[0]
        c.position.y = pos[1]
        c.horizontalAnchor = hAnchor
        c.verticalAnchor = vAnchor
        p.addChild(c)
        _setAllModeCombinations(c, 'horizontalPositionMode')
        _setAllModeCombinations(c, 'verticalPositionMode')
        _setAllModeCombinations(c, 'widthMode')
        _setAllModeCombinations(c, 'heightMode')

    clear()
    w = GUI.Window('system/maps/col_white.bmp')
    w.position = (0, 0.25, 1)
    _setAllModeCombinations(w, 'horizontalPositionMode')
    _setAllModeCombinations(w, 'verticalPositionMode')
    _setAllModeCombinations(w, 'widthMode')
    _setAllModeCombinations(w, 'heightMode')
    add_conv_test_child(w, 'LEFT', 'TOP', (-1, 1))
    add_conv_test_child(w, 'RIGHT', 'TOP', (1, 1))
    add_conv_test_child(w, 'LEFT', 'BOTTOM', (-1, -1))
    add_conv_test_child(w, 'RIGHT', 'BOTTOM', (1, -1))
    add_conv_test_child(w, 'CENTER', 'CENTER', (0, 0))
    GUI.addRoot(w)


class _Child(object):

    def __init__(self, component):
        self.component = component
        self.component.script = self

    def handleMouseEnterEvent(self, comp):
        self.component.parent.hoverLabel.text = '< !! >'
        return False

    def handleMouseLeaveEvent(self, comp):
        self.component.parent.hoverLabel.text = ''
        return False

    @staticmethod
    def create(hAnchor, vAnchor, pos):
        c = GUI.Simple('system/maps/col_white.bmp')
        c.colour = (0, 0, 255, 255)
        c.horizontalPositionMode = 'CLIP'
        c.verticalPositionMode = 'CLIP'
        c.widthMode = 'CLIP'
        c.heightMode = 'CLIP'
        c.horizontalAnchor = hAnchor
        c.verticalAnchor = vAnchor
        c.materialFX = 'SOLID'
        c.width = 0.5
        c.height = 0.5
        c.crossFocus = True
        c.moveFocus = True
        c.focus = True
        c.position.x = pos[0]
        c.position.y = pos[1]
        return _Child(c)


class _ParentAnchorWindow(object):

    def __init__(self, component):
        self.component = component
        self.component.script = self

    def handleMouseEnterEvent(self, comp):
        self.component.hoverLabel.text = '!!'
        return False

    def handleMouseLeaveEvent(self, comp):
        self.component.hoverLabel.text = ''
        return False

    @staticmethod
    def create(hAnchor, vAnchor, pos, colour):
        c = GUI.Window('system/maps/col_white.bmp')
        c.widthMode = 'PIXEL'
        c.heightMode = 'PIXEL'
        c.width = 200
        c.height = 200
        c.widthMode = 'CLIP'
        c.heightMode = 'CLIP'
        c.colour = colour
        c.horizontalAnchor = hAnchor
        c.verticalAnchor = vAnchor
        c.position.x = pos[0]
        c.position.y = pos[1]
        c.materialFX = 'BLEND'
        c.crossFocus = True
        c.moveFocus = True
        c.focus = True
        c.addChild(_Child.create('LEFT', 'TOP', (-1, 1)).component)
        c.addChild(_Child.create('CENTER', 'TOP', (0, 1)).component)
        c.addChild(_Child.create('RIGHT', 'TOP', (1, 1)).component)
        c.addChild(_Child.create('LEFT', 'CENTER', (-1, 0)).component)
        c.addChild(_Child.create('CENTER', 'CENTER', (0, 0)).component)
        c.addChild(_Child.create('RIGHT', 'CENTER', (1, 0)).component)
        c.addChild(_Child.create('LEFT', 'BOTTOM', (-1, -1)).component)
        c.addChild(_Child.create('CENTER', 'BOTTOM', (0, -1)).component)
        c.addChild(_Child.create('RIGHT', 'BOTTOM', (1, -1)).component)
        label = GUI.Text('%s, %s' % (hAnchor, vAnchor))
        label.font = 'default_smaller.font'
        label.verticalAnchor = 'BOTTOM'
        label.horizontalPositionMode = 'CLIP'
        label.verticalPositionMode = 'CLIP'
        label.position.y = -0.8
        label.colour = (100, 100, 100, 255)
        c.addChild(label, 'label')
        hoverLabel = GUI.Text('')
        hoverLabel.colour = (255, 128, 64, 255)
        c.addChild(hoverLabel, 'hoverLabel')
        return _ParentAnchorWindow(c)


def anchors():
    clear()
    GUI.addRoot(_ParentAnchorWindow.create('LEFT', 'TOP', (-1, 1), (0, 0, 0, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('CENTER', 'TOP', (0, 1), (0, 0, 128, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('RIGHT', 'TOP', (1, 1), (0, 255, 0, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('LEFT', 'CENTER', (-1, 0), (0, 255, 255, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('CENTER', 'CENTER', (0, 0), (255, 0, 0, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('RIGHT', 'CENTER', (1, 0), (255, 0, 255, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('LEFT', 'BOTTOM', (-1, -1), (255, 255, 0, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('CENTER', 'BOTTOM', (0, -1), (255, 255, 255, 255)).component)
    GUI.addRoot(_ParentAnchorWindow.create('RIGHT', 'BOTTOM', (1, -1), (128, 128, 128, 255)).component)


class _FocusableComponent:

    def __init__(self):
        self.component = GUI.Simple('system/maps/col_white.bmp')
        self.component.script = self
        self.component.materialFX = 'BLEND'
        self.component.focus = False
        self.component.mouseButtonFocus = True

    def handleKeyEvent(self, event):
        print 'handleKeyEvent', BigWorld.keyToString(event.key), event.isKeyDown()
        if event.key == Keys.KEY_SPACE:
            self.component.colour = (random.random() * 255,
             random.random() * 255,
             random.random() * 255,
             255)
            return True
        return False

    def handleMouseButtonEvent(self, comp, event):
        print 'handleMouseButtonEvent', BigWorld.keyToString(event.key), event.isKeyDown(),
        if self.component.focus == False:
            print 'Setting focus to True!'
            self.component.focus = True
            self.component.colour = (128, 128, 12, 255)
        else:
            print "We're already in focus."
        return True


def mouseButtonFocus():
    clear()
    GUI.addRoot(_FocusableComponent().component)


class _GameSquare:

    def __init__(self, component):
        self.component = component
        self.component.script = self
        self.velocity = Math.Vector2(random.random() * 2 - 1, random.random() * 2 - 1)
        self.velocity.normalise()
        self.velocity *= 0.25
        self.lastUpdateTime = BigWorld.time()
        self.gameStarted = False
        BigWorld.callback(0.01, self.update)
        BigWorld.callback(3, self.startGame)

    def startGame(self):
        self.gameStarted = True
        self.lastUpdateTime = BigWorld.time()
        self.gameStartTime = BigWorld.time()
        BigWorld.callback(0.01, self.update)
        BigWorld.callback(7, self.speedUp)

    def update(self):
        dt = float(BigWorld.time() - self.lastUpdateTime)
        self.lastUpdateTime = BigWorld.time()
        self.component.position.x += float(self.velocity.x) * float(dt)
        self.component.position.y += float(self.velocity.y) * float(dt)
        if self.component.position.x < -1:
            self.velocity.x = -self.velocity.x
            self.component.position.x = -1
        elif self.component.position.x > 1 - self.component.width:
            self.velocity.x = -self.velocity.x
            self.component.position.x = 1.0 - self.component.width
        elif self.component.position.y < -1 + self.component.height:
            self.velocity.y = -self.velocity.y
            self.component.position.y = -1 + self.component.height
        elif self.component.position.y > 1:
            self.velocity.y = -self.velocity.y
            self.component.position.y = 1.0
        if self.gameStarted:
            BigWorld.callback(0.001, self.update)

    def speedUp(self):
        BigWorld.callback(5, self.speedUp)
        self.velocity = self.velocity.scale(1.4)

    def handleMouseEnterEvent(self, comp):
        if self.gameStarted:
            t = GUI.Text('YOU LOSE! Time: %.2f sec.' % (BigWorld.time() - self.gameStartTime))
            t.colour = (255, 0, 0, 255)
            t.position.z = 0.5
            GUI.addRoot(t)
            GUI.reSort()
            BigWorld.callback(5, clear)
            for root in GUI.roots():
                if isinstance(root.script, _GameSquare):
                    root.script.gameStarted = False

        return False

    def handleMouseLeaveEvent(self, comp):
        return False

    @staticmethod
    def create():
        c = GUI.Simple('system/maps/col_white.bmp')
        c.horizontalPositionMode = 'LEGACY'
        c.verticalPositionMode = 'LEGACY'
        c.horizontalAnchor = 'LEFT'
        c.verticalAnchor = 'TOP'
        c.materialFX = 'SOLID'
        c.widthMode = 'CLIP'
        c.heightMode = 'CLIP'
        c.width = random.random()
        c.height = random.random()
        c.focus = True
        c.moveFocus = True
        c.crossFocus = True
        c.colour = (int(random.random() * 127),
         int(random.random() * 127),
         int(random.random() * 127),
         255)
        c.position = (random.random() * 2 - 1, random.random() * 2 - 1, 1)
        return _GameSquare(c)


def _removeComponent(component):
    GUI.delRoot(component)


def _gameStarted(label):
    label.text = 'GO!'
    BigWorld.callback(1, partial(_removeComponent, label))


def game():
    clear()
    for i in range(10):
        GUI.addRoot(_GameSquare.create().component)

    t = GUI.Text('Get ready...')
    t.colour = (255, 0, 0, 255)
    t.position.z = 0.5
    GUI.mcursor().clipped = True
    GUI.addRoot(t)
    BigWorld.callback(3, partial(_gameStarted, t))
    GUI.reSort()


class _OrderStackingBlock:

    def __init__(self, component, colour):
        self.component = component
        self.component.script = self
        self.name = colour

    def handleMouseClickEvent(self, comp):
        self.component.hoverLabel.text = self.name
        BigWorld.callback(2, self.clearClick)
        return True

    def clearClick(self):
        self.component.hoverLabel.text = ''

    @staticmethod
    def create(position, colour):
        c = GUI.Simple('helpers/maps/col_%s.bmp' % colour)
        c.materialFX = 'SOLID'
        c.size = (0.5, 0.5)
        c.position = position
        c.focus = True
        hoverLabel = GUI.Text('')
        hoverLabel.colour = (255, 255, 255, 255)
        hoverLabel.position = position
        hoverLabel.position.x *= 2
        hoverLabel.position.y *= 2
        hoverLabel.position.z = 0.0
        c.addChild(hoverLabel, 'hoverLabel')
        return _OrderStackingBlock(c, colour)


class _OrderChangingButton:

    def __init__(self, component, backComponent, resortFn):
        self.component = component
        self.component.script = self
        self.target = backComponent
        self.resortFn = resortFn
        self.component.mouseButtonFocus = True

    def handleMouseClickEvent(self, comp):
        self.target.position.z = 0.2
        self.resortFn()
        return True

    @staticmethod
    def create(backComponent, resortFn):
        c = GUI.Text('Click here to move black box forward')
        c.position = (0.0, -0.8, 0.0)
        c.focus = True
        return _OrderChangingButton(c, backComponent, resortFn)


def localReSort():
    clear()
    ourRoot = _OrderStackingBlock.create((0.0, 0.0, 0.0), 'white').component
    GUI.addRoot(ourRoot)
    red = _OrderStackingBlock.create((0.0, -0.2, 0.5), 'red').component
    ourRoot.addChild(red)
    yellow = _OrderStackingBlock.create((0.2, 0.0, 0.6), 'yellow').component
    ourRoot.addChild(yellow)
    black = _OrderStackingBlock.create((-0.2, 0.0, 0.7), 'black').component
    ourRoot.addChild(black)
    GUI.addRoot(_OrderChangingButton.create(black, ourRoot.reSort).component)


def globalReSort():
    clear()
    ourRoot = _OrderStackingBlock.create((0.0, 0.0, 0.0), 'white').component
    GUI.addRoot(ourRoot)
    red = _OrderStackingBlock.create((0.0, -0.2, 0.5), 'red').component
    ourRoot.addChild(red)
    yellow = _OrderStackingBlock.create((0.2, 0.0, 0.6), 'yellow').component
    ourRoot.addChild(yellow)
    black = _OrderStackingBlock.create((-0.2, 0.0, 0.7), 'black').component
    ourRoot.addChild(black)
    GUI.addRoot(_OrderChangingButton.create(black, GUI.reSort).component)


class _MouseEventTester1:

    def __init__(self, parent, component):
        self.component = component
        component.focus = True
        component.mouseButtonFocus = True
        component.crossFocus = True
        component.moveFocus = True
        component.dragFocus = True
        component.dropFocus = True
        self.parent = parent
        self.label1 = GUI.Text('')
        self.label1.colour = (255, 0, 0, 255)
        self.label1.verticalPositionMode = 'CLIP'
        component.addChild(self.label1)
        self.label2 = GUI.Text('')
        self.label2.colour = (0, 0, 255, 255)
        self.label2.verticalPositionMode = 'CLIP'
        self.label2.position.y = -0.5
        component.addChild(self.label2)
        self.label3 = GUI.Text('')
        self.label3.colour = (0, 255, 0, 255)
        self.label3.verticalPositionMode = 'CLIP'
        self.label3.position.y = 0.5
        component.addChild(self.label3)
        self.startPosition = Math.Vector3(self.component.position)
        BigWorld.callback(0.01, self._animatePosition)
        self.hideCBHandle = None
        return

    def handleMouseEnterEvent(self, component):
        self.label1.text = 'handleMouseEnter'
        return True

    def handleMouseLeaveEvent(self, component):
        self.label1.text = 'handleMouseLeave'
        return True

    def handleMouseClickEvent(self, component):
        self.label1.text = 'handleMouseClickEvent'
        return True

    def handleMouseButtonEvent(self, component, event):
        self.label1.text = 'handleMouseButtonEvent'
        return True

    def handleDragStartEvent(self, component):
        self.label3.text = 'handleDragStartEvent'
        return True

    def handleDragStopEvent(self, component):
        self.label3.text = 'handleDragStopEvent'
        return True

    def handleDragEnterEvent(self, component, dragged):
        self.label3.text = 'handleDragEnterEvent'
        return True

    def handleDragLeaveEvent(self, component, dragged):
        self.label3.text = 'handleDragLeaveEvent'
        return True

    def handleDropEvent(self, component, dragged):
        self.label3.text = 'handleDropEvent'
        return True

    def handleMouseEvent(self, comp, event):
        self.label2.visible = True
        self.label2.text = 'handleMouseEvent (%s %s %s)' % (event.dx, event.dy, event.dz)
        if self.hideCBHandle is not None:
            BigWorld.cancelCallback(self.hideCBHandle)
        self.hideCBHandle = BigWorld.callback(2.0, self._hideLabel)
        return True

    def _hideLabel(self):
        self.label2.visible = False
        self.hideCBHandle = None
        return

    def _animatePosition(self):
        self.component.position.x = self.startPosition.x + math.sin(BigWorld.time()) * 0.25
        if self.parent is not None and self.parent in GUI.roots() or self.component in GUI.roots():
            BigWorld.callback(0.01, self._animatePosition)
        return

    @staticmethod
    def create(parent, pos):
        s = GUI.Window('system/maps/col_white.bmp')
        s.materialFX = 'SOLID'
        s.width = 0.5
        s.height = 0.5
        s.position = pos
        s.script = _MouseEventTester1(parent, s)
        if parent is None:
            GUI.addRoot(s)
        else:
            parent.addChild(s)
        return s


class _MouseEventTester2:

    def __init__(self, parent, component, labelPos, toggleFromHierarchy):
        self.component = component
        component.focus = True
        component.mouseButtonFocus = True
        component.crossFocus = True
        component.moveFocus = True
        self.parent = parent
        self.toggleFromHierarchy = toggleFromHierarchy
        self.label1 = GUI.Text('')
        self.label1.colour = (255, 0, 0, 255)
        self.label1.verticalPositionMode = 'CLIP'
        self.label1.position = labelPos
        self.label2 = GUI.Text('')
        self.label2.colour = (0, 0, 255, 255)
        self.label2.verticalPositionMode = 'CLIP'
        self.label2.position = labelPos + Math.Vector3(0.5, 0, 0)
        self.label3 = GUI.Text('')
        self.label3.colour = (0, 255, 0, 255)
        self.label3.verticalPositionMode = 'CLIP'
        self.label3.position = labelPos + Math.Vector3(-0.5, 0, 0)
        if labelPos[1] > 0:
            self.label1.verticalAnchor = 'TOP'
            self.label2.verticalAnchor = 'TOP'
            self.label3.verticalAnchor = 'TOP'
        elif labelPos[1] < 0:
            self.label1.verticalAnchor = 'BOTTOM'
            self.label2.verticalAnchor = 'BOTTOM'
            self.label3.verticalAnchor = 'BOTTOM'
        if parent is None:
            GUI.addRoot(self.label1)
            GUI.addRoot(self.label2)
            GUI.addRoot(self.label3)
        else:
            parent.addChild(self.label1)
            parent.addChild(self.label2)
            parent.addChild(self.label3)
        BigWorld.callback(1.0, self._hideTimer)
        return

    def handleMouseEnterEvent(self, component):
        self.label1.text = 'handleMouseEnter'
        return True

    def handleMouseLeaveEvent(self, component):
        self.label1.text = 'handleMouseLeave'
        return True

    def handleMouseClickEvent(self, component):
        self.label1.text = 'handleMouseClickEvent'
        return True

    def handleMouseEvent(self, comp, event):
        self.label2.text = 'handleMouseEvent (%s %s %s)' % (event.dx, event.dy, event.dz)
        return True

    def handleMouseButtonEvent(self, component, event):
        self.label1.text = 'handleMouseButtonEvent'
        return True

    def handleKeyEvent(self, event):
        self.label3.text = 'handleKeyEvent (%s, %s)' % (BigWorld.keyToString(event.key), event.isKeyDown())
        return False

    def _hideTimer(self):
        if self.toggleFromHierarchy:
            if self.parent is not None:
                if self.component.parent is not None:
                    self.parent.delChild(self.component)
                else:
                    self.parent.addChild(self.component)
            elif self.component in GUI.roots():
                GUI.delRoot(self.component)
            else:
                GUI.addRoot(self.component)
        else:
            self.component.visible = not self.component.visible
        BigWorld.callback(1.0, self._hideTimer)
        return

    @staticmethod
    def create(parent, pos, labelPos, toggleFromHierarchy):
        s = GUI.Window('system/maps/col_white.bmp')
        s.materialFX = 'SOLID'
        s.width = 0.5
        s.height = 0.25
        s.position = pos
        s.script = _MouseEventTester2(parent, s, labelPos, toggleFromHierarchy)
        if parent is None:
            GUI.addRoot(s)
        else:
            parent.addChild(s)
        return s


def mouseEvents():
    clear()
    r = GUI.Simple('')
    r.width = 2.0
    r.height = 2.0
    GUI.addRoot(r)
    _MouseEventTester1.create(r, (-0.5, 0.0, 0.5))
    _MouseEventTester1.create(r, (0.5, 0.0, 0.5))
    _MouseEventTester2.create(r, (0.0, -0.75, 0.0), (0, -1, 0), False)
    _MouseEventTester2.create(r, (0.0, 0.75, 0.0), (0, 1, 0), True)
