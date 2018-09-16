# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/EditField.py
import BigWorld, GUI, Keys
from PyGUIBase import PyGUIBase
import copy
import BigWorld
import GUI
import Math
import Keys
import bwobsolete_helpers.PyGUI.IME
import Utils
from Helpers.PyGUI.Listeners import registerDeviceListener
from Helpers.PyGUI.Utils import BlinkingCursor
from Helpers.PyGUI.Utils import blinkingColourProvider
from Helpers.PyGUI.Utils import getHPixelScalar, getVPixelScalar
from Helpers.PyGUI.Utils import CURSOR_WIDTH
from Helpers.PyGUI import PyGUIBase
from Helpers.PyGUI.FocusManager import *
SCROLL_SKIP_AMOUNT = 8
DEFAULT_TEXT_COLOUR_ACTIVE = (255, 255, 255, 255)
DEFAULT_TEXT_COLOUR_INACTIVE = (155, 155, 155, 255)

def gotComposition():
    return len(BigWorld.ime.composition) > 0


def skipWordRight(s, cursorPos):
    s = unicode(s)
    i = cursorPos
    while i < len(s) and s[i] not in Utils.WHITESPACE:
        i += 1

    while i < len(s) and s[i] in Utils.WHITESPACE:
        i += 1

    return i


def skipWordLeft(s, cursorPos):
    s = unicode(s)
    i = cursorPos - 1
    while i > 0 and s[i] in Utils.WHITESPACE:
        i -= 1

    while i > 0 and s[i - 1] not in Utils.WHITESPACE:
        i -= 1

    return i


def skipWord(s, cursorPos, direction):
    if direction > 0:
        return skipWordRight(s, cursorPos)
    else:
        return skipWordLeft(s, cursorPos)


