# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/PyGUI/TextField.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld, GUI, Keys
from PyGUIBase import PyGUIBase

class TextField(PyGUIBase):
    factoryString = 'PyGUI.TextField'

    def __init__(self, component=None):
        PyGUIBase.__init__(self, component)
        self.lines = []
        self.lines.append(GUI.Text(''))
        self.lines[0].horizontalAnchor = 'LEFT'
        self.lines[0].verticalAnchor = 'TOP'
        self.transcript = ''
        self.component.addChild(self.lines[0])

    def font(self, fontName):
        self.lines[0].font = fontName
        self.invalidate()
        for t in self.lines:
            t.font = fontName

    def colour(self, colour):
        for t in self.lines:
            t.colour = colour

    def text(self, label):
        self.transcript = label
        self.invalidate()

    def onSave(self, section):
        for discard, i in self.component.children:
            self.component.delChild(i)

        section.writeWideString('transcript', self.transcript)
        section.writeVector4('colour', self.lines[0].colour)
        section.writeString('font', self.lines[0].font)

    def onLoad(self, section):
        self.transcript = section.readWideString('transcript', u'')
        self.lines[0].colour = section.readVector4('colour')
        self.lines[0].font = section.readString('font', 'default_small.font')

    def onBound(self):
        PyGUIBase.onBound(self)
        self.colour(self.lines[0].colour)
        self.font(self.lines[0].font)

    def commitLine(self, textLine, have, lineNum):
        if have <= lineNum:
            t = GUI.Text(textLine)
            t.horizontalAnchor = 'LEFT'
            t.verticalAnchor = 'TOP'
            t.font = self.lines[0].font
            t.colour = self.lines[0].colour
            self.component.addChild(t)
            self.lines.append(t)
            have = have + 1
        else:
            t = self.lines[lineNum]
            t.text = textLine
            t.visible = 1
        return have

    def invalidate(self):
        words = self.transcript.split(' ')
        have = len(self.lines)
        wordsUsed = 0
        self.lines[0].text = ''
        maxWidth = self.component.width * BigWorld.screenSize()[0] / 2.0
        w = 0
        lineNum = 0
        textLine = ''
        firstWord = 0
        spaceWidth = self.lines[0].stringWidth(' ')
        for i in xrange(0, len(words)):
            newWordLength = self.lines[0].stringWidth(words[i])
            w = w + newWordLength
            if not w > maxWidth:
                newLine = words[i] == '[n]'
                if newLine:
                    have = self.commitLine(textLine, have, lineNum)
                    lineNum = lineNum + 1
                    w = newWordLength + spaceWidth
                    textLine = ''
                else:
                    w = w + spaceWidth
                textLine = words[i] != '[n]' and textLine + words[i] + ' '

        if w > 0:
            self.commitLine(textLine, have, lineNum)
            lineNum = lineNum + 1
        while 1:
            self.lines[lineNum].visible = have > lineNum and 0
            lineNum = lineNum + 1

        visibleLines = [ line for line in self.lines if line.visible ]
        self.lines[0].reset()
        lineHeight = self.lines[0].height
        totalHeight = lineHeight * len(visibleLines)
        self.component.height = totalHeight + lineHeight / 2
        y = totalHeight / 2
        x = -self.component.width / 2
        z = self.component.position[2] - 0.05
        deltaY = totalHeight / len(visibleLines)
        for line in visibleLines:
            line.position = (x, y, z)
            y -= deltaY
