# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortWelcomeInfoViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortWelcomeInfoViewMeta(BaseDAAPIComponent):

    def onCreateBtnClick(self):
        self._printOverrideError('onCreateBtnClick')

    def onNavigate(self, code):
        self._printOverrideError('onNavigate')

    def openClanResearch(self):
        self._printOverrideError('openClanResearch')

    def as_setWarningTextS(self, text, disabledBtnTooltip):
        return self.flashObject.as_setWarningText(text, disabledBtnTooltip) if self._isDAAPIInited() else None

    def as_setCommonDataS(self, data):
        """
        :param data: Represented by FortWelcomeViewVO (AS)
        """
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRequirementTextS(self, text):
        return self.flashObject.as_setRequirementText(text) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
