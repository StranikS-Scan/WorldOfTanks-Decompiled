# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ManualChapterViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ManualChapterViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def bootcampButtonClicked(self):
        self._printOverrideError('bootcampButtonClicked')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_showPageS(self, index):
        return self.flashObject.as_showPage(index) if self._isDAAPIInited() else None
