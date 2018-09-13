# Embedded file name: scripts/client/tutorial/gui/Scaleform/meta/TutorialBattleNoResultsMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TutorialBattleNoResultsMeta(DAAPIModule):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
