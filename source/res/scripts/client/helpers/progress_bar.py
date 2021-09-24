# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/progress_bar.py
import functools
import GUI
from helpers.CallbackDelayer import CallbackDelayer

class ProgressBar(object):

    def __init__(self, colour='green', text='', direction='RIGHT', anchor='CENTER', height=20, width=0.5, position=None, textcolour=(0, 0, 0, 255), font='system_medium.font'):
        super(ProgressBar, self).__init__()
        self.__cd = CallbackDelayer()
        self.win = win = GUI.Window('helpers/maps/col_dark_gray.dds')
        self.bar = bar = GUI.Simple('helpers/maps/col_{}.dds'.format(colour))
        self.txt = txt = GUI.Text(text)
        self.shad = shad = GUI.ClipShader()
        txt.font = font
        txt.colour = textcolour
        win.heightMode = 'PIXEL' if isinstance(height, int) else 'CLIP'
        win.widthMode = 'PIXEL' if isinstance(width, int) else 'CLIP'
        win.height = height
        win.width = width
        bar.width = width
        bar.materialFX = 'BLEND'
        win.verticalAnchor = anchor
        win.position = position or (0, 0, 1)
        shad.mode = direction
        shad.speed = 1.0
        bar.addShader(shad)
        win.addChild(bar)
        win.addChild(txt)
        GUI.addRoot(win)

    def destroy(self):
        self.__cd.destroy()
        self.__cd = None
        GUI.delRoot(self.win)
        self.win = None
        self.bar = None
        self.txt = None
        self.shad = None
        return

    def startTextUpdate(self, callback, period):
        func = functools.partial(self.__tickFunc, callback, period)
        self.__cd.delayCallback(period, func)

    def setSpeed(self, speed):
        self.shad.speed = speed

    def setValue(self, value):
        self.shad.value = value

    def setText(self, text):
        self.txt.text = text

    def reset(self):
        self.shad.reset()

    def stopUpdate(self):
        self.__cd.clearCallbacks()

    def __tickFunc(self, callback, period):
        self.txt.text = callback()
        return period
