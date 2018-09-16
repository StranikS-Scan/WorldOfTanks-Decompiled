# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LinkedSetHintsViewMeta.py
from gui.Scaleform.framework.entities.View import View

class LinkedSetHintsViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