class EditField(PyGUIBase):
    factoryString = 'PyGUI.EditField'

    def __init__(self, component=None):
        PyGUIBase.__init__(self, component)
        self.cursorIndex = 0
        self.scrollInPixels = 0
        self.onEnter = None
        self.onEscape = None
        self.maxLength = 256
        self.enabled = True
        self.enableIME = False
        self.focusViaMouse = True
        self.focusObserver = None
        self.shouldAdjustClipping = False
        self.__externalKeyEventHandler = None
        self.__allowAutoDefocus = True
        if self.component is None:
            self.component = GUI.Window('system/maps/col_white.bmp')
            self.component.colour = (0, 0, 0, 255)
            self.component.materialFX = 'BLEND'
            self.component.width = 0.75
            self.component.height = 0.1
            self.component.heightMode = 'CLIP'
            self.component.widthMode = 'CLIP'
            self.component.minScroll = (-100, -100)
            self.component.maxScroll = (+100, +100)
            self.component.script = self
            self.onBound()
        self.autoSelectionFonts = ['default_medium.font']
        self.idealVisibleCharacters = 80
        registerDeviceListener(self)
        return

    def setExternalKeyEventHandler(self, cb):
        self.__externalKeyEventHandler = cb

    def onBound(self):
        if hasattr(self.component, 'cursor'):
            self.component.delChild(self.component.cursor)
        self.activeColour = DEFAULT_TEXT_COLOUR_ACTIVE
        self.inactiveColour = DEFAULT_TEXT_COLOUR_INACTIVE
        text = self.component.text
        text.horizontalAnchor = 'LEFT'
        text.horizontalPositionMode = 'PIXEL'
        text.position.x = 0
        text.colour = self.inactiveColour
        if len(self.autoSelectionFonts) == 0:
            self.autoSelectionFonts = [self.component.text.font]
        self.cursor = BlinkingCursor()
        self.component.addChild(self.cursor.comp, 'cursor')
        self._updateCursor()
        self.cursor.enable(False)
        PyGUIBase.onBound(self)
        self._selectFontBestMatch()

    def setEnabled(self, state):
        self.enabled = state
        if not state:
            self.focus(False)

    def fitVertically(self):
        heightMode = self.component.heightMode
        self.component.heightMode = 'PIXEL'
        _, self.component.height = self.component.text.stringDimensions('W')
        self.component.height *= getVPixelScalar()
        self.component.heightMode = heightMode

    def setText(self, text):
        c = self.component.text
        c.text = unicode(text[:self.maxLength])
        self.scrollInPixels = 0
        self.component.scroll.x = 0
        self.cursorIndex = len(c.text)
        self._updateCursor()

    def getText(self):
        return self.component.text.text

    def onLoad(self, dataSection):
        PyGUIBase.onLoad(self, dataSection)
        self.maxLength = dataSection.readInt('maxLength', self.maxLength)
        self.focusViaMouse = dataSection.readBool('focusViaMouse', True)
        self.enableIME = dataSection.readBool('enableIME', False)
        self.shouldAdjustClipping = dataSection.readBool('shouldAdjustClipping', False)
        self.activeColour = dataSection.readVector4('activeColour', DEFAULT_TEXT_COLOUR_ACTIVE)
        self.inactiveColour = dataSection.readVector4('inactiveColour', DEFAULT_TEXT_COLOUR_INACTIVE)
        self.__allowAutoDefocus = dataSection.readBool('allowAutoDefocus', True)
        self.idealVisibleCharacters = dataSection.readInt('idealVisibleCharacters', self.idealVisibleCharacters)
        fonts = dataSection.readStrings('autoFont')
        if len(fonts) > 0:
            self.autoSelectionFonts = fonts

    def onSave(self, dataSection):
        PyGUIBase.onSave(self, dataSection)
        dataSection.writeInt('maxLength', self.maxLength)
        dataSection.writeBool('focusViaMouse', self.focusViaMouse)
        dataSection.writeBool('enableIME', self.enableIME)
        dataSection.writeBool('shouldAdjustClipping', self.shouldAdjustClipping)
        dataSection.writeVector4('activeColour', self.activeColour)
        dataSection.writeVector4('inactiveColour', self.inactiveColour)
        dataSection.writeBool('allowAutoDefocus', self.__allowAutoDefocus)

    def addFocusObserver(self, focusObserver):
        self.focusObserver = focusObserver

    def handleKeyEvent(self, event):
        if not self.enabled:
            return False
        elif event.isMouseButton():
            return False
        else:
            c = self.component.text
            character = event.character
            handled = False
            touchCursor = False
            if event.isKeyDown():
                if event.key in [Keys.KEY_RETURN, Keys.KEY_NUMPADENTER]:
                    handled = True
                    if self.eventHandler is not None:
                        textString = c.text
                        self.eventHandler.onClick(c.text)
                    elif self.onEnter is not None:
                        self.onEnter(c.text)
                elif event.key == Keys.KEY_BACKSPACE:
                    if self.cursorIndex > 0:
                        c.text = c.text[:self.cursorIndex - 1] + c.text[self.cursorIndex:]
                        self.cursorIndex -= 1
                        self._updateCursor()
                    touchCursor = True
                    handled = True
                elif event.key == Keys.KEY_DELETE:
                    if self.cursorIndex < len(c.text):
                        c.text = c.text[:self.cursorIndex] + c.text[self.cursorIndex + 1:]
                        self._updateCursor()
                    touchCursor = True
                    handled = True
                elif event.key in [Keys.KEY_LEFTARROW, Keys.KEY_RIGHTARROW]:
                    direction = 1 if event.key == Keys.KEY_RIGHTARROW else -1
                    if event.isCtrlDown():
                        self.cursorIndex = skipWord(c.text, self.cursorIndex, direction)
                    else:
                        self.cursorIndex += direction
                    self._updateCursor()
                    touchCursor = True
                    handled = True
                elif event.key == Keys.KEY_HOME:
                    self.cursorIndex = 0
                    self._updateCursor()
                    touchCursor = True
                    handled = True
                elif event.key == Keys.KEY_END:
                    self.cursorIndex = len(self._getText().text)
                    self._updateCursor()
                    touchCursor = True
                    handled = True
                elif event.key == Keys.KEY_ESCAPE:
                    if self.onEscape is not None:
                        self.onEscape()
                        handled = True
                elif character is not None:
                    self._insertString(character)
                    touchCursor = True
                    handled = True
                elif self.__externalKeyEventHandler is not None:
                    handled = self.__externalKeyEventHandler(event)
            if touchCursor:
                self.cursor.touch()
            return handled

    def handleMouseButtonEvent(self, comp, event):
        if self.enabled and event.isKeyDown() and event.key == Keys.KEY_LEFTMOUSE:
            setFocusedComponent(self.component)
            self.cursorIndex = self.screenToCharacterIndex(GUI.mcursor().position)
            self._updateCursor()
            self.cursor.touch()
            return True
        return False

    def handleIMEEvent(self, event):
        self._updateCursor()
        cursorPosClip = self.cursor.getScreenClipPosition()
        clipMin, clipMax = Utils.clipRegion(self.component)
        Helpers.PyGUI.IME.handleIMEEvent(event, cursorPosClip, clipMin, clipMax, self.component.text.font)
        return False

    def focus(self, state):
        if self.component.parent is not None and self.component.parent.script is not None:
            pscript = self.component.parent.script
            if hasattr(pscript, 'editFieldChangeFocus'):
                pscript.editFieldChangeFocus(self, state)
        if not self.enabled and state:
            setFocusedComponent(None)
            return
        else:
            BigWorld.ime.enabled = state and self.enableIME
            self.component.text.colour = self.activeColour if state else self.inactiveColour
            self._updateCursor()
            if not state:
                self.cursor.enable(False)
            return

    def screenToCharacterIndex(self, clipPos):
        oldWidthMode = self.component.widthMode
        self.component.widthMode = 'PIXEL'
        locPos = self.component.screenToLocal(clipPos)
        self.component.widthMode = oldWidthMode
        clickedAtPixel = locPos.x / getHPixelScalar()
        w = 0
        idx = 0
        text = self.component.text.text
        for c in text:
            cw = self.component.text.stringWidth(c)
            if clickedAtPixel <= w + cw / 2:
                return idx
            w += cw
            idx += 1

        return len(text)

    def allowAutoDefocus(self):
        return self.__allowAutoDefocus

    def _insertString(self, s):
        c = self.component.text
        curLen = len(c.text)
        s = s[:max(self.maxLength - curLen, 0)]
        c.text = c.text[:self.cursorIndex] + s + c.text[self.cursorIndex:]
        self.cursorIndex += len(s)
        self._updateCursor()

    def _updateCursor(self):
        text = self._getText()
        textLen = len(text.text)
        self.cursorIndex = max(self.cursorIndex, 0)
        self.cursorIndex = min(self.cursorIndex, textLen)
        cursorComp = self.cursor.comp
        cursorComp.position.x = text.stringWidth(text.text[:self.cursorIndex]) * getHPixelScalar()
        self._scrollIntoView()
        self.cursor.enable(self.enabled and not gotComposition() and isFocusedComponent(self.component))

    def _scrollIntoView(self):
        hratio = getHPixelScalar()
        textArea = self.component
        widthMode = textArea.widthMode
        textArea.widthMode = 'PIXEL'
        textAreaWidth = textArea.width / hratio
        textArea.widthMode = widthMode
        cursorPosInPixels = textArea.cursor.position.x / hratio
        relCursorPos = cursorPosInPixels - self.scrollInPixels
        if relCursorPos > 0 and relCursorPos < textAreaWidth:
            return
        textComponent = textArea.text
        cursorIdx = self.cursorIndex
        if relCursorPos < 0:
            startingString = textComponent.text[cursorIdx - SCROLL_SKIP_AMOUNT:cursorIdx + 1]
            startingWidth = textComponent.stringWidth(startingString)
            self.scrollInPixels = cursorPosInPixels - startingWidth
        elif relCursorPos > textAreaWidth - 5:
            trailingString = textComponent.text[cursorIdx - 1:cursorIdx + SCROLL_SKIP_AMOUNT]
            trailingWidth = textComponent.stringWidth(trailingString)
            self.scrollInPixels = cursorPosInPixels - textAreaWidth + trailingWidth
        self.scrollInPixels = max(self.scrollInPixels, 0)
        self.scrollInPixels = min(self.scrollInPixels, abs(self._textWidthInPixels() - textAreaWidth) + CURSOR_WIDTH)
        self._applyScroll()

    def _applyScroll(self):
        scrollX = -self.scrollInPixels / (GUI.screenResolution()[0] * 0.5)
        scrollX = scrollX * getHPixelScalar()
        self.component.scroll = (scrollX, 0.0)

    def _getCursor(self):
        return self.component.cursor

    def _getText(self):
        return self.component.text

    def _textWidthInPixels(self):
        c = self._getText()
        return c.stringWidth(c.text)

    def _selectFontBestMatch(self):
        selectedFont = Utils.autoSelectFont(self.autoSelectionFonts, self.idealVisibleCharacters, self._widthInPixels(), self.component.text)
        self.component.text.font = selectedFont

    def _widthInPixels(self):
        widthMode = self.component.widthMode
        self.component.widthMode = 'PIXEL'
        w = self.component.width
        self.component.widthMode = widthMode
        return w / getHPixelScalar()

    def onRecreateDevice(self):
        self._selectFontBestMatch()
        self._updateCursor()
        if self.component.focus and self.enableIME:
            cursorPosClip = self.cursor.getScreenClipPosition()
            clipMin, clipMax = Utils.clipRegion(self.component)
            Helpers.PyGUI.IME.refresh(cursorPosClip, clipMin, clipMax, self.component.text.font)

    @staticmethod
    def create(self):
        return EditField().component
