# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortWelcomeInfoViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortWelcomeInfoViewMeta(BaseDAAPIComponent):

    def onCreateBtnClick(self):
        self._printOverrideError('onCreateBtnClick')

    def onNavigate(self, code):
        self._printOverrideError('onNavigate')

    def as_setWarningTextS(self, text, disabledBtnTooltipHeader, disabledBtnTooltipBody):
        if self._isDAAPIInited():
            return self.flashObject.as_setWarningText(text, disabledBtnTooltipHeader, disabledBtnTooltipBody)

    def as_setHyperLinksS(self, searchClanLink, createClanLink, detailLink):
        if self._isDAAPIInited():
            return self.flashObject.as_setHyperLinks(searchClanLink, createClanLink, detailLink)

    def as_setCommonDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCommonData(data)

    def as_setRequirementTextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setRequirementText(text)

    def as_showMiniClientInfoS(self, description, hyperlink):
        if self._isDAAPIInited():
            return self.flashObject.as_showMiniClientInfo(description, hyperlink)
