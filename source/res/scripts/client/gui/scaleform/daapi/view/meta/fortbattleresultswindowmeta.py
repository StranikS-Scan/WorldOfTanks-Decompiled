# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBattleResultsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortBattleResultsWindowMeta(AbstractWindowView):

    def getMoreInfo(self, battleID):
        self._printOverrideError('getMoreInfo')

    def getClanEmblem(self):
        self._printOverrideError('getClanEmblem')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_notAvailableInfoS(self, battleID):
        if self._isDAAPIInited():
            return self.flashObject.as_notAvailableInfo(battleID)

    def as_setClanEmblemS(self, iconTag):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(iconTag)
