# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/ChainView.py
from _PostProcessing import debug as _debug
from _PostProcessing import chain
import BigWorld
import GUI
import Math
import Keys

class EffectView:
    """This class creates a GUI that displays a single effect.  It is
    designed to be created on-demand, and not serialised from xml."""

    def __init__(self, effect, eIdx, maxPhases):
        self.window = GUI.Window()
        self.window.script = self
        self.setToClipMode(self.window)
        self.effectWindow = GUI.Window()
        self.setToClipMode(self.effectWindow)
        self.effectWindow.size = (2, 0.05)
        self.effectWindow.position = (0, 0.95, 1)
        self.effectWindow.verticalAnchor = 'BOTTOM'
        self.effectWindow.textureName = 'system/maps/col_white.dds'
        self.effectWindow.colour = (0, 92, 0, 92)
        self.effectWindow.materialFX = 'BLEND'
        self.addLabel(self.effectWindow, effect.name)
        if effect.bypass != None:
            self.addGraph(self.effectWindow, effect.bypass)
        self.phasesWindow = GUI.Window()
        self.setToClipMode(self.phasesWindow)
        self.phasesWindow.size = (2, 1.95)
        self.phasesWindow.position = (0, 0.95, 1)
        self.phasesWindow.verticalAnchor = 'TOP'
        pIdx = 0
        h = 2.0 / maxPhases
        for p in effect.phases:
            s = self.createPhase(eIdx, pIdx, effect, p, maxPhases)
            s.size = (2.0, h)
            y = float(pIdx) / maxPhases
            s.position = (0.0, 1.0 - 2 * y, 0.5)
            self.phasesWindow.addChild(s)
            pIdx += 1

        self.window.effect = self.effectWindow
        self.window.phases = self.phasesWindow
        return

    def setToClipMode(self, s):
        s.widthMode = 'CLIP'
        s.heightMode = 'CLIP'
        s.horizontalPositionMode = 'CLIP'
        s.verticalPositionMode = 'CLIP'

    def addLabel(self, s, label):
        s.label = GUI.Text(label)
        s.label.font = 'label_small.font'
        s.label.horizontalAnchor = 'LEFT'
        s.label.verticalAnchor = 'TOP'
        self.setToClipMode(s.label)
        s.label.position = (-1, 1, 0.5)

    def addGraph(self, s, v4):
        s.graph = GUI.Graph()
        self.setToClipMode(s.graph)
        s.graph.input = v4
        s.graph.minY = 0.0
        s.graph.maxY = 1.0
        s.graph.frequency = 0.1
        s.graph.nPoints = 50
        s.graph.size = (1.8, 1.8)
        s.graph.colour = (128, 255, 128, 255)

    def displayAlpha(self, show):
        if show:
            for n, c in self.phasesWindow.children:
                c.materialFX = 'BLEND'

        else:
            for n, c in self.phasesWindow.children:
                c.materialFX = 'SOLID'

    def createPhase(self, eIdx, pIdx, e, p, maxPhases):
        d = _debug()
        effects = chain()
        s = GUI.Window('')
        s.texture = d.renderTarget.texture
        uvs = d.phaseUV(eIdx, pIdx, len(effects), len(e.phases))
        bl = (uvs[0], 1.0 - uvs[1])
        tl = (uvs[0], 1.0 - uvs[3])
        tr = (uvs[2], 1.0 - uvs[3])
        br = (uvs[2], 1.0 - uvs[1])
        s.mapping = (tl,
         bl,
         br,
         tr)
        s.horizontalAnchor = 'CENTER'
        s.verticalAnchor = 'TOP'
        s.materialFX = 'SOLID'
        self.setToClipMode(s)
        s.filterType = 'LINEAR'
        try:
            label = '%s (%d x %d)' % (p.name, p.renderTarget.width, p.renderTarget.height)
        except:
            label = '%s' % (p.name,)

        l = self.addLabel(s, label)
        return s


