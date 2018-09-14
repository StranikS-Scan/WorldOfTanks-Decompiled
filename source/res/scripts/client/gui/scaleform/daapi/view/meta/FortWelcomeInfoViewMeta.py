# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortWelcomeInfoViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortWelcomeInfoViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onCreateBtnClick(self):
        """
        :return :
        """
        self._printOverrideError('onCreateBtnClick')

    def onNavigate(self, code):
        """
        :param code:
        :return :
        """
        self._printOverrideError('onNavigate')

    def openClanResearch(self):
        """
        :return :
        """
        self._printOverrideError('openClanResearch')

    def as_setWarningTextS(self, text, disabledBtnTooltip):
        """
        :param text:
        :param disabledBtnTooltip:
        :return :
        """
        return self.flashObject.as_setWarningText(text, disabledBtnTooltip) if self._isDAAPIInited() else None

    def as_setCommonDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRequirementTextS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_setRequirementText(text) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        """
        :param description:
        :param hyperlink:
        :return :
        """
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
