# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesSeasonCompleteViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesSeasonCompleteViewMeta(WrapperViewMeta):

    def showRating(self):
        self._printOverrideError('showRating')

    def closeView(self):
        self._printOverrideError('closeView')

    def onSoundTrigger(self, soundName):
        self._printOverrideError('onSoundTrigger')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setPlaceS(self, value):
        return self.flashObject.as_setPlace(value) if self._isDAAPIInited() else None

    def as_setAwardsDataS(self, awardsData):
        return self.flashObject.as_setAwardsData(awardsData) if self._isDAAPIInited() else None
