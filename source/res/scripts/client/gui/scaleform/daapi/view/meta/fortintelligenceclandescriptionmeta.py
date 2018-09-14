# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceClanDescriptionMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortIntelligenceClanDescriptionMeta(BaseDAAPIComponent):

    def onOpenCalendar(self):
        self._printOverrideError('onOpenCalendar')

    def onOpenClanList(self):
        self._printOverrideError('onOpenClanList')

    def onOpenClanStatistics(self):
        self._printOverrideError('onOpenClanStatistics')

    def onOpenClanCard(self):
        self._printOverrideError('onOpenClanCard')

    def onAddRemoveFavorite(self, isAdd):
        self._printOverrideError('onAddRemoveFavorite')

    def onAttackDirection(self, uid):
        self._printOverrideError('onAttackDirection')

    def onHoverDirection(self):
        self._printOverrideError('onHoverDirection')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_updateBookMarkS(self, isAdd):
        if self._isDAAPIInited():
            return self.flashObject.as_updateBookMark(isAdd)
