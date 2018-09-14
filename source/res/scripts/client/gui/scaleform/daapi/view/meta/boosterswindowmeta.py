# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BoostersWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BoostersWindowMeta(AbstractWindowView):

    def requestBoostersArray(self, isAvailable):
        self._printOverrideError('requestBoostersArray')

    def onBoosterActionBtnClick(self, boosterID, questID):
        self._printOverrideError('onBoosterActionBtnClick')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setStaticDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setStaticData(data)

    def as_setListDataS(self, boosters, scrollToTop):
        if self._isDAAPIInited():
            return self.flashObject.as_setListData(boosters, scrollToTop)
