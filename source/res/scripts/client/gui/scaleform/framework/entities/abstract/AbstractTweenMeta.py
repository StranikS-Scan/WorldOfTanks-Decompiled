# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractTweenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class AbstractTweenMeta(BaseDAAPIModule):

    def initialiaze(self, props):
        self._printOverrideError('initialiaze')

    def creatTweenPY(self, tween):
        self._printOverrideError('creatTweenPY')

    def getPaused(self):
        self._printOverrideError('getPaused')

    def setPaused(self, paused):
        self._printOverrideError('setPaused')

    def getLoop(self):
        self._printOverrideError('getLoop')

    def setLoop(self, loop):
        self._printOverrideError('setLoop')

    def getDuration(self):
        self._printOverrideError('getDuration')

    def setDuration(self, duration):
        self._printOverrideError('setDuration')

    def getPosition(self):
        self._printOverrideError('getPosition')

    def setPosition(self, position):
        self._printOverrideError('setPosition')

    def getDelay(self):
        self._printOverrideError('getDelay')

    def setDelay(self, delay):
        self._printOverrideError('setDelay')

    def resetAnim(self):
        self._printOverrideError('resetAnim')

    def getTweenIdx(self):
        self._printOverrideError('getTweenIdx')

    def getIsComplete(self):
        self._printOverrideError('getIsComplete')

    def postponedCheckState(self):
        self._printOverrideError('postponedCheckState')

    def getTargetDisplayObjectS(self):
        return self.flashObject.getTargetDisplayObject() if self._isDAAPIInited() else None

    def onAnimCompleteS(self):
        return self.flashObject.onAnimComplete() if self._isDAAPIInited() else None

    def onAnimStartS(self):
        return self.flashObject.onAnimStart() if self._isDAAPIInited() else None
