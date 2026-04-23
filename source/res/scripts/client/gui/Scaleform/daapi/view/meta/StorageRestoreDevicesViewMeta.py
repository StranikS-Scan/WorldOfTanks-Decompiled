# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageRestoreDevicesViewMeta.py
from gui.Scaleform.framework.entities.View import View

class StorageRestoreDevicesViewMeta(View):

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
