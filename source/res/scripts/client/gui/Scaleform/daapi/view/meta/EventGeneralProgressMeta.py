# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventGeneralProgressMeta.py
from gui.Scaleform.framework.entities.View import View

class EventGeneralProgressMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def changeGeneral(self, index):
        self._printOverrideError('changeGeneral')

    def specialOfferClick(self):
        self._printOverrideError('specialOfferClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_selectSectionS(self, sectionIdx):
        return self.flashObject.as_selectSection(sectionIdx) if self._isDAAPIInited() else None
