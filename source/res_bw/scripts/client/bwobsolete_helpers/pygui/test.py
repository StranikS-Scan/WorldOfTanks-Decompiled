# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/Test.py
import BigWorld
import GUI
from Window import DraggableWindow
import random
from functools import partial

def clear():
    while len(GUI.roots()):
        GUI.delRoot(GUI.roots()[0])


def _deleteComponent(t):
    if t.parent:
        t.parent.delChild(t)
    else:
        GUI.delRoot(t)


class TestWindow(DraggableWindow):
    factoryString = 'PyGUI.Test.TestWindow'

    def __init__(self, component):
        DraggableWindow.__init__(self, component)

    def buttonClicked(self):
        t = GUI.Text('Button Clicked!')
        t.colour = (255, 0, 0, 255)
        t.position.y = 0.85
        t.verticalAnchor = 'TOP'
        GUI.addRoot(t)
        BigWorld.callback(2.5, partial(_deleteComponent, t))

    def buttonToggled(self, newState):
        self.component.statusLabel.text = 'Toggle state: %s' % ('True' if newState else 'False')

    def draggableBeginDrag(self):
        self.component.draggableStatus.text = 'Dragging'

    def draggableEndDrag(self):
        self.component.draggableStatus.text = ''

    def draggableDragging(self):
        self.component.draggableStatus.colour = (int(random.random() * 127),
         int(random.random() * 127),
         int(random.random() * 127),
         255)

    def onBound(self):
        self.component.button1.script.onClick = self.buttonClicked
        self.component.button2.script.onActivate = lambda : self.buttonToggled(True)
        self.component.button2.script.onDeactivate = lambda : self.buttonToggled(False)
        self.component.draggable.script.onBeginDrag = self.draggableBeginDrag
        self.component.draggable.script.onEndDrag = self.draggableEndDrag
        self.component.draggable.script.onDragging = self.draggableDragging


def testWindow():
    BigWorld.camera(BigWorld.CursorCamera())
    BigWorld.setCursor(GUI.mcursor())
    GUI.mcursor().visible = True
    clear()
    w = GUI.load('gui/tests/window.gui')
    GUI.addRoot(w)
    return w
