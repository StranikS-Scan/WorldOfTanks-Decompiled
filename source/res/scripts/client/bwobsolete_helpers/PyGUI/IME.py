# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/IME.py
import BigWorld
import GUI
import Math
import Utils
from Utils import BlinkingCursor
from Utils import blinkingColourProvider
from Utils import getHPixelScalar, getVPixelScalar
from bwdebug import *
ALWAYS_ON_TOP_Z = 0.01
BACKGROUND_COLOUR = (32, 32, 32, 255)
DEFAULT_FONT_NAME = 'default_small.font'
SELECTED_CANDIDATE_BGCOLOUR = (220, 220, 220, 255)
SELECTED_CANDIDATE_FGCOLOUR = (16, 16, 16, 255)
ATTR_INPUT = 0
ATTR_TARGET_CONVERTED = 1
ATTR_CONVERTED = 2
ATTR_TARGET_NOTCONVERTED = 3
ATTR_INPUT_ERROR = 4
ATTR_FIXEDCONVERTED = 5

def _attrToColours(attr):
    bgColour = None
    fgColour = None
    if attr in [ATTR_INPUT, ATTR_CONVERTED]:
        bgColour = (32, 32, 32, 255)
        fgColour = (255, 255, 255, 255)
    else:
        bgColour = (220, 220, 220, 255)
        fgColour = (16, 16, 16, 255)
    return (bgColour, fgColour)


def _compositionStringBlocks():
    comp = BigWorld.ime.composition
    attr = BigWorld.ime.compositionAttr
    if len(comp) == 0:
        return []
    ret = []
    currentAttr = attr[0]
    currentBlock = u''
    for idx in range(len(comp)):
        if attr[idx] != currentAttr:
            ret.append((currentAttr, currentBlock))
            currentAttr = attr[idx]
            currentBlock = u''
        currentBlock += comp[idx]

    if len(currentBlock) > 0:
        ret.append((currentAttr, currentBlock))
    return ret


def _bgText(text, font, bgcolour, fgcolour):
    w = Utils.createTextWithBackground(text, font, bgcolour, fgcolour)
    w.colouriser = GUI.ColourShader()
    w.colouriser.colourProvider = bgcolour
    w.text.colouriser = GUI.ColourShader()
    w.text.colouriser.colourProvider = fgcolour
    return w


def logIMEEvent(event):
    print str(event) + ':'
    print '   stateChanged=' + str(event.stateChanged) + " (value='" + str(BigWorld.ime.state) + "')"
    print '   candidatesVisibilityChanged=' + str(event.candidatesVisibilityChanged) + ' (value=' + str(BigWorld.ime.candidatesVisible) + ')'
    print '   candidatesChanged=' + str(event.candidatesChanged) + " (value='" + str(BigWorld.ime.candidates) + "', attrs=" + str(BigWorld.ime.compositionAttr) + ')'
    print '   selectedCandidateChanged=' + str(event.selectedCandidateChanged) + ' (value=' + str(BigWorld.ime.selectedCandidate) + ')'
    print '   compositionChanged=' + str(event.compositionChanged) + " (value='" + str(BigWorld.ime.composition) + "')"
    print '   compositionCursorPositionChanged=' + str(event.compositionCursorPositionChanged) + ' (value=' + str(BigWorld.ime.compositionCursorPosition) + ')'
    print '   readingVisibilityChanged=' + str(event.readingVisibilityChanged) + ' (value=' + str(BigWorld.ime.readingVisible) + ')'
    print '   readingChanged=' + str(event.readingChanged) + " (value='" + str(BigWorld.ime.reading) + "')"


