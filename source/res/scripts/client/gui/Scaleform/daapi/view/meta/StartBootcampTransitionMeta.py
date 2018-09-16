# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StartBootcampTransitionMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StartBootcampTransitionMeta(BaseDAAPIComponent):

    def as_setTransitionTextS(self, text):
        return self.flashObject.as_setTransitionText(text) if self._isDAAPIInited() else None

    def as_updateStageS(self, width, height):
        return self.flashObject.as_updateStage(width, height) if self._isDAAPIInited() else None
