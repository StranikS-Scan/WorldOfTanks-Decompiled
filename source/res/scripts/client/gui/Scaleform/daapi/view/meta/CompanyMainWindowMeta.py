# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyMainWindowMeta.py
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyWindow import AbstractRallyWindow

class CompanyMainWindowMeta(AbstractRallyWindow):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractRallyWindow
    null
    """

    def getCompanyName(self):
        """
        :return String:
        """
        self._printOverrideError('getCompanyName')

    def showFAQWindow(self):
        """
        :return :
        """
        self._printOverrideError('showFAQWindow')

    def getClientID(self):
        """
        :return Number:
        """
        self._printOverrideError('getClientID')

    def as_setWindowTitleS(self, title, icon):
        """
        :param title:
        :param icon:
        :return :
        """
        return self.flashObject.as_setWindowTitle(title, icon) if self._isDAAPIInited() else None
