# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/UseAwardSheetWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class UseAwardSheetWindowMeta(AbstractWindowView):

    def accept(self):
        self._printOverrideError('accept')

    def cancel(self):
        self._printOverrideError('cancel')

    def as_setSettingsS(self, value):
        return self.flashObject.as_setSettings(value) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None
