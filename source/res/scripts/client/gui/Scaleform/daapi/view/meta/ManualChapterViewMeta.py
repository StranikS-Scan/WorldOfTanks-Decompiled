# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ManualChapterViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ManualChapterViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def pageButtonClicked(self, pageType):
        self._printOverrideError('pageButtonClicked')

    def bootcampHighlighted(self):
        self._printOverrideError('bootcampHighlighted')

    def onPreviewClicked(self, videoUrl):
        self._printOverrideError('onPreviewClicked')

    def onPageChanged(self, id):
        self._printOverrideError('onPageChanged')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setPagesS(self, pages):
        return self.flashObject.as_setPages(pages) if self._isDAAPIInited() else None

    def as_showPageS(self, index):
        return self.flashObject.as_showPage(index) if self._isDAAPIInited() else None