class CompositionWindow(object):

    def __init__(self):
        self.comp = GUI.Window('system/maps/col_white.bmp')
        self.comp.materialFX = GUI.Simple.eMaterialFX.BLEND
        self.comp.visible = False
        self.comp.script = self
        self.comp.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.verticalAnchor = GUI.Simple.eVAnchor.CENTER
        self.comp.widthMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.heightMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.position.z = ALWAYS_ON_TOP_Z
        self.comp.addChild(GUI.Text(), 'text')
        self.comp.text.font = DEFAULT_FONT_NAME
        self.comp.text.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.text.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.text.colouriser = GUI.ColourShader()
        self.comp.text.colouriser.colourProvider = self.comp.text.colour
        self.cursor = BlinkingCursor()
        self.comp.addChild(self.cursor.comp, 'cursor')
        self.cursor.enable(True)
        self.comp.backgroundColouriser = GUI.ColourShader()
        self.comp.backgroundColouriser.colourProvider = BACKGROUND_COLOUR
        self._firstTargetConvertedBlock = -1

    def populate(self, fontName):
        if len(BigWorld.ime.composition) == 0:
            self.comp.visible = False
            return False
        for name, comp in self.comp.children:
            if name not in ('cursor', 'text'):
                self.comp.delChild(comp)

        if BigWorld.ime.language == 'KOREAN':
            self._populateKorean(fontName)
        else:
            self._populateChineseJapanese(fontName)
        self.comp.visible = True
        return True

    def _populateChineseJapanese(self, fontName):
        compString = BigWorld.ime.composition
        self.comp.text.font = fontName
        self.comp.text.text = ''
        compBlocks = _compositionStringBlocks()
        self._firstTargetConvertedBlock = -1
        fullWidth = 0
        idx = 0
        for attr, str in compBlocks:
            bgColour, fgColour = _attrToColours(attr)
            if self._firstTargetConvertedBlock < 0 and attr not in [ATTR_INPUT, ATTR_CONVERTED]:
                self._firstTargetConvertedBlock = idx
            w = _bgText(str, fontName, bgColour, fgColour)
            w.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
            w.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
            w.position.x = fullWidth
            self.comp.addChild(w, 'compBlock%d' % idx)
            idx += 1
            fullWidth += w.width

        self.comp.widthMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.width = fullWidth
        _, self.comp.height = self.comp.compBlock0.text.stringDimensions(compString)
        self.comp.height = self.comp.height * getVPixelScalar()
        cursorIndex = BigWorld.ime.compositionCursorPosition
        cursorOffset = self.comp.compBlock0.text.stringWidth(compString[:cursorIndex])
        self.cursor.comp.position.x = cursorOffset * getHPixelScalar()
        self.comp.backgroundColouriser.colourProvider = BACKGROUND_COLOUR
        self.cursor.enable(True)
        self.cursor.touch()

    def _populateKorean(self, fontName):
        compString = BigWorld.ime.composition
        self.comp.text.font = fontName
        self.comp.text.text = compString
        sw, sh = self.comp.text.stringDimensions(compString)
        hratio = getHPixelScalar()
        vratio = getVPixelScalar()
        self.comp.width = sw * hratio
        self.comp.height = sh * vratio
        self.comp.text.position.x = 0
        self.comp.backgroundColouriser.colourProvider = blinkingColourProvider(BACKGROUND_COLOUR, Utils.CURSOR_BLINK_PERIOD)
        self.cursor.enable(False)

    def reposition(self, positionClip, minClip, maxClip):
        widthInClip, heightInClip = Utils.clipSize(self.comp)
        if positionClip[0] + widthInClip > maxClip[0]:
            positionClip = minClip
        self.comp.position.x = positionClip.x
        self.comp.position.y = positionClip.y

    def clipBounds(self):
        return Utils.clipRegion(self.comp)

    def candidateClipBounds(self):
        clipMins, clipMaxs = self.cursor.clipBounds()
        if BigWorld.ime.language == 'JAPANESE':
            ftcb = self._firstTargetConvertedBlock
            block = getattr(self.comp, 'compBlock%d' % ftcb, None)
            if block is not None:
                widthMode = block.widthMode
                block.widthMode = GUI.Simple.eSizeMode.CLIP
                blockMins = block.localToScreen((-1, -1))
                block.widthMode = widthMode
                clipMins[0] = blockMins[0]
                clipMaxs[0] = blockMins[0]
        return (clipMins, clipMaxs)

    def hide(self):
        self.comp.visible = False