class ChainView:
    """This class provides a simple debug / overview of the
    post-processing chain. It lays out effects horizontally,
    and each effect's phases are laid out vertically from top
    to bottom."""

    def __init__(self, component):
        self.component = component
        f = GUI.Frame2('gui/maps/tooltip_frame.dds')
        f.widthMode = 'CLIP'
        f.heightMode = 'CLIP'
        f.horizontalPositionMode = 'CLIP'
        f.verticalPositionMode = 'CLIP'
        f.position = (0, 0, 0.1)
        f.size = (2, 2)
        self.component.frame = f
        self.mmSpeed = 2.0
        self.setupScrolling()
        from PostProcessing import chainListeners
        chainListeners.append(self.onChainChanged)

    def onChainChanged(self):
        """This makes sure we respond after all other
        chain listeners have responded.  the reason for
        this is other chain listeners do things like set
        up their effect.bypass - which is information we
        need to work with"""
        BigWorld.callback(0, self.onChainChanged2)

    def onChainChanged2(self):
        frame = self.component.frame
        for name, c in self.component.children:
            self.component.delChild(c)

        self.component.frame = frame
        self.createChildren()

    def displayAlpha(self, show):
        for n, c in self.component.children:
            if c.script:
                c.script.displayAlpha(show)

        if show:
            self.component.textureName = 'system/maps/col_red.dds'
            self.component.materialFX = 'SOLID'
        else:
            self.component.textureName = ''
            self.component.materialFX = 'ADD'
        self.component.frame.materialFX = 'ADD'

    def setupScrolling(self):
        self.component.mouseButtonFocus = True
        self.component.moveFocus = True
        self.component.focus = True
        self.isDragging = False
        self.component.transform = GUI.MatrixShader()
        self.scroll = [0, 0]
        self.scrollSpeed = 0.05
        self.scrollTransform = Math.Matrix()
        self.scrollTransform.setIdentity()
        self.calcScrollBounds()

    def calcScrollBounds(self):
        w, h = self.component.size
        minX = -w / 2.0
        maxX = w / 2.0
        minY = -h / 2.0
        maxY = h / 2.0
        if h > 2.0:
            ys = [1 - maxY, -1 - minY]
        else:
            ys = [-1 - minY, 1 - maxY]
        if w > 2.0:
            xs = [1 - maxX, -1 - minX]
        else:
            xs = [-1 - minX, 1 - maxX]
        xs[0] -= 0.95
        ys[0] -= 0.95
        xs[1] += 0.95
        ys[1] += 0.95
        self.minScroll = [xs[0], ys[0]]
        self.maxScroll = [xs[1], ys[1]]

    def scrollTo(self, x, y, animate=False):
        self.scroll[0] = max(x, self.minScroll[0])
        self.scroll[0] = min(self.scroll[0], self.maxScroll[0])
        self.scroll[1] = max(y, self.minScroll[1])
        self.scroll[1] = min(self.scroll[1], self.maxScroll[1])
        self.scrollTransform.setTranslate((self.scroll[0], self.scroll[1], 0))
        self.component.transform.target = self.scrollTransform
        self.component.transform.eta = self.scrollSpeed if animate else 0.0

    def createChildren(self):
        d = _debug()
        if d is None or d.renderTarget is None:
            return
        else:
            effects = chain()
            if len(effects) == 0:
                return
            width = 2.0 / len(effects)
            maxPhases = 0
            for e in effects:
                maxPhases = max(maxPhases, len(e.phases))

            height = 2.0 / maxPhases
            x = -1.0
            eIdx = 0
            for e in effects:
                effectScript = EffectView(e, eIdx, maxPhases)
                s = effectScript.window
                s.height = 2.0
                s.width = width
                s.horizontalAnchor = 'LEFT'
                s.verticalAnchor = 'CENTER'
                s.position = (x, 0.0, 1.0)
                self.component.addChild(s)
                x += width
                eIdx += 1

            return

    def focus(self, state):
        pass

    def handleKeyEvent(self, event):
        return False

    def handleMouseEvent(self, comp, event):
        width = float(BigWorld.screenWidth())
        height = float(BigWorld.screenHeight())
        if self.isDragging:
            self.scrollTo(event.cursorPosition[0] + self.cursorDragOffset[0], event.cursorPosition[1] + self.cursorDragOffset[1])
        elif event.dz != 0:
            amt = 1.0 + event.dz / 1000.0
            w, h = self.component.size
            if not BigWorld.isKeyDown(Keys.KEY_LCONTROL):
                self.component.size = (w * amt, h * amt)
            else:
                self.component.size = (w * amt, h)
            self.calcScrollBounds()
        return True

    def handleMouseButtonEvent(self, comp, event):
        if event.key == Keys.KEY_MIDDLEMOUSE:
            return False
        if event.key == Keys.KEY_LEFTMOUSE:
            self.recordCursorDragOffset()
            self.isDragging = event.isKeyDown()
            return True
        return False

    def recordCursorDragOffset(self):
        self.cursorDragOffset = [0, 0]
        self.cursorDragOffset[0] = self.scroll[0] - GUI.mcursor().position[0]
        self.cursorDragOffset[1] = self.scroll[1] - GUI.mcursor().position[1]

    def handleMouseClickEvent(self, component):
        return False

    def handleMouseEnterEvent(self, comp):
        self.recordCursorDragOffset()
        return False

    def handleMouseLeaveEvent(self, comp):
        return False

    def handleAxisEvent(self, event):
        return False

    def handleDragStartEvent(self, comp):
        return False

    def handleDragStopEvent(self, comp):
        return False

    def handleDragEnterEvent(self, comp, dragged):
        return False

    def handleDragLeaveEvent(self, comp, dragged):
        return False

    def handleDropEvent(self, comp, dropped):
        return False

    def onLoad(self, dataSection):
        pass

    def onSave(self, dataSection):
        pass

    def onBound(self):
        pass
