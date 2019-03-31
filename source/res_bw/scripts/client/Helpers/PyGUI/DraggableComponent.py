# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/PyGUI/DraggableComponent.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld, GUI, Math, Keys
import Utils

class DraggableComponent:

    def __init__(self, horzDrag, vertDrag, restrictToParent):
        self.horzDrag = horzDrag
        self.vertDrag = vertDrag
        self.restrictToParent = restrictToParent
        self.component.focus = True
        self.component.moveFocus = True
        self.component.crossFocus = True
        self.onBeginDrag = lambda : None
        self.onEndDrag = lambda : None
        self.onDragging = lambda : None

    def handleMouseButtonEvent(self, comp, event):
        if event.key == Keys.KEY_LEFTMOUSE and (self.horzDrag or self.vertDrag):
            if event.isKeyDown():
                self.startDragging(event.cursorPosition)
            elif dragManager.isDragging():
                self.stopDragging()
        return True

    def onSave(self, dataSection):
        dataSection.writeBool('horzDrag', self.horzDrag)
        dataSection.writeBool('vertDrag', self.vertDrag)
        dataSection.writeBool('restrictToParent', self.restrictToParent)

    def onLoad(self, dataSection):
        self.horzDrag = dataSection.readBool('horzDrag')
        self.vertDrag = dataSection.readBool('vertDrag')
        self.restrictToParent = dataSection.readBool('restrictToParent')

    def startDragging(self, cursorPosition):
        dragManager.startDragging(self.component, self.horzDrag, self.vertDrag, self.restrictToParent, cursorPosition)

    def stopDragging(self):
        dragManager.stopDragging()


def _horzAnchorOffset(component):
    if component.horizontalAnchor == 'LEFT':
        return 0
    if component.horizontalAnchor == 'CENTER':
        return -component.width / 2.0
    if component.horizontalAnchor == 'RIGHT':
        return -component.width


def _vertAnchorOffset(component):
    if component.verticalAnchor == 'TOP':
        return 0
    if component.verticalAnchor == 'CENTER':
        return component.height / 2.0
    if component.verticalAnchor == 'BOTTOM':
        return component.height


class ComponentDragManager:

    def __init__(self):
        self.component = None
        self.offset = (0, 0)
        self.horzDrag = False
        self.vertDrag = False
        self.restrictToParent = False
        return

    def isDragging(self):
        return self.component is not None

    def startDragging(self, component, horzDrag, vertDrag, restrictToParent, mpos):
        if self.component:
            print 'WARNING: startDragging called again without first calling stop!'
            self.stopDragging()
        self.horzDrag = horzDrag
        self.vertDrag = vertDrag
        self.restrictToParent = restrictToParent
        cpos = Utils.absoluteClipPosition(component)
        mpos = Math.Vector2(mpos)
        self.offset = Math.Vector2(mpos.x - cpos.x, mpos.y - cpos.y)
        self.component = component
        if restrictToParent:
            self.restrictHorizontally()
            self.restrictVertically()
        if hasattr(self.component.script, 'onBeginDrag'):
            self.component.script.onBeginDrag()

    def stopDragging(self):
        if not self.component:
            print 'WARNING: stopDragging called without any component currently being dragged!'
        if self.component is not None:
            if hasattr(self.component.script, 'onEndDrag'):
                self.component.script.onEndDrag()
        self.component = None
        return

    def handleKeyEvent(self, event):
        if not event.isRepeatedEvent() and event.key == Keys.KEY_LEFTMOUSE and not event.isKeyDown() and self.isDragging():
            self.stopDragging()
            return True
        return False

    def handleMouseEvent(self, event):
        if self.component is None:
            return False
        else:
            mpos = event.cursorPosition
            cpos = Math.Vector2(mpos[0] - self.offset.x, mpos[1] - self.offset.y)
            nrp = Utils.nearestRelativeParent(self.component)
            while 1:
                nrpPos = nrp is not None and Utils.legacyPosition(nrp)
                cpos.x = cpos.x - nrpPos.x
                cpos.y = cpos.y - nrpPos.y
                nrp = Utils.nearestRelativeParent(nrp)

            startPos = tuple(self.component.position)
            if self.horzDrag:
                horzMode = self.component.horizontalPositionMode
                self.component.horizontalPositionMode = 'LEGACY'
                self.component.position.x = cpos.x
                x = cpos.x
                self.component.horizontalPositionMode = horzMode
                if self.restrictToParent:
                    self.restrictHorizontally()
            if self.vertDrag:
                vertMode = self.component.verticalPositionMode
                self.component.verticalPositionMode = 'LEGACY'
                self.component.position.y = cpos.y
                self.component.verticalPositionMode = vertMode
                if self.restrictToParent:
                    self.restrictVertically()
            draggedHorz = self.component.position.x != startPos[0]
            draggedVert = self.component.position.y != startPos[1]
            if not draggedHorz:
                dragged = draggedVert
                dragged and hasattr(self.component.script, 'onDragging') and self.component.script.onDragging()
            return True

    def restrictHorizontally(self):
        if self.component is None:
            return
        else:
            horzMode = self.component.horizontalPositionMode
            widthMode = self.component.widthMode
            self.component.horizontalPositionMode = 'CLIP'
            self.component.widthMode = 'CLIP'
            anchorOffsetX = _horzAnchorOffset(self.component)
            restricted = True
            if self.component.position.x < -1.0 - anchorOffsetX:
                self.component.position.x = -1.0 - anchorOffsetX
            elif self.component.position.x > 1.0 + anchorOffsetX:
                self.component.position.x = 1.0 + anchorOffsetX
            else:
                restricted = False
            self.component.horizontalPositionMode = horzMode
            self.component.widthMode = widthMode
            return restricted

    def restrictVertically(self):
        if self.component is None:
            return
        else:
            vertMode = self.component.verticalPositionMode
            heightMode = self.component.heightMode
            self.component.verticalPositionMode = 'CLIP'
            self.component.heightMode = 'CLIP'
            anchorOffsetY = _vertAnchorOffset(self.component)
            restricted = True
            if self.component.position.y < -1.0 + anchorOffsetY:
                self.component.position.y = -1.0 + anchorOffsetY
            elif self.component.position.y > 1.0 - anchorOffsetY:
                self.component.position.y = 1.0 - anchorOffsetY
            else:
                restricted = False
            self.component.verticalPositionMode = vertMode
            self.component.heightMode = heightMode
            return restricted


dragManager = ComponentDragManager()
