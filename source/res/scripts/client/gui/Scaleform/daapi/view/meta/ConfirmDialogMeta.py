# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ConfirmDialogMeta(AbstractWindowView):

    def submit(self, selected):
        self._printOverrideError('submit')

    def as_setSettingsS(self, data):
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None
