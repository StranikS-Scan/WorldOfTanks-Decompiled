# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/ProgressBar.py
from PyGUI import PyGUIBase
import BigWorld
import GUI
import ResMgr
import FantasyDemo
import Bloom
from functools import partial

class IProgressBar(PyGUIBase):
    factoryString = 'PyGUI.IProgressBar'

    def __init__(self, component):
        PyGUIBase.__init__(self, component)

    def setMinMax(self, min, max):
        pass

    def setProgress(self, value):
        pass

    def reset(self, value):
        pass

    def addMessage(self, str):
        pass

    def appendMessage(self, str):
        pass


class ProgressBar(IProgressBar):
    factoryString = 'PyGUI.ProgressBar'

    def __init__(self, component):
        self.min = 0.0
        self.max = 1.0
        self.msgs = []
        IProgressBar.__init__(self, component)

    def setMinMax(self, min, max):
        self.min = min
        self.max = max

    def setProgress(self, value):
        range = self.max - self.min
        value = self.min + value * range
        try:
            self.component.bar.clipper.value = value
        except ReferenceError:
            pass

    def reset(self, value):
        self.component.bar.clipper.reset()

    def addMessage(self, str):
        FantasyDemo.rds.console.script.addMsg(str, 0)

    def appendMessage(self, str):
        FantasyDemo.rds.console.script.appendMsg(str, 0)

    def onLoad(self, section):
        PyGUIBase.onLoad(self, section)
        FantasyDemo.initConsole()

    def onBound(self):
        IProgressBar.onBound(self)


class ChunkLoadingProgressBar(ProgressBar):
    factoryString = 'PyGUI.ChunkLoadingProgressBar'

    def __init__(self, component):
        ProgressBar.__init__(self, component)
        self.phase1Ratio = 1.0
        self.checkRate = 0.05
        self.timeout = 180
        self.last = 0.0
        self.started = False
        self.inPhase1 = True
        self.cancelled = False

    def start(self, distance, callbackFn):
        if self.started:
            return
        self.started = True
        self.distance = distance
        self.last = 0.0
        self.callbackFn = callbackFn
        self.cancelled = False
        self.setProgress(0.0)
        self.component.bar.clipper.reset()
        self.progressCheck(BigWorld.time() + self.timeout)

    def finish(self, timedOut=False):
        self.started = False
        if self.callbackFn and not self.cancelled:
            if timedOut:
                self.callbackFn(True)
            else:
                BigWorld.callback(self.component.bar.clipper.speed, partial(self.callbackFn, timedOut))
            self.callbackFn = None
        return

    def cancel(self):
        self.cancelled = True
        self.started = False

    def progressCheck(self, endTime):
        timedOut = endTime < BigWorld.time()
        finished = timedOut
        if not finished:
            status = BigWorld.spaceLoadStatus(self.distance)
            finished = status > 0.95
        if finished:
            self.setProgress(1.0)
            self.finish(timedOut)
        else:
            if status > self.last:
                self.setProgress(status)
                self.last = status
            BigWorld.callback(self.checkRate, lambda : self.progressCheck(endTime))

    def onLoad(self, section):
        ProgressBar.onLoad(self, section)
        self.phase1Ratio = section.readFloat('phase1Ratio', self.phase1Ratio)
        self.checkRate = section.readFloat('checkRate', self.checkRate)
        self.timeout = section.readInt('timeout', self.timeout)
        if section.readBool('useDefaultLoadingScreen', True):
            self.replaceLoadingScreen(section)
        self.startPhase(1)
        self.active(True)

    def replaceLoadingScreen(self, section):
        sect = ResMgr.openSection('resources.xml/system')
        self.component.textureName = sect.readString('loadingScreen')

    def startPhase(self, num):
        if num == 1:
            self.setMinMax(0.0, self.phase1Ratio)
        else:
            self.setMinMax(self.phase1Ratio, 1.0)


class TeleportProgressBar(ChunkLoadingProgressBar):
    factoryString = 'PyGUI.TeleportProgressBar'

    def __init__(self, component):
        ChunkLoadingProgressBar.__init__(self, component)

    def replaceLoadingScreen(self, section):
        pass

    def preTeleport(self, callbackFn):
        import PostProcessing
        effect = PostProcessing.blur()
        effect.name = 'Teleport Progress Bar'
        effect.phases[-1].renderTarget = BigWorld.RenderTarget('teleportGobo', -3, -3)
        effect.phases[-1].material.additionalAlpha = 1.0
        c = list(PostProcessing.chain())
        c.append(effect)
        PostProcessing.chain(c)
        self.component.secondaryTexture = effect.phases[-1].renderTarget.texture
        self.component.freeze = None
        self.component.fader.value = 1.0
        BigWorld.callback(self.component.fader.speed, lambda : self.onBlurred(callbackFn))
        return

    def postTeleport(self):
        self.component.freeze = None
        return

    def onBlurred(self, callbackFn):
        import PostProcessing
        c = list(PostProcessing.chain())
        ch = []
        for e in c:
            if e.name != 'Teleport Progress Bar':
                ch.append(e)

        PostProcessing.chain(ch)
        if callbackFn:
            callbackFn()
