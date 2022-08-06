# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ManualMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ManualMainViewMeta(View):

    def onChapterOpenedS(self, id):
        self._printOverrideError('onChapterOpenedS')

    def closeView(self):
        self._printOverrideError('closeView')

    def onBackButton(self):
        self._printOverrideError('onBackButton')

    def as_setChaptersS(self, data):
        return self.flashObject.as_setChapters(data) if self._isDAAPIInited() else None

    def as_setPageBackgroundS(self, value):
        return self.flashObject.as_setPageBackground(value) if self._isDAAPIInited() else None

    def as_showCloseBtnS(self, value):
        return self.flashObject.as_showCloseBtn(value) if self._isDAAPIInited() else None

    def as_showBackBtnS(self, value):
        return self.flashObject.as_showBackBtn(value) if self._isDAAPIInited() else None
