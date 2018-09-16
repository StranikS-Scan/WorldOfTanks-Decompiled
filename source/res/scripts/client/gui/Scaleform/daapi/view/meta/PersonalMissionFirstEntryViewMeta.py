# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionFirstEntryViewMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionFirstEntryViewMeta(View):

    def playVideo(self):
        self._printOverrideError('playVideo')

    def backBtnClicked(self):
        self._printOverrideError('backBtnClicked')

    def onViewClose(self, isAcceptBtnClick):
        self._printOverrideError('onViewClose')

    def onCardClick(self, cardID):
        self._printOverrideError('onCardClick')

    def onNextCardClick(self, cardID):
        self._printOverrideError('onNextCardClick')

    def onPrevCardClick(self, cardID):
        self._printOverrideError('onPrevCardClick')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setDetailedCardDataS(self, data):
        return self.flashObject.as_setDetailedCardData(data) if self._isDAAPIInited() else None
