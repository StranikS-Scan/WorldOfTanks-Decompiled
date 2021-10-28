# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HWIngameHelpWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class HWIngameHelpWindowMeta(AbstractWindowView):

    def clickSettingWindow(self):
        self._printOverrideError('clickSettingWindow')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setPaginatorDataS(self, pages):
        return self.flashObject.as_setPaginatorData(pages) if self._isDAAPIInited() else None
