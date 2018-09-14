# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleResultsMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleResultsMeta(DAAPIModule):

    def saveSorting(self, iconType, sortDirection, bonusType):
        self._printOverrideError('saveSorting')

    def showEventsWindow(self, questID, eventType):
        self._printOverrideError('showEventsWindow')

    def getClanEmblem(self, uid, clanID):
        self._printOverrideError('getClanEmblem')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setClanEmblemS(self, uid, iconTag):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(uid, iconTag)
