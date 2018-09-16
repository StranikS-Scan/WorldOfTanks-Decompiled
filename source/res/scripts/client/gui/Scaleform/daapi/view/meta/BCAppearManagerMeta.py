# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCAppearManagerMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BCAppearManagerMeta(BaseDAAPIComponent):

    def onComponentTweenComplete(self, componentId):
        self._printOverrideError('onComponentTweenComplete')

    def onComponentPrepareAppear(self, componentId):
        self._printOverrideError('onComponentPrepareAppear')

    def as_showAnimatedS(self, data):
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None

    def as_setAppearConfigS(self, data):
        return self.flashObject.as_setAppearConfig(data) if self._isDAAPIInited() else None
