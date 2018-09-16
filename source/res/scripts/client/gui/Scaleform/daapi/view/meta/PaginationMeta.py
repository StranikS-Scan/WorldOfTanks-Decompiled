# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PaginationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PaginationMeta(BaseDAAPIComponent):

    def showPage(self, dir):
        self._printOverrideError('showPage')

    def as_setPageS(self, value):
        return self.flashObject.as_setPage(value) if self._isDAAPIInited() else None

    def as_setEnabledS(self, leftEnabled, rightEnabled):
        return self.flashObject.as_setEnabled(leftEnabled, rightEnabled) if self._isDAAPIInited() else None
