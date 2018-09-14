# Embedded file name: scripts/client/tutorial/gui/Scaleform/meta/TutorialBattleNoResultsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class TutorialBattleNoResultsMeta(AbstractWindowView):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
