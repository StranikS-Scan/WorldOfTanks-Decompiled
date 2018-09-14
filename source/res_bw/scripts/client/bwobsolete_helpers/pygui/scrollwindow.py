# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/ScrollWindow.py
import BigWorld, GUI, Keys
from PyGUIBase import PyGUIBase

class ScrollWindow(PyGUIBase):
    factoryString = 'PyGUI.ScrollWindow'

    def __init__(self, component):
        PyGUIBase.__init__(self, component)

    def handleKeyEvent(self, event):
        c = self.component
        key = event.key
        if event.isKeyDown():
            if key == Keys.KEY_JOYDUP or key == Keys.KEY_UPARROW:
                x, y = c.scroll
                y += 0.1
                c.scroll = (x, y)
                BigWorld.playSound('ui/tick')
                return True
            if key == Keys.KEY_JOYDDOWN or key == Keys.KEY_DOWNARROW:
                x, y = c.scroll
                y -= 0.1
                c.scroll = (x, y)
                BigWorld.playSound('ui/tick')
                return True
            if key == Keys.KEY_JOYDRIGHT or key == Keys.KEY_RIGHTARROW:
                x, y = c.scroll
                x += 0.1
                c.scroll = (x, y)
                BigWorld.playSound('ui/tick')
                return True
            if key == Keys.KEY_JOYDLEFT or key == Keys.KEY_LEFTARROW:
                x, y = c.scroll
                x -= 0.1
                c.scroll = (x, y)
                BigWorld.playSound('ui/tick')
                return True
        return False


class ZoomScrollWindow(ScrollWindow):
    factoryString = 'PyGUI.ZoomScrollWindow'

    def __init__(self, component):
        ScrollWindow.__init__(self, component)
        self.zoomFactor = 1

    def updateScrollLimits(self):
        c = self.component.children[0][1]
        w, h = c.width, c.height
        x, y = self.component.maxScroll
        x = (w - self.component.width) / 2
        y = (h - self.component.height) / 2
        self.component.maxScroll = (x, y)
        self.component.minScroll = (-x, -y)

    def handleKeyEvent(self, event):
        handled = ScrollWindow.handleKeyEvent(self, event)
        if not handled and down:
            if event.key == Keys.KEY_JOYALPUSH:
                if self.zoomFactor > 1:
                    c = self.component.children[0][1]
                    c.width = c.width / 2
                    c.height = c.height / 2
                    self.updateScrollLimits()
                    self.zoomFactor = self.zoomFactor - 1
                BigWorld.playSound('ui/boop')
                return True
            if event.key in [Keys.KEY_JOYARPUSH, Keys.KEY_MIDDLEMOUSE]:
                c = self.component.children[0][1]
                c.width = c.width * 2
                c.height = c.height * 2
                self.updateScrollLimits()
                self.zoomFactor = self.zoomFactor + 1
                BigWorld.playSound('ui/boop')
                return True
        return False