class ReadingWindow(object):
    MARGIN_SIZE = 2

    def __init__(self):
        self.comp = GUI.Window('system/maps/col_white.bmp')
        self.comp.materialFX = GUI.Simple.eMaterialFX.BLEND
        self.comp.colour = BACKGROUND_COLOUR
        self.comp.visible = False
        self.comp.script = self
        self.comp.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.verticalAnchor = GUI.Simple.eVAnchor.RIGHT
        self.comp.widthMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.heightMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.position.z = ALWAYS_ON_TOP_Z
        self.comp.addChild(GUI.Text(''), 'text')
        self.comp.text.multiline = True
        self.comp.text.font = DEFAULT_FONT_NAME
        self.comp.text.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.text.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.text.verticalAnchor = GUI.Simple.eVAnchor.TOP
        self.comp.text.verticalPositionMode = GUI.Simple.eSizeMode.PIXEL

    def populate(self, fontName):
        readingString = BigWorld.ime.reading
        if not BigWorld.ime.readingVisible or len(readingString) == 0:
            self.comp.visible = False
            return False
        self.comp.text.font = fontName
        if BigWorld.ime.readingVertical:
            readingString = '\n'.join([ c for c in readingString ])
        horzMargin = self.MARGIN_SIZE * getHPixelScalar()
        vertMargin = self.MARGIN_SIZE * getVPixelScalar()
        self.comp.text.text = readingString
        self.comp.text.position.x = horzMargin
        self.comp.text.position.y = vertMargin
        self.comp.widthMode = GUI.Simple.eSizeMode.PIXEL
        textWidth, textHeight = self.comp.text.stringDimensions(readingString)
        self.comp.width = horzMargin * 2 + textWidth * getHPixelScalar()
        self.comp.height = vertMargin * 2 + textHeight * getVPixelScalar()
        self.comp.visible = True
        return True

    def reposition(self, screenClip):
        self.comp.position[0] = screenClip[0]
        self.comp.position[1] = screenClip[1]
        self.comp.visible = True

    def clipBounds(self):
        return Utils.clipRegion(self.comp)

    def hide(self):
        self.comp.visible = False


class CandidateWindow(object):

    def __init__(self):
        self.comp = GUI.Window('system/maps/col_white.bmp')
        self.comp.colour = (32, 32, 32, 255)
        self.comp.materialFX = GUI.Simple.eMaterialFX.BLEND
        self.comp.visible = False
        self.comp.script = self
        self.comp.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.position.x = 0
        self.comp.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        self.comp.verticalAnchor = GUI.Simple.eVAnchor.TOP
        self.comp.position.y = 0
        self.comp.position.z = ALWAYS_ON_TOP_Z
        self.comp.widthMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.heightMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.addChild(GUI.Text(''), 'candidateText')
        self.comp.candidateText.font = DEFAULT_FONT_NAME
        self.comp.candidateText.multiline = True
        self.comp.candidateText.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.candidateText.verticalPositionMode = GUI.Simple.eSizeMode.PIXEL
        self.comp.candidateText.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        self.comp.candidateText.verticalAnchor = GUI.Simple.eVAnchor.TOP
        self.comp.candidateText.position = (0, 0, 0.5)

    def populate(self, fontName):
        if not BigWorld.ime.candidatesVisible:
            self.comp.visible = False
            return False
        candidates = BigWorld.ime.candidates
        selectedIdx = BigWorld.ime.selectedCandidate
        fullText = u''
        preSelectWidth = 0
        for i in range(len(candidates)):
            fullText += str(i + 1) + candidates[i]
            if i < len(candidates) - 1:
                fullText += u'\n' if BigWorld.ime.candidatesVertical else u' '
            if i == selectedIdx - 1:
                preSelectWidth, _ = self.comp.candidateText.stringDimensions(fullText)

        self.comp.candidateText.font = fontName
        self.comp.candidateText.text = fullText
        sw, sh = self.comp.candidateText.stringDimensions(fullText)
        self._resize(sw, sh)
        if hasattr(self.comp, 'selectedCandidate'):
            self.comp.delChild(self.comp.selectedCandidate)
        if len(candidates) > 0:
            selStr = str(selectedIdx + 1) + candidates[selectedIdx]
            selectedComp = _bgText(selStr, fontName, SELECTED_CANDIDATE_BGCOLOUR, SELECTED_CANDIDATE_FGCOLOUR)
            selectedComp.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
            selectedComp.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
            selectedComp.verticalAnchor = GUI.Simple.eVAnchor.TOP
            selectedComp.verticalPositionMode = GUI.Simple.eSizeMode.PIXEL
            selectedComp.position.z = 0.01
            selectedComp.text.horizontalPositionMode = GUI.Simple.eSizeMode.PIXEL
            selectedComp.text.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
            selectedComp.text.position.x = 0
            fontWidth, fontHeight = self.comp.candidateText.stringDimensions(selStr)
            if BigWorld.ime.candidatesVertical:
                selectedComp.position.x = 0
                selectedComp.position.y = fontHeight * selectedIdx * getVPixelScalar()
                selectedComp.widthMode = self.comp.widthMode
                selectedComp.width = self.comp.width
            else:
                selectedComp.position.x = preSelectWidth * getHPixelScalar()
                selectedComp.position.y = 0
                selectedComp.widthMode = GUI.Simple.eSizeMode.PIXEL
                selectedComp.width = (fontWidth + 1) * getHPixelScalar()
                selectedComp.heightMode = self.comp.heightMode
                selectedComp.height = self.comp.height
            self.comp.addChild(selectedComp, 'selectedCandidate')
        self.comp.visible = True
        return True

    def reposition(self, screenClipMins, screenClipMaxs):
        clipWidth, clipHeight = Utils.clipSize(self.comp)
        cx, cy = screenClipMaxs.x, screenClipMins.y
        if cy - clipHeight < -1.0:
            cy = screenClipMaxs.y + clipHeight
        self.comp.position[0] = cx
        self.comp.position[1] = cy

    def _resize(self, pixelW, pixelH):
        self.comp.width = pixelW * getHPixelScalar()
        self.comp.height = pixelH * getVPixelScalar()

    def hide(self):
        self.comp.visible = False


