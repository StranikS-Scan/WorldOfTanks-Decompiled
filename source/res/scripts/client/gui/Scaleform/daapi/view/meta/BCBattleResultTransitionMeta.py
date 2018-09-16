# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCBattleResultTransitionMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BCBattleResultTransitionMeta(BaseDAAPIComponent):

    def as_msgTypeHandlerS(self, status):
        return self.flashObject.as_msgTypeHandler(status) if self._isDAAPIInited() else None

    def as_updateStageS(self, width, height):
        return self.flashObject.as_updateStage(width, height) if self._isDAAPIInited() else None
