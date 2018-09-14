# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileAchievementSectionMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileAchievementSectionMeta(DAAPIModule):

    def as_setRareAchievementDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setRareAchievementData(data)
