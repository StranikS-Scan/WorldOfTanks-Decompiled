# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBattleResultsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortBattleResultsWindowMeta(AbstractWindowView):

    def getMoreInfo(self, battleID):
        self._printOverrideError('getMoreInfo')

    def getClanEmblem(self):
        self._printOverrideError('getClanEmblem')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_notAvailableInfoS(self, battleID):
        return self.flashObject.as_notAvailableInfo(battleID) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, iconTag):
        return self.flashObject.as_setClanEmblem(iconTag) if self._isDAAPIInited() else None
