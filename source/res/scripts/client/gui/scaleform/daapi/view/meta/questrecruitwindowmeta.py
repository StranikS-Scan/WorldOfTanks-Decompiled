# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestRecruitWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class QuestRecruitWindowMeta(AbstractWindowView):

    def onApply(self, data):
        self._printOverrideError('onApply')

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)
