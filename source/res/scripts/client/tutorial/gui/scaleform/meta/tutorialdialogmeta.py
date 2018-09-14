# Embedded file name: scripts/client/tutorial/gui/Scaleform/meta/TutorialDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class TutorialDialogMeta(AbstractWindowView):

    def submit(self):
        self._printOverrideError('submit')

    def cancel(self):
        self._printOverrideError('cancel')

    def as_setContentS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setContent(data)

    def as_updateContentS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateContent(data)
