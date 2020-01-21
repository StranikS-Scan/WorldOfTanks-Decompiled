# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageViewMeta.py
from gui.Scaleform.framework.entities.View import View

class StorageViewMeta(View):

    def navigateToHangar(self):
        self._printOverrideError('navigateToHangar')

    def onClose(self):
        self._printOverrideError('onClose')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_selectSectionS(self, sectionIdx):
        return self.flashObject.as_selectSection(sectionIdx) if self._isDAAPIInited() else None

    def as_setButtonCounterS(self, sectionIdx, value):
        return self.flashObject.as_setButtonCounter(sectionIdx, value) if self._isDAAPIInited() else None