_composition = None
_reading = None
_candidates = None

def init():
    global _composition
    global _reading
    global _candidates
    TRACE_MSG('Initialising IME components')
    if _composition is None:
        _composition = CompositionWindow()
        GUI.addRoot(_composition.comp)
    if _reading is None:
        _reading = ReadingWindow()
        GUI.addRoot(_reading.comp)
    if _candidates is None:
        _candidates = CandidateWindow()
        GUI.addRoot(_candidates.comp)
    return


def fini():
    global _reading
    global _candidates
    global _composition
    if _composition is not None:
        GUI.delRoot(_composition.comp)
        _composition = None
    if _reading is not None:
        GUI.delRoot(_reading.comp)
        _reading = None
    if _candidates is not None:
        GUI.delRoot(_candidates.comp)
        _candidates = None
    return


def refresh(positionClip, minClip, maxClip, fontName):
    if _composition is None or _candidates is None or _reading is None:
        ERROR_MSG('IME components have not been initialised.')
        return
    else:
        gotComposition = _composition.populate(fontName)
        gotReading = _reading.populate(fontName)
        gotCandidates = _candidates.populate(fontName)
        if gotComposition:
            _composition.reposition(positionClip, minClip, maxClip)
        else:
            return
        compPosMins, compPosMaxs = _composition.clipBounds()
        candPosMins, candPosMaxs = _composition.candidateClipBounds()
        if gotReading:
            pos = (compPosMins[0] + 0.025, compPosMins[1] + (compPosMaxs[1] - compPosMins[1]) * 0.5)
            _reading.reposition(pos)
            readingMins, readingMaxs = _reading.clipBounds()
            candPosMins[1] = readingMins[1]
            candPosMaxs[1] = compPosMaxs[1]
        else:
            candPosMins[1] = compPosMins[1]
            candPosMaxs[1] = compPosMaxs[1]
        if gotCandidates:
            _candidates.reposition(candPosMins, candPosMaxs)
        return


def handleIMEEvent(event, positionClip, minClip, maxClip, fontName):
    if event.compositionChanged or event.compositionCursorPositionChanged or event.candidatesVisibilityChanged or event.candidatesChanged or event.selectedCandidateChanged or event.readingChanged:
        refresh(positionClip, minClip, maxClip, fontName)


def hideAll():
    _composition.hide()
    _candidates.hide()
    _reading.hide()
